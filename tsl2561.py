#!/usr/bin/python3

import time
import sys
import uuid

import board
import busio
import adafruit_tsl2561
 
import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""

try:
    r = redis.StrictRedis(host=redis_host, port=redis_port,
            password=redis_password, decode_responses=True)
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the TSL2561 instance, passing in the I2C bus
    tsl = adafruit_tsl2561.TSL2561(i2c)
    tsl.enabled = True
    
    # Print chip info
    # print("Chip ID = {}".format(tsl.chip_id))
    # print("Enabled = {}".format(tsl.enabled))
    # print("Gain = {}".format(tsl.gain))
    # print("Integration time = {}".format(tsl.integration_time))
    
    # print("Configuring TSL2561...")
    
    # Enable the light sensor
    # sleep(100) 
    # Set gain 0=1x, 1=16x
    tsl.gain = 0
    
    # Set integration time (0=13.7ms, 1=101ms, 2=402ms, or 3=manual)
    tsl.integration_time = 1
    
    # Disble the light sensor (to save power)
    sys.stdout.write("\nLogging TSL2561 sensor data\nProgress:.")
    pipe = r.pipeline()

    while True:
        log_timestamp = time.time();
        log_id = uuid.uuid4()

        # print("Getting readings...")
        # Get raw (luminosity) readings individually
        broadband = tsl.broadband
        infrared = tsl.infrared
        
        # Get raw (luminosity) readings using tuple unpacking
        #broadband, infrared = tsl.luminosity
        
        # Get computed lux value
        lux = tsl.lux
        
        # Print results
        # print("Enabled = {}".format(tsl.enabled))
        # print("Gain = {}".format(tsl.gain))
        # print("Integration time = {}".format(tsl.integration_time))
        # print("Broadband = {}".format(broadband))
        # print("Infrared = {}".format(infrared))
        # print("Lux = {}".format(lux))
    
        sensor_data = {
            "enabled": tsl.enabled,
            "gain": tsl.gain,
            "integration_time": tsl.integration_time,
            "broadband": broadband,
            "infrared": infrared,
            "lux": lux,
            "time": log_timestamp,
        }
        pipe.hmset('tsl2561:%s' % log_id, sensor_data)
        pipe.zadd('tsl2561_keys', log_timestamp, log_id)


        pipe.execute()
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)

except KeyboardInterrupt as e:
    tsl.enabled = False
    sys.stdout.write("\nStopping TSL2561 logger\n")
    quit(0)

