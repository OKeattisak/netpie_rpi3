import microgear.client as microgear
import RPi.GPIO as GPIO
import time
import os
import glob
import requests

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pinList = [8,23,24,25]
TRIG = 16
ECHO = 20

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

appid = "xx"
gearkey = "xx"
gearsecret = "xx"

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

def connection():
    print "Now I am connected with netpie"

def subscription(topic, message):
    print topic + ":" + message


    if message == "RELAY1ON":
        GPIO.output(23, GPIO.LOW)
        microgear.chat("RELAY1STATUS","ON")
        
    elif message == "RELAY1OFF":
        GPIO.output(23, GPIO.HIGH)
        microgear.chat("RELAY1STATUS", "OFF")

    elif message == "RELAY2ON":
        microgear.chat("RELAY2STATUS", "ON")
        GPIO.output(24, GPIO.LOW)

    elif message == "RELAY2OFF":
        GPIO.output(24, GPIO.HIGH)
        microgear.chat("RELAY2STATUS", "OFF")

    elif message == "RELAY3ON":
        GPIO.output(25, GPIO.LOW)
        microgear.chat("RELAY3STATUS", "ON")
    elif message == "RELAY3OFF":
        GPIO.output(25, GPIO.HIGH)
        microgear.chat("RELAY3STATUS", "OFF")

    elif message == "RELAY4ON":
        GPIO.output(8, GPIO.LOW)
        microgear.chat("RELAY4STATUS", "ON")
    else:
        GPIO.output(8, GPIO.HIGH)
        microgear.chat("RELAY4STATUS", "OFF")


def disconnect():
    logging.debug("disconnect is work")


microgear.setalias("RPI3")
microgear.on_connect = connection
microgear.on_message = subscription
microgear.on_disconnect = disconnect
microgear.connect()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        print "Temp:", temp_c
        microgear.chat("TEMPWATER", temp_c)

def waterlevel():
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance,2)

    if distance > 2 and distance < 400:
        print "Water Level:", distance, "cm"
        microgear.chat("WATERLEVEL", distance)
        return distance
    else:
        print "Out Of Range"

while True:
    read_temp()
    waterlevel()