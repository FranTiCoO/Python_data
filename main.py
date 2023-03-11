from DHT22 import *
from config import *
from TSL2561 import *
from control_io import *
import concurrent.futures
import time


class Main:
    
    def __init__(self):
        self.wait_sensor_read = SENSOR_WAIT
        self.control_io = ControlIO()
        self.dht22 = DHT22()
        self.tsl2561 = TSL2561()

    def sensor_loop(self):  
        while True:
            self.dht22.get_temp_hum()
            self.tsl2561.get_lum()
            time.sleep(self.wait_sensor_read)

    def pump_loop(self):
        while True:
            self.control_io.pump_toggle()

    def loop_no_delay(self):
        while True:
            self.control_io.light_mode()
            pass

    def main(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # submit the functions to the thread pool
            sensor_loop = executor.submit(self.sensor_loop)
            pump_loop = executor.submit(self.pump_loop)
            loop_no_delay = executor.submit(self.loop_no_delay)
            
            try:
                for loop in concurrent.futures.as_completed([sensor_loop, pump_loop, loop_no_delay]):
                    loop.result()
            except KeyboardInterrupt:
                # cancel all the futures if a keyboard interrupt is received
                for loop in [sensor_loop, pump_loop, loop_no_delay]:
                    loop.cancel()

main = Main()
main.main()

