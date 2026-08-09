import adafruit_dht
import board
import config
from writeDB import *
from pid_controller import *
from main import logger

class DHT22:
    def __init__(self):
        self.pin = f'D{config.PIN_DHT22}'
        self.pin = getattr(board, self.pin)
        

#function with adafruit_dht
    def get_temp_hum(self):
        dhtDevice = adafruit_dht.DHT22(self.pin, use_pulseio = False)
        
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            
            attributes = [
                {
                    "measurement": "temperature",
                    "fields": {"value": temperature},
                },
                {
                    "measurement": "humidity",
                    "fields": {"value": humidity},
                },
            ]
            #send tmeperature and humidity to influx writer
            writer = InfluxDBWriter()
            writer.write_data_attribute(attributes)

            #send temperature to pid controller
            pid = PIDController()
            pid.generate_pwm_output(temperature)
            
            logger.debug(f'Temperature: {temperature}°C')
            logger.debug(f'Humidity: {humidity}%')
            
        except RuntimeError:
            return
        
        except Exception:
            return

        finally:
            dhtDevice.exit()