#!/usr/bin/python
import time
import sys
import math
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import PID as PID
import config as conf

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

sensor = MAX31855.MAX31855(spi=SPI.SpiDev(conf.spi_port, conf.spi_dev))

rGPIO = GPIO.get_platform_gpio()

rGPIO.setup(conf.he_pin, GPIO.OUT)
rGPIO.output(conf.he_pin,0)

nanct=0

pid = PID.PID(conf.P,conf.I,conf.D)
pid.SetPoint = conf.set_temp
pid.setSampleTime(conf.sample_time)

i=0
j=0
pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
avgpid = 0
hestat = 0

print 'i,tempf,pidout,pidavg,hestat'

# mainLoop
try:
  while True : # Loops 10x/second
    tempc = sensor.readTempC()
    tempf = c_to_f(tempc)

    if math.isnan(tempc) :
      nanct += 1
#     print ' nanct:',nanct
      if nanct > 100000 :
        rGPIO.output(conf.he_pin,0)
        break
      continue
    else:
      nanct = 0

    pid.update(tempf)
    pidout = pid.output
    pidhist[i%10] = pidout
    avgpid = sum(pidhist)/len(pidhist)

    if avgpid >= 100 :
      hestat = 1
    elif avgpid > 0 and avgpid < 100 and tempf < conf.set_temp * 1.02 :
      if i%10 == 0 :
        j=int(avgpid)/10
      if i%10 <= j :
        hestat = 1
      else :
        hestat = 0
    else:
      hestat = 0

    rGPIO.output(conf.he_pin,hestat) 
    
    print i,tempf,pidout,avgpid,hestat

    i += 1

    time.sleep(conf.sample_time)

finally:
  pid.clear
  rGPIO.output(conf.he_pin,0)
  rGPIO.cleanup()
