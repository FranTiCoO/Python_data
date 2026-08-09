from datetime import datetime, timedelta

import config
import RPi.GPIO as gpio

from logger_setup import logger


class ControlIO:

    def __init__(self, gpio_module=None, logger_instance=None):
        self.gpio = gpio_module or gpio
        self.logger = logger_instance or logger

        # define pins
        self.pin_light_toggle = config.PIN_LIGHT_TOGGLE
        self.pin_light_mode = config.PIN_LIGHT_MODE
        self.pin_pump_toggle = config.PIN_PUMP_TOGGLE

        # get PWM pin
        self.pin_temperature_pwm = config.PIN_TEMPERATURE_PWM

        # define pins as outputs
        self.gpio.setup(self.pin_pump_toggle, self.gpio.OUT)
        self.gpio.setup(self.pin_light_toggle, self.gpio.OUT)
        self.gpio.setup(self.pin_light_mode, self.gpio.OUT)

        self.light_toggle()

        # setting PWM pin to output
        self.gpio.setup(self.pin_temperature_pwm, self.gpio.OUT)

        self._pwm = None

    # Pump ON/OFF
    def pump_toggle(self):
        if config.PUMP_TIMER_ON == 1:
            final_power_state = self.gpio.HIGH
            for start_time in config.TIMES_PUMP_ON:
                current_time = datetime.now().time()

                # converting string to time
                start_time = datetime.strptime(start_time, '%H:%M:%S')
                end_time = start_time + timedelta(seconds=config.DURATION_PUMP_ON)

                # extract only the time
                start_time = start_time.time()
                end_time = end_time.time()

                if start_time <= current_time <= end_time:
                    final_power_state = self.gpio.LOW

            if final_power_state == 0:
                self.logger.debug("Pumpe EIN")
            else:
                self.logger.debug("Pumpe AUS")
        else:
            final_power_state = config.PUMP_ON

        self.gpio.output(self.pin_pump_toggle, final_power_state)

    # Switch between night and day light
    def light_mode(self):
        current_time = datetime.now().time()
        day_time = datetime.strptime(config.TIMES_LIGHT_MODE["day"], '%H:%M:%S').time()
        night_time = datetime.strptime(config.TIMES_LIGHT_MODE["night"], '%H:%M:%S').time()

        if day_time <= current_time <= night_time:
            self.gpio.output(self.pin_light_mode, self.gpio.LOW)
        else:
            self.gpio.output(self.pin_light_mode, self.gpio.HIGH)

    # light ON/OFF
    def light_toggle(self):
        state = config.STATE_LIGHT
        if isinstance(state, str):
            state = getattr(self.gpio, state)
        self.gpio.output(self.pin_light_toggle, state)

    # set PWM signal OUT
    def output_pwm(self, pwm_value):
        if self._pwm is None:
            self._pwm = self.gpio.PWM(self.pin_temperature_pwm, config.PWM_FREQUENCY)
            self._pwm.start(0)

        self._pwm.ChangeDutyCycle(pwm_value)
        self.logger.debug(f'PWM Value: {pwm_value}%')

    def cleanup(self):
        try:
            if self._pwm is not None:
                self._pwm.stop()
                self._pwm = None
        except Exception as exc:
            self.logger.debug(f"PWM cleanup failed: {exc}")

        try:
            self.gpio.output(self.pin_pump_toggle, self.gpio.LOW)
            self.gpio.output(self.pin_light_toggle, self.gpio.LOW)
            self.gpio.output(self.pin_light_mode, self.gpio.LOW)
        except Exception as exc:
            self.logger.debug(f"GPIO output cleanup failed: {exc}")

        try:
            self.gpio.cleanup()
        except Exception as exc:
            self.logger.debug(f"GPIO cleanup failed: {exc}")

