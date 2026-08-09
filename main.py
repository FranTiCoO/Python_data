#raspi-gpio set 18 op dl
#raspi-gpio set 18 op dh

import importlib
import os
import threading
import time

import config
import server
import timer
from logger_setup import logger


def thread_main():
    server.start_server()


if __name__ == '__main__':
    control_io = timer.control_io.ControlIO()

    logger.debug("Starting server...")
    t = threading.Thread(target=thread_main)
    t.start()
    logger.debug("...done")

    timer_sensor = timer.TimerSensor(config.SENSOR_WAIT * 10)
    timer_pump = timer.TimerPump(1 * 10)
    timer_light_mode = timer.TimerLightMode(10 * 10)

    config_path = config.__file__
    config_mtime = os.path.getmtime(config_path)

    t_list = [timer_sensor, timer_pump, timer_light_mode]
    logger.debug("Entering mainloop...")
    try:
        while True:
            try:
                current_mtime = os.path.getmtime(config_path)
                if current_mtime != config_mtime:
                    importlib.reload(config)
                    config_mtime = current_mtime
            except OSError:
                pass

            for timer_instance in t_list:
                timer_instance.tick()
                timer_instance.check()
            time.sleep(config.TICK_TIME)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        control_io.cleanup()


#logger.debug("Oh god i'm debugging")
#logger.info("Hello Ertl this is a info message")
#logger.warning("I'm a warning")
#logger.error("I'm an error oh error")
