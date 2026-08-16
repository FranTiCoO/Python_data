
#time between the measurements of each sensor in seconds
SENSOR_WAIT = 60
TICK_TIME = 0.1

#BUS address of TSL2561 sensor
ADD_TSL = 57

#frequency for PWM signal in Hz
PWM_FREQUENCY = 250

#define BCM channel OUT
PIN_LIGHT_TOGGLE = 18
PIN_LIGHT_MODE = 14
PIN_PUMP_TOGGLE = 23

#define BCM channel for temperature controller
PIN_TEMPERATURE_PWM = 4

#BCM channel were DHT22 is connected
PIN_DHT22 = 17

#times for pump
TIMES_PUMP_ON = ['07:00:00', '09:00:00', '13:25:00', '19:40:00']
TIME_PUMP_OFFSET = 1
DURATION_PUMP_ON = 5
PUMP_TIMER_ON = 0
PUMP_ON = 1

#timers for light
TIMES_LIGHT_MODE = {'day': '20:00:00', 'night': '22:00:00'}

#switching light
STATE_LIGHT = 0

#define variables for PID
KP = 1.0
KI = 0.0
KD = 0.0
SET_POINT = 28.0

# Enable relay-feedback PID tuning during startup when explicitly requested.
PID_SELF_OPTIMIZATION = False
PID_AUTOTUNE_OUTPUT_LOW = 0.0
PID_AUTOTUNE_OUTPUT_HIGH = 100.0
PID_AUTOTUNE_CYCLES = 3
