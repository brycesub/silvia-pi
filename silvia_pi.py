#!/usr/bin/python

from multiprocessing import Process, Manager

def pid_loop(dummy,state):
  import time
  import sys
  import math
  import Adafruit_GPIO as GPIO
  import Adafruit_GPIO.SPI as SPI
  import Adafruit_MAX31855.MAX31855 as MAX31855
  import PID as PID
  import config as conf

  def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

  sensor = MAX31855.MAX31855(spi=SPI.SpiDev(conf.spi_port, conf.spi_dev))

  rGPIO = GPIO.get_platform_gpio()
  rGPIO.setup(conf.he_pin, GPIO.OUT)
  rGPIO.output(conf.he_pin,0)

  pid = PID.PID(conf.P,conf.I,conf.D)
  pid.SetPoint = conf.set_temp
  pid.setSampleTime(conf.sample_time)

  nanct=0
  i=0
  j=0
  pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
  avgpid = 0
  hestat = 0

  print 'P =',conf.P,'I =',conf.I,'D =',conf.D,'Set Temp =',conf.set_temp
  print 'i tempf pidout pidavg pterm iterm dterm hestat'

  try:
    while True : # Loops 10x/second
      tempc = sensor.readTempC()
      tempf = c_to_f(tempc)

      if math.isnan(tempc) :
        nanct += 1
#       print ' nanct:',nanct
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
      elif avgpid > 0 and avgpid < 100 and tempf < conf.set_temp :
        if i%10 == 0 :
          j=int((avgpid/10)+.5)
        if i%10 <= j :
          hestat = 1
        else :
          hestat = 0
      else:
        hestat = 0

      rGPIO.output(conf.he_pin,hestat) 

      state['i'] = i
      state['tempf'] = round(tempf,2)
      state['pidval'] = round(pidout,2)
      state['avgpid'] = round(avgpid,2)
      state['pterm'] = round(pid.PTerm,2)
      state['iterm'] = round(pid.ITerm * conf.I,2)
      state['dterm'] = round(pid.DTerm * conf.D,2)
      state['settemp'] = round(conf.set_temp,2)
      state['hestat'] = hestat

      print state

      i += 1
      time.sleep(conf.sample_time)

  finally:
    pid.clear
    rGPIO.output(conf.he_pin,0)
    rGPIO.cleanup()

def rest_server(dummy,state):
  from bottle import route, run, template, get, post, request, static_file
  import config as conf

  @route('/')
  def docroot():
    return static_file('index.html',conf.wwwdir)

  @route('/<filename>')
  def servfile(filename):
    return static_file(filename,conf.wwwdir)

  @route('/curtemp')
  def curtemp():
    return str(state['tempf'])

  @get('/settemp')
  def settemp():
    return str(state['settemp'])

  @post('/settemp')
  def post_settemp():
    settemp = request.forms.get('settemp')
    if settemp > 200 and settemp < 265 :
      state['settemp'] = settemp
      return str(settemp)
    return str(-1)

  @route('/allstats')
  def allstats():
    return dict(state)

  run(host='0.0.0.0',port=conf.port)

if __name__ == '__main__':
  manager = Manager()
  pidstate = manager.dict()

  p = Process(target=pid_loop,args=(1,pidstate))
  p.start()

  r = Process(target=rest_server,args=(1,pidstate))
  r.start()

  p.join()
  r.join()
