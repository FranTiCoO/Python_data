from config import *
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

class InfluxDBWriter:
    def __init__(self):
        self.url = INFLUX_URL
        self.token = INFLUX_TOKEN
        self.org = INFLUX_ORG
        self.bucket = INFLUX_BUCKET
        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
    
    #write attribute to InfluxDB
    def write_data(self, data):
        async_write = self.write_api.write(bucket=self.bucket, org=self.org, record=data)
        async_write.get()

    #create attribute from dictionary  
    def write_data_attribute(self, attributes):
        data = []
        
        for attribute in attributes:
            data.append({"measurement": attribute["measurement"], "fields": attribute["fields"]})

        self.write_data(data)