from config import *
import RPi.GPIO as gpio
import time
from datetime import datetime, timedelta

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
        
        #innitializing PWM
        self.pwm = gpio.PWM(self.pin_temperature_pwm, self.pwm_frequency)
        self.pwm.start(0)  

    
    #Pump ON/OFF
    def pump_toggle(self):

        for pump_time in self.times_pump_on:
            current_time = datetime.now().time()
            #converting string to time
            pump_time = datetime.strptime(pump_time, '%H:%M:%S')
            
            #set range for pump on
            min_time = pump_time - timedelta(seconds=self.time_pump_offset)
            max_time = pump_time + timedelta(seconds=self.time_pump_offset)
            #extract only the time
            min_time = min_time.time()
            max_time = max_time.time()
            #print(current_time)
            #print(min_time, max_time, self.current_time)

            if min_time <= current_time <= max_time:
                gpio.output(self.pin_pump_toggle, gpio.HIGH)
                #print("Pump ON")
                time.sleep(self.duration_pump_on)
            else: 
                gpio.output(self.pin_pump_toggle, gpio.LOW)
                #print("Pump OFF")

    #Switch between night and day light
    def light_mode(self):
        current_time = datetime.now().time()
        
        if self.day_time <= current_time <= self.night_time:
            gpio.output(self.pin_light_mode, gpio.LOW)
            #print("Day Time")
        else:
            gpio.output(self.pin_light_mode, gpio.HIGH)
            #print("Night Time")
    
    #light ON/OFF
    def light_toggle(self, state):
        state = getattr(gpio, state)
        gpio.output(self.pin_light_toggle, state)

    #set PWM signal OUT
    def output_pwm(self, pwm_value):
        
        self.pwm.ChangeDutyCycle(pwm_value)
        print(f'PWM Value: {pwm_value}%')
        #print(f'PWM Output: {gpio.input(self.pin_temperature_pwm)}')

