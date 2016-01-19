#!/usr/bin/python
import time
import RPi.GPIO as gpio
import sys
import math
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import PID as PID

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

# Raspberry Pi hardware SPI configuration.
SPI_PORT   = 0
SPI_DEVICE = 0
sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

boilerpin=4
gpio.setup(boilerpin, gpio.OUT)
gpio.output(boilerpin,0)

nanct=0

settemp=200.
sampletime=0.1
P=3.0
I=0.01
D=10.

pid = PID.PID(P,I,D)
pid.SetPoint = settemp
pid.setSampleTime(sampletime)

i=0
j=0

# mainLoop
try:
  while True :
    tempc = sensor.readTempC()
    tempf = c_to_f(tempc)

    if math.isnan(tempc) :
      nanct += 1
#      print ' nanct:',nanct
#      if nanct > 1000 :
#        break
      continue
    else:
      nanct = 0

    print ' tempc:',tempc,'*C'
    print ' tempf:',tempf,'*F'

    pid.update(tempf)
    pidout = pid.output
    print 'pidout:',pidout

    if pidout >= 100 :
      gpio.output(boilerpin,1)
      print 'boiler: on'
    elif pidout > 0 and pidout < 100 and tempf < settemp * 1.01 :
      if i%10 == 0 :
        j=int(pidout)/10
      if i%10 <= j :
        gpio.output(boilerpin,1)
        print 'boiler: on'
      else :
        gpio.output(boilerpin,0)
        print 'boiler: off'
    else:
      gpio.output(boilerpin,0)
      print 'boiler: off'

    print

    i+=1

    time.sleep(sampletime)

finally:
  pid.clear
  gpio.output(boilerpin,0)
  gpio.cleanup()
