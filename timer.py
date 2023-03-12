import time

import control_io
import dht22
import tsl2561

from main import logger

class TimerTemplate:

    def __init__(self, trigger_time):
        self.trigger_time = trigger_time
        self.counter = 0
        logger.debug("Creating a timer")

    def tick(self):
        self.counter += 1

    def check(self):

        if self.counter == self.trigger_time:
            self.action()
            self.counter = 0

    def action(self):
        pass
    
    def update_timer(self):
        pass

class TimerPump(TimerTemplate):

    def __init__(self, trigger_time):
        super().__init__(trigger_time)
        self.control_io = control_io.ControlIO()
    
    def action(self):
        self.control_io.pump_toggle()

class TimerSensor(TimerTemplate):

    def __init__(self, trigger_time):
        super().__init__(trigger_time)
        self.dht22 = dht22.DHT22()
        self.tsl2561 = tsl2561.TSL2561()
    
    def action(self):
        self.dht22.get_temp_hum()
        self.tsl2561.get_lum()

class TimerLightMode(TimerTemplate):

    def __init__(self, trigger_time):
        super().__init__(trigger_time)
        self.control_io = control_io.ControlIO()
    
    def action(self):
        self.control_io.light_mode()


class TimerLightToggle(TimerTemplate):

    def __init__(self, trigger_time):
        super().__init__(trigger_time)
        self.control_io = control_io.ControlIO()
    
    def action(self):
        self.control_io.light_toggle()

