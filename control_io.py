from config import *
import RPi.GPIO as gpio
import time
from datetime import datetime, timedelta

from main import logger

class ControlIO:

    def __init__(self):
        #define pins
        self.pin_light_toggle = PIN_LIGHT_TOGGLE
        self.pin_light_mode = PIN_LIGHT_MODE
        self.pin_pump_toggle = PIN_PUMP_TOGGLE
        
        #get PWM pin
        self.pin_temperature_pwm = PIN_TEMPERATURE_PWM
        
        #get PWM frequency
        self.pwm_frequency = PWM_FREQUENCY
        
        #define times
        self.times_pump_on = TIMES_PUMP_ON
        self.duration_pump_on = DURATION_PUMP_ON
        self.times_light_mode = TIMES_LIGHT_MODE

        self.time_pump_offset = TIME_PUMP_OFFSET

        self.night_time = self.times_light_mode["night"]
        self.night_time = datetime.strptime(self.night_time, '%H:%M:%S').time()

        self.day_time = self.times_light_mode["day"]
        self.day_time = datetime.strptime(self.day_time, '%H:%M:%S').time()

        #define pins as outputs
        gpio.setup(self.pin_pump_toggle, gpio.OUT)
        gpio.setup(self.pin_light_toggle, gpio.OUT)
        gpio.setup(self.pin_light_mode, gpio.OUT)
        
        #setting PWM pin to output
        gpio.setup(self.pin_temperature_pwm, gpio.OUT)
        


    
    #Pump ON/OFF
    def pump_toggle(self):
        final_power_state = gpio.LOW
        
        for start_time in self.times_pump_on:
            current_time = datetime.now().time()
            
            #converting string to time
            start_time = datetime.strptime(start_time, '%H:%M:%S')
            end_time = start_time + timedelta(seconds=self.duration_pump_on)
            
            #extract only the time
            start_time = start_time.time()
            end_time = end_time.time()
            
            if start_time <= current_time <= end_time:
                final_power_state = gpio.HIGH
                #logger.debug("Pump ON")
        logger.debug(final_power_state)
        gpio.output(self.pin_pump_toggle, final_power_state)

            

    #Switch between night and day light
    def light_mode(self):
        current_time = datetime.now().time()
        
        if self.day_time <= current_time <= self.night_time:
            gpio.output(self.pin_light_mode, gpio.LOW)
            #logger.debug("Day Time")
            
        else:
            gpio.output(self.pin_light_mode, gpio.HIGH)
            #logger.debug("Night Time")
    
    #light ON/OFF
    def light_toggle(self, state):
        state = getattr(gpio, state)
        gpio.output(self.pin_light_toggle, state)

    #set PWM signal OUT
    def output_pwm(self, pwm_value):
        #innitializing PWM
        pwm = gpio.PWM(self.pin_temperature_pwm, self.pwm_frequency)
        pwm.start(0)        
        pwm.ChangeDutyCycle(pwm_value)
        logger.debug(f'PWM Value: {pwm_value}%')

