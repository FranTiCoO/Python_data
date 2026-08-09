from simple_pid import PID
import config
from control_io import ControlIO
from logger_setup import logger
from writeDB import InfluxDBWriter


class PIDController:

    def __init__(self):
        self.control = ControlIO()

    def generate_pwm_output(self, temperature):
        #innitiate PID controler
        pid = PID(config.KP, config.KI, config.KD, config.SET_POINT)
        
        #keep the pwm_value between 0 and 100
        pid.output_limits = (0, 100)
        
        # Update PID controller with new temperature
        pwm_value = pid(temperature)

        # Write control output to pwm output

        self.control.output_pwm(pwm_value)
        logger.debug(f"PID output: {pwm_value:.2f} for temperature: {temperature:.2f}")
        
        

