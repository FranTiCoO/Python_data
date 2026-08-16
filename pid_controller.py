import time
import threading

from simple_pid import PID
import config
from control_io import ControlIO
from logger_setup import logger
from server import update_config_file


class PIDController:

    def __init__(self, control=None, pid_factory=PID, clock=time.monotonic):
        self.control = control or ControlIO()
        self.pid = pid_factory(config.KP, config.KI, config.KD, config.SET_POINT)
        self.pid.output_limits = (0, 100)
        self.clock = clock
        self._lock = threading.RLock()
        self.self_optimizing = False
        self._autotune_extrema = []
        self._autotune_current_extremum = None
        self._autotune_last_direction = None
        self._autotune_completed = threading.Event()
        self._autotune_result = {"state": "idle"}
        self._autotune_completed.set()

        if getattr(config, "PID_SELF_OPTIMIZATION", False):
            self.start_self_optimization()

    def start_self_optimization(self):
        """Start relay-feedback tuning and apply the resulting gains automatically."""
        with self._lock:
            low = config.PID_AUTOTUNE_OUTPUT_LOW
            high = config.PID_AUTOTUNE_OUTPUT_HIGH
            if not 0 <= low < high <= 100:
                raise ValueError("PID autotune output limits must satisfy 0 <= low < high <= 100")
            if config.PID_AUTOTUNE_CYCLES < 3:
                raise ValueError("PID autotune requires at least three cycles")

            self.self_optimizing = True
            self._autotune_extrema = []
            self._autotune_current_extremum = None
            self._autotune_last_direction = None
            self._autotune_completed.clear()
            self._autotune_result = {"state": "running"}
            self.pid.set_auto_mode(False)
            logger.info("PID self-optimization started")

    def stop_self_optimization(self):
        with self._lock:
            self.self_optimizing = False
            self.pid.set_auto_mode(True, last_output=0)

    def cancel_self_optimization(self):
        with self._lock:
            if not self.self_optimizing:
                return False

            self.stop_self_optimization()
            self._finish_self_optimization("cancelled")
            logger.info("PID self-optimization cancelled")
            return True

    def wait_for_self_optimization(self, timeout=None):
        if not self._autotune_completed.wait(timeout):
            return {"state": "running"}
        with self._lock:
            return dict(self._autotune_result)

    def generate_pwm_output(self, temperature):
        with self._lock:
            if self.self_optimizing:
                pwm_value = self._generate_autotune_output(temperature)
            else:
                pwm_value = self.pid(temperature)

            self.control.output_pwm(pwm_value)
            logger.debug(f"PID output: {pwm_value:.2f} for temperature: {temperature:.2f}")
            return pwm_value

    def _generate_autotune_output(self, temperature):
        direction = 1 if temperature <= self.pid.setpoint else -1
        if self._autotune_last_direction is None:
            self._autotune_last_direction = direction
            self._autotune_current_extremum = temperature
        elif direction == self._autotune_last_direction:
            if direction > 0:
                self._autotune_current_extremum = max(self._autotune_current_extremum, temperature)
            else:
                self._autotune_current_extremum = min(self._autotune_current_extremum, temperature)
        else:
            self._autotune_extrema.append((self.clock(), self._autotune_current_extremum))
            self._autotune_last_direction = direction
            self._autotune_current_extremum = temperature
            if len(self._autotune_extrema) >= config.PID_AUTOTUNE_CYCLES * 2:
                self._apply_autotune_gains()
                return self.pid(temperature)

        return (
            config.PID_AUTOTUNE_OUTPUT_HIGH
            if direction > 0
            else config.PID_AUTOTUNE_OUTPUT_LOW
        )

    def _apply_autotune_gains(self):
        amplitudes = [
            abs(self._autotune_extrema[index][1] - self._autotune_extrema[index - 1][1]) / 2
            for index in range(1, len(self._autotune_extrema))
        ]
        periods = [
            self._autotune_extrema[index][0] - self._autotune_extrema[index - 2][0]
            for index in range(2, len(self._autotune_extrema))
        ]
        amplitude = sum(amplitudes) / len(amplitudes)
        period = sum(periods) / len(periods)
        relay_amplitude = (config.PID_AUTOTUNE_OUTPUT_HIGH - config.PID_AUTOTUNE_OUTPUT_LOW) / 2

        if amplitude <= 0 or period <= 0:
            logger.warning("PID self-optimization failed: insufficient temperature oscillation")
            self.stop_self_optimization()
            self._finish_self_optimization("failed")
            return

        ultimate_gain = 4 * relay_amplitude / (3.141592653589793 * amplitude)
        config.KP = 0.6 * ultimate_gain
        config.KI = 1.2 * ultimate_gain / period
        config.KD = 0.075 * ultimate_gain * period
        self.pid.tunings = (config.KP, config.KI, config.KD)
        try:
            update_config_file(
                {"KP": config.KP, "KI": config.KI, "KD": config.KD},
                config_path=config.__file__,
            )
        except OSError:
            logger.exception("PID self-optimization completed but could not save gains")
        self.stop_self_optimization()
        self._finish_self_optimization(
            "completed",
            {"KP": config.KP, "KI": config.KI, "KD": config.KD},
        )
        logger.info(
            "PID self-optimization completed: Kp=%.4f, Ki=%.4f, Kd=%.4f",
            config.KP,
            config.KI,
            config.KD,
        )

    def _finish_self_optimization(self, state, result=None):
        with self._lock:
            self._autotune_result = {"state": state, **(result or {})}
            self._autotune_completed.set()
        
        

