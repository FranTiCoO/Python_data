import logging
import time

import config
import timer

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)d]     %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.DEBUG)

if __name__ == '__main__':
    
    timer_sensor = timer.TimerSensor(config.SENSOR_WAIT * 10)
    timer_pump = timer.TimerPump(1 * 10)
    timer_light_mode = timer.TimerLightMode(10 * 10)

    t_list = [timer_sensor, timer_pump, timer_light_mode]
    #logger.debug("Oh god i'm debugging")
    #logger.info("Hello Ertl this is a info message")
    #logger.warning("I'm a warning")
    #logger.error("I'm an error oh error")
    while True:
        for t in t_list:
            t.tick()
            t.check()

        time.sleep(config.TICK_TIME)
