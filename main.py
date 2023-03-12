from DHT22 import *
from config import *
from TSL2561 import *
from control_io import *
#import concurrent.futures
import time


class Main:
    
    def __init__(self):
        self.tick_time = TICK_TIME
        self.sensor_wait = SENSOR_WAIT
        self.duration_pump_on = DURATION_PUMP_ON
        self.tick = 0
        self.control_io = ControlIO()
        self.dht22 = DHT22()
        self.tsl2561 = TSL2561()
        self.pump_status = False
        self.pump_tick = 0

#    def sensor_loop(self):  
#        while True:
#            self.dht22.get_temp_hum()
#            self.tsl2561.get_lum()
#            time.sleep(self.wait_sensor_read)

#    def pump_loop(self):
#        while True:
#            self.control_io.pump_toggle()

#    def loop_no_delay(self):
#        while True:
#            self.control_io.light_mode()
#            pass    
    
    def main(self):
        while True:
            time.sleep(self.tick_time)
            #1 tick is 0.1 seconds
            self.tick += 1
            
            if self.tick == 101:
                self.tick = 0

            if self.tick == self.sensor_wait * 10:
                self.dht22.get_temp_hum()
                self.tsl2561.get_lum()
            
            if self.pump_status == False or self.pump_tick * 10 == self.duration_pump_on:
                self.pump_status = self.control_io.pump_toggle()
                if self.pump_status == True:
                    print(self.pump_status)
                self.pump_tick = 0
            else: 
                self.pump_tick += 1
            
            self.control_io.light_mode()

main = Main()
main.main()

