import time

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from credentials import *
from logger_setup import logger

class InfluxDBWriter:
    def __init__(self):
        self.url = INFLUX_URL
        self.token = INFLUX_TOKEN
        self.org = INFLUX_ORG
        self.bucket = INFLUX_BUCKET
        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
    
    #write attribute to InfluxDB
    def write_data(self, data):
        max_retries = 3
        retry_delay_s = 0.5

        for attempt in range(max_retries):
            try:
                self.write_api.write(bucket=self.bucket, org=self.org, record=data)
                return True
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay_s)

        return False

    #create attribute from dictionary  
    def write_data_attribute(self, attributes):
        data = []
        
        for attribute in attributes:
            data.append({"measurement": attribute["measurement"], "fields": attribute["fields"]})

        self.write_data(data)