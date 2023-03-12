from simple_pid import PID
from config import *
from control_io import *
from writeDB import *
from main import logger

class PIDController:

    def __init__(self):
        #generate variables for PID controller
        self.set_point = SET_POINT
        self.Kp = KP
        self.Ki = KI
        self.Kd = KD
        self.control = ControlIO()

    def generate_pwm_output(self, temperature):
        #innitiate PID controler
        pid = PID(self.Kp, self.Ki, self.Kd, self.set_point)
        
        #keep the pwm_value between 0 and 100
        pid.output_limits = (0, 100)
        
        # Update PID controller with new temperature
        pwm_value = pid(temperature)

        # Write control output to pwm output

        self.control.output_pwm(pwm_value)
        
        

