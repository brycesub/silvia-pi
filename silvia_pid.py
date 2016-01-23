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

rGPIO.setup(conf.boiler_pin, GPIO.OUT)
rGPIO.output(conf.boiler_pin,0)

nanct=0

pid = PID.PID(conf.P,conf.I,conf.D)
pid.SetPoint = conf.set_temp
pid.setSampleTime(conf.sample_time)

i=0
j=0
pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
avgpid = 0

# mainLoop
try:
  while True : # Loops 10x/second
    tempc = sensor.readTempC()
    tempf = c_to_f(tempc)

    if math.isnan(tempc) :
      nanct += 1
#     print ' nanct:',nanct
      if nanct > 100000 :
        rGPIO.output(conf.boiler_pin,0)
        break
      continue
    else:
      nanct = 0
    print '  loop:',i
#   print ' tempc:',tempc,'*C'
    print ' tempf:',tempf,'*F'

    pid.update(tempf)
    pidout = pid.output
    pidhist[i%10] = pidout
    avgpid = sum(pidhist)/len(pidhist)
    print 'pidout:',pidout
    print 'avgpid:',avgpid

    if avgpid >= 100 :
      rGPIO.output(conf.boiler_pin,1)
      print 'boiler: on'
    elif avgpid > 0 and avgpid < 100 and tempf < conf.set_temp * 1.01 :
      if i%10 == 0 :
        j=int(avgpid)/10
      if i%10 <= j :
        rGPIO.output(conf.boiler_pin,1)
        print 'boiler: on'
      else :
        rGPIO.output(conf.boiler_pin,0)
        print 'boiler: off'
    else:
      rGPIO.output(conf.boiler_pin,0)
      print 'boiler: off'

    print

    i+=1

    time.sleep(conf.sample_time)

finally:
  pid.clear
  rGPIO.output(conf.boiler_pin,0)
  rGPIO.cleanup()
