#!/usr/bin/env python

import serial
import requests
from datetime import datetime, timedelta

# Set the serial port to the same serial port you uploaded the arduino sketch to
# In the Arduino IDE, click "Tools > Serial Port"
# SERIAL_PORT = "/dev/tty.usbserial-A70064Mh"
SERIAL_PORT = "/dev/tty.usbserial-AH00PP05"
SERIAL_BAUD = 115200

# Don"t send more than one message every 30 minutes
SENSOR_INTERVAL = timedelta(minutes=30)

SMS_FROM = "YOUR TWILIO NUMBER" # Make sure this is a number on twilio.com
SMS_TO = "YOUR CELL PHONE NUMBER"
SMS_BODY = "ALERT! Your Arduino just detected motion!"
TWILIO_ACCOUNT_SID = "YOUR TWILIO ACCOUNT SID"
TWILIO_TOKEN = "YOUR TWILIO ACCOUNT TOKEN"

# Try to import TWILIO_ACCOUNT_SID and such from settings_local.py, if it exists
try:
    from settings_local import *
except ImportError:
    pass

TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/%s/SMS/Messages" % TWILIO_ACCOUNT_SID

# Start the server
if __name__ == "__main__":
    print "Starting SMS motion detector server at", datetime.now()
    last_sent_time = None

    # Open a serial connection to the Arduino
    with serial.Serial(SERIAL_PORT, SERIAL_BAUD) as arduino:
        while True:
            print "Polling Arduino..."

            # Listen for the Arduino to send a byte
            byte_received = arduino.read()

            print "Received byte:", byte_received

            # Motion was detected
            if byte_received == "1":
                print "Motion detected at", datetime.now()

                # If we haven"t sent an SMS in the last 30 minutes, send one now
                if not last_sent_time or (datetime.now() - last_sent_time) > SENSOR_INTERVAL:
                    last_sent_time = datetime.now()
                    print "Sending SMS..."

                    # Send request to Twilo to send SMS
                    try:
                        data = {
                            "From": SMS_FROM,
                            "To": SMS_TO,
                            "Body": SMS_BODY,
                        }
                        requests.post(TWILIO_SMS_URL, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_TOKEN))

                        print "** SMS Sent! **"

                    except Exception as e:
                        print "Some error occurred while sending SMS:", e
