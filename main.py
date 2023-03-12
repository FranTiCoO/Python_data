import time
import timer
import config

if __name__ == '__main__':
    
    timer_sensor = timer.TimerSensor(config.SENSOR_WAIT * 10)
    timer_pump = timer.TimerPump(1 * 10)
    
    timer_light_mode = timer.TimerLightMode(10 * 10)

    t_list = [timer_sensor, timer_pump, timer_light_mode]

    while True:
        
        for t in t_list:
            t.tick()
            t.check()

        time.sleep(config.TICK_TIME)
