import smbus
import time
from config import *
from writeDB import *
from main import logger

class TSL2561:
    def __init__(self):
        self.sensor_address = ADD_TSL
        self.writer = InfluxDBWriter()
    
    def get_lum(self):
        bus = smbus.SMBus(1)
        
        #initializing TSL2561
        bus.write_byte_data(self.sensor_address, 0x00 | 0x80, 0x03)
        bus.write_byte_data(self.sensor_address, 0x01 | 0x80, 0x02)

        time.sleep(0.5)

        #read values from TSL2561
        data = bus.read_i2c_block_data(self.sensor_address, 0x0C | 0x80, 2)
        data1 = bus.read_i2c_block_data(self.sensor_address, 0x0E | 0x80, 2)

        # Convert the data
        channel0 = data[1] * 256 + data[0]
        channel1 = data1[1] * 256 + data1[0]

        #create light values
        full = channel0
        infrared = channel1
        visible = channel0 - channel1
        
        #create dictionary from light values
        attributes = [
            {
                "measurement": "light_full",
                "fields": {"value": full},
            },
            {
                "measurement": "light_infrared",
                "fields": {"value": infrared},
            },
            {
                "measurement": "light_visible",
                "fields": {"value": visible},
            },
        ]
        
        #write values to InfluxDB
        self.writer.write_data_attribute(attributes)
        
        logger.debug(f'Full: {full}lum')
        logger.debug(f'Infrared: {infrared}lum')
        logger.debug(f'Visible: {visible}lum')
        logger.debug("------------------------------------")

        
