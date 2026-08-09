#raspi-gpio set 18 op dl
#raspi-gpio set 18 op dh

import logging
import time
import importlib
import os

import config
import timer
import server
import threading

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)d]     %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)

def thread_main():
    server.start_server()

if __name__ == '__main__':

    logging.debug("Starting server...")
    t = threading.Thread(target=thread_main)
    t.start()
    logging.debug("...done")
    
    timer_sensor = timer.TimerSensor(config.SENSOR_WAIT * 10)
    timer_pump = timer.TimerPump(1 * 10)
    timer_light_mode = timer.TimerLightMode(10 * 10)

    config_path = config.__file__
    config_mtime = os.path.getmtime(config_path)

    t_list = [timer_sensor, timer_pump, timer_light_mode]
    logging.debug("Entering mainloop...")
    while True:
        try:
            current_mtime = os.path.getmtime(config_path)
            if current_mtime != config_mtime:
                importlib.reload(config)
                config_mtime = current_mtime
        except OSError:
            pass

        for t in t_list:
            t.tick()
            t.check()
        time.sleep(config.TICK_TIME)


#logger.debug("Oh god i'm debugging")
#logger.info("Hello Ertl this is a info message")
#logger.warning("I'm a warning")
#logger.error("I'm an error oh error")
