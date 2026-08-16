import time

import adafruit_dht
import board
import config
from logger_setup import logger
from pid_controller import PIDController
from writeDB import InfluxDBWriter


class DHT22:
    def __init__(self):
        self.pin_name = f'D{config.PIN_DHT22}'
        self.pin = getattr(board, self.pin_name)
        self.pid_controller = PIDController()

    def get_temp_hum(self):
        dht_device = adafruit_dht.DHT22(self.pin, use_pulseio=False)
        retries = 3

        try:
            for attempt in range(retries):
                try:
                    temperature = dht_device.temperature
                    humidity = dht_device.humidity

                    if temperature is None or humidity is None:
                        raise RuntimeError("incomplete_data")

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

                    writer = InfluxDBWriter()
                    writer.write_data_attribute(attributes)

                    self.pid_controller.generate_pwm_output(temperature)

                    logger.debug(f'Temperature: {temperature}°C')
                    logger.debug(f'Humidity: {humidity}%')
                    if attempt > 0:
                        logger.warning(f"DHT22 data read successfully on attempt {attempt + 1}/{retries}")
                    return {"ok": True, "temperature": temperature, "humidity": humidity}

                except RuntimeError as exc:
                    if attempt < retries - 1:
                        logger.warning(f"DHT22 read attempt {attempt + 1}/{retries} failed: {exc}")
                        time.sleep(1)
                        continue
                    logger.warning(f"DHT22 read failed after {retries} attempts: {exc}")
                    return {"ok": False, "reason": "read_error"}

        except Exception as exc:
            logger.exception(f"Unexpected DHT22 error: {exc}")
            return {"ok": False, "reason": "unexpected_error"}

        finally:
            try:
                dht_device.exit()
            except Exception:
                logger.debug("DHT22 device cleanup failed")