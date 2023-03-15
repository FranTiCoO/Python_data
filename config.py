
#time between the measurements of each sensor in seconds
SENSOR_WAIT = 10.0
TICK_TIME = 0.1

#BUS address of TSL2561 sensor
ADD_TSL = 0x39

#frequency for PWM signal in Hz
PWM_FREQUENCY = 250

#define BCM channel OUT
PIN_LIGHT_TOGGLE = 18   #light ON/OFF
PIN_LIGHT_MODE = 14    #switch DAY/NIGHT
PIN_PUMP_TOGGLE = 23    #pump ON/OFF

#define BCM channel for temperature controller
PIN_TEMPERATURE_PWM = 4

#BCM channel were DHT22 is connected
PIN_DHT22 = 17

#times for pump
TIMES_PUMP_ON = ['7:00:12', '9:00:00', '13:25:00', '19:34:00'] 
TIME_PUMP_OFFSET = 1
DURATION_PUMP_ON = 5

#timers for light
TIMES_LIGHT_MODE = {"night": "20:00:00", "day": "7:00:00"}

#define variables for PID
KP = 1.0
KI = 0.0
KD = 0.0
SET_POINT = 28
