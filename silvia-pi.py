#!/usr/bin/python

def pid_loop(dummy,state):
  import sys
  from time import sleep
  from datetime import datetime, timedelta
  from math import isnan
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
  pid.SetPoint = state['settemp']
  pid.setSampleTime(conf.sample_time)

  nanct=0
  i=0
  j=0
  pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
  avgpid = 0.
  temphist = [0.,0.,0.,0.,0.]
  avgtemp = 0.
  hestat = 0
  lastsettemp = state['settemp']

  try:
    while True : # Loops 10x/second
      """
      if state['snoozeon'] == True :
        szto = ''
        sztoday = datetime.now().replace(minute=szin.minute,hour=szin.hour,second=0,microsecond=0)
        sztomorrow = sztoday+timedelta(days=1)
        if sztoday > datetime.now() :
          szto = sztoday
        else:
          szto = sztomorrow

        if datetime.now() >= state['snoozeon'] :
          state['snoozeon'] = False
        else:
          sleep(1)
          continue
      """
      tempc = sensor.readTempC()
      tempf = c_to_f(tempc)
      temphist[i%5] = tempf
      avgtemp = sum(temphist)/len(temphist)

      if isnan(tempc) :
        nanct += 1
        if nanct > 100000 :
          rGPIO.output(conf.he_pin,0)
          break
        continue
      else:
        nanct = 0

      if state['settemp'] != lastsettemp :
        pid.SetPoint = state['settemp']
        lastsettemp = state['settemp']

      pid.update(avgtemp)
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
      state['avgtemp'] = round(avgtemp,2)
      state['pidval'] = round(pidout,2)
      state['avgpid'] = round(avgpid,2)
      state['pterm'] = round(pid.PTerm,2)
      state['iterm'] = round(pid.ITerm * conf.I,2)
      state['dterm'] = round(pid.DTerm * conf.D,2)
      state['hestat'] = hestat

      print state

      i += 1
      sleep(conf.sample_time)

  finally:
    pid.clear
    rGPIO.output(conf.he_pin,0)
    rGPIO.cleanup()

def rest_server(dummy,state):
  from bottle import route, run, get, post, request, static_file, abort
  from subprocess import call
  import config as conf
  import os

  basedir = os.path.dirname(__file__)
  wwwdir = basedir+'/www/'

  @route('/')
  def docroot():
    return static_file('index.html',wwwdir)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwdir)

  @route('/curtemp')
  def curtemp():
    return str(state['avgtemp'])

  @get('/settemp')
  def settemp():
    return str(state['settemp'])

  @post('/settemp')
  def post_settemp():
    try:
      settemp = float(request.forms.get('settemp'))
      if settemp >= 200 and settemp <= 260 :
        state['settemp'] = settemp
        return str(settemp)
      else:
        abort(400,'Set temp out of rante 200-260.')
    except:
      abort(400,'Invalid number for set temp.')

  @get('/snooze')
  def get_snooze():
    return str(state['snooze'])

  @post('/snooze')
  def post_snooze():
    snooze = request.forms.get('snooze')
    try:
      szin = datetime.strptime(snooze,'%H:%M')
    except:
      abort(400,'Invalid time format.')
    state['snoozeon'] = True
    state['snooze'] = snooze
    return str(snooze)

  @route('/allstats')
  def allstats():
    return dict(state)

  @route('/restart')
  def restart():
    call(["reboot"])
    return '';

  @route('/healthcheck')
  def healthcheck():
    return 'OK'

  run(host='0.0.0.0',port=conf.port,server='cherrypy')

if __name__ == '__main__':
  from multiprocessing import Process, Manager
  from time import sleep
  from urllib2 import urlopen
  import config as conf

  manager = Manager()
  pidstate = manager.dict()
  pidstate['snooze'] = conf.snooze 
  pidstate['snoozeon'] = False
  pidstate['i'] = 0
  pidstate['settemp'] = conf.set_temp

  p = Process(target=pid_loop,args=(1,pidstate))
  p.daemon = True
  p.start()

  r = Process(target=rest_server,args=(1,pidstate))
  r.daemon = True
  r.start()

  #Start Watchdog loop
  piderr = 0
  weberr = 0
  weberrflag = 0
  urlhc = 'http://localhost:'+str(conf.port)+'/healthcheck'

  lasti = pidstate['i']
  sleep(1)

  while True:
    curi = pidstate['i']
    if curi == lasti :
      piderr = piderr + 1
    else :
      piderr = 0

    lasti = curi

    if piderr > 9 :
      print 'ERROR IN PID THREAD, RESTARTING'
      p.terminate()
      sleep(60)
      p.run()
      sleep(2)

    try:
      hc = urlopen(urlhc,timeout=2)
    except:
      weberrflag = 1
    else:
      if hc.getcode() != 200 :
        weberrflag = 1

    if weberrflag != 0 :
      weberr = weberr + 1

    if weberr > 9 :
      print 'ERROR IN WEB SERVER THREAD, RESTARTING'
      r.terminate()
      sleep(2)
      r.run()
      sleep(2)

    weberrflag = 0

    sleep(1)
