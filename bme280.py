#!/usr/bin/python3

import time
import sys
import uuid
 
import board
import busio
import adafruit_bme280

import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""

temp_threshold = (18, 22)
humidity_threshold = (40, 60)

try:
    r = redis.StrictRedis(host=redis_host, port=redis_port,
            password=redis_password, decode_responses=True)

    # Create library object using our Bus I2C port
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    
    
    # change this to match the location's pressure (hPa) at sea level
    bme280.sea_level_pressure = 1013.25
    
    sys.stdout.write("\nLogging BME280 sensor data\nProgress:.")
    pipe = r.pipeline()
    while True:
        log_timestamp = time.time();
        log_id = uuid.uuid4()

        sensor_data = {
                "temperature": bme280.temperature,
                "humidity": bme280.humidity,
                "pressure": bme280.pressure,
                "altitude": bme280.altitude,
                "time": log_timestamp,
                }
        pipe.hmset('bme280:%s' % log_id, sensor_data)
        pipe.zadd('bme280_keys', log_timestamp, log_id)

        if (bme280.humidity < humidity_threshold[0] 
                or bme280.humidity > humidity_threshold[1]):
            pipe.publish('alerts:humidity', bme280.humidity)
        
        if (bme280.temperature < temp_threshold[0]
                or bme280.temperature > temp_threshold[1]):
            pipe.publish('alerts:temperature', bme280.temperature)

        pipe.execute()
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)

except KeyboardInterrupt as e:
    sys.stdout.write("\nStopping BME280 logger\n")
    quit(0)

