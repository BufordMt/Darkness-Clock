#####################################################################################
####    wjnGPSReader.py  GLOBAL POSITIONING SYSTEM READER
####    Version 1, July 24, 2023 Revised September 8, 2023
####    William Neubert
#####################################################################################

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.

# MODIFIED BY WILLIAM NEUBERT, JULY 24, 2023

import time
import board
import busio
import adafruit_gps

global uart
global gps

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
# uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
import serial

def wjngStartGPS():
    global gps
    # uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10) # USING THE SPI INTERFACE
    # Create a GPS module instance.
    gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
    # gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface

    # Initialize the GPS module by changing what data it sends and at what rate.
    # These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
    # PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
    # the GPS module behavior:
    #   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    # Turn on just minimum info (RMC only, location):
    # gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Turn off everything:
    # gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    # Turn on everything (not all of it is parsed!)
    # gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

    # Set update rate to once a second (1hz) which is what you typically want.
    gps.send_command(b"PMTK220,1000")
    # Or decrease to once every two seconds by doubling the millisecond value.
    # Be sure to also increase your UART timeout above!
    # gps.send_command(b'PMTK220,2000')
    # You can also speed up the rate, but don't go too fast or else you can lose
    # data during parsing.  This would be twice a second (2hz, 500ms delay):
    # gps.send_command(b'PMTK220,500')
    uart.reset_input_buffer()
    return gps

# Main loop runs forever printing the location, etc. every second.
# last_print = time.monotonic()

def wjngGetGPSData():
    global gps
    
    gps.update()
    # i=0
    # while (i<10) and (not gps.has_fix):
    #         gps.update()
    #         time.sleep(1000)
    #         # Try again if we don't have a fix yet.
    #         print("Waiting for fix...")
    #         i += 1
    datestr = "{}-{}-{} {:02}:{:02}:{:02}".format(
        gps.timestamp_utc.tm_year,  
        gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
        gps.timestamp_utc.tm_mday,  # struct_time object that holds the fix time.  Note you might
        gps.timestamp_utc.tm_hour,  # not get all data like year, day,
        gps.timestamp_utc.tm_min,  # month!
        gps.timestamp_utc.tm_sec
        )

    returndata = {"time":datestr, "lon":gps.longitude, "lat":gps.latitude, "alt":gps.altitude_m, "hdop":gps.horizontal_dilution, "fix":gps.has_fix}
    #print(returndata)
    return returndata

# class wjngGPS:
#     def __init__()