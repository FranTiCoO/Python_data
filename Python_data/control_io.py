import config
import RPi.GPIO as gpio
import time
from datetime import datetime, timedelta
import logging

from main import logger

class ControlIO:

    def __init__(self):
        #define pins
        self.pin_light_toggle = config.PIN_LIGHT_TOGGLE
        self.pin_light_mode = config.PIN_LIGHT_MODE
        self.pin_pump_toggle = config.PIN_PUMP_TOGGLE
        
        #get PWM pin
        self.pin_temperature_pwm = config.PIN_TEMPERATURE_PWM

        #define pins as outputs
        gpio.setup(self.pin_pump_toggle, gpio.OUT)
        gpio.setup(self.pin_light_toggle, gpio.OUT)
        gpio.setup(self.pin_light_mode, gpio.OUT)

        self.light_toggle()
        
        #setting PWM pin to output
        gpio.setup(self.pin_temperature_pwm, gpio.OUT)
           
    #Pump ON/OFF
    def pump_toggle(self):

        
        if config.PUMP_TIMER_ON == 1:
            final_power_state = gpio.HIGH
            for start_time in config.TIMES_PUMP_ON:
                current_time = datetime.now().time()
                
                #converting string to time
                start_time = datetime.strptime(start_time, '%H:%M:%S')
                end_time = start_time + timedelta(seconds=config.DURATION_PUMP_ON)
                
                #extract only the time
                start_time = start_time.time()
                end_time = end_time.time()
                
                if start_time <= current_time <= end_time:
                    final_power_state = gpio.LOW
                    #logger.debug("Pump ON")
            
            if final_power_state == 0:
                logger.debug("Pumpe EIN")
            else:
                logger.debug("Pumpe AUS")
        else:
            final_power_state = config.PUMP_ON

        gpio.output(self.pin_pump_toggle, final_power_state)
        #logging.info(f"Pump state: {final_power_state}")

    #Switch between night and day light
    def light_mode(self):
        current_time = datetime.now().time()
        day_time = datetime.strptime(config.TIMES_LIGHT_MODE["day"], '%H:%M:%S').time()
        night_time = datetime.strptime(config.TIMES_LIGHT_MODE["night"], '%H:%M:%S').time()
        
        if day_time <= current_time <= night_time:
            gpio.output(self.pin_light_mode, gpio.LOW)
            #logger.debug("Day Time")
            
        else:
            gpio.output(self.pin_light_mode, gpio.HIGH)
            #logger.debug("Night Time")
    
    #light ON/OFF
    def light_toggle(self):
        state = config.STATE_LIGHT
        if isinstance(state, str):
            state = getattr(gpio, state)
        #logger.info(f"Light state: {state}")
        gpio.output(self.pin_light_toggle, state)

    #set PWM signal OUT
    def output_pwm(self, pwm_value):
        #innitializing PWM
        pwm = gpio.PWM(self.pin_temperature_pwm, config.PWM_FREQUENCY)
        pwm.start(0)        
        pwm.ChangeDutyCycle(pwm_value)
        logger.debug(f'PWM Value: {pwm_value}%')

