#!/usr/bin/python

import time
import logging
from threading import Timer
from datetime import datetime
from bottle import route, run, get, post, request, static_file, abort
from subprocess import call
from urllib2 import urlopen
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import PID as PID
import config as conf
import os

logging.basicConfig(filename='scheduler.log', level=logging.INFO)

def log_to_file(filename, message):
    with open(filename, 'a') as log_file:
        log_file.write(message + '\n')

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def delayed_function():
    # Code to be executed after the specified time
    pass

def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(conf.he_pin, GPIO.OUT)
    GPIO.output(conf.he_pin, 0)

def cleanup_gpio():
    GPIO.output(conf.he_pin, 0)
    GPIO.cleanup()

def scheduler(dummy, state):
    log_to_file("scheduler.log", "Starting scheduler thread ...")

    last_wake = 0
    last_sleep = 0
    last_sched_switch = 0

    while True:
        if (last_wake != state['wake_time'] or
                last_sleep != state['sleep_time'] or
                last_sched_switch != state['sched_enabled']):

            # Clear the schedule
            schedule.clear()

            if state['sched_enabled']:
                schedule.every().day.at(state['sleep_time']).do(gotosleep, 1, state)
                schedule.every().day.at(state['wake_time']).do(wakeup, 1, state)

                # Additional logic to handle the case when wake_time is greater than sleep_time

            else:
                wakeup(1, state)

            last_wake = state['wake_time']
            last_sleep = state['sleep_time']
            last_sched_switch = state['sched_enabled']

            schedule.run_pending()

            time.sleep(1)

def wakeup(dummy, state):
    state['is_awake'] = True

def gotosleep(dummy, state):
    state['is_awake'] = False

def he_control_loop(dummy, state):
    initialize_gpio()

    heating = False

    try:
        while True:
            avg_pid = state['avgpid']

            if not state['is_awake']:
                state['heating'] = False
                GPIO.output(conf.he_pin, 0)
                time.sleep(1)
            else:
                # Additional logic for heating control
                pass

    finally:
        cleanup_gpio()

def pid_loop(dummy, state):
    # PID loop implementation
    pass

def rest_server(dummy, state):
    # REST server implementation
    pass

if __name__ == '__main__':
    from multiprocessing import Process, Manager
    from time import sleep

    manager = Manager()
    pidstate = manager.dict()
    pidstate['is_awake'] = True
    pidstate['sched_enabled'] = conf.sched_enabled
    pidstate['sleep_time'] = conf.sleep_time
    pidstate['wake_time'] = conf.wake_time
    pidstate['i'] = 0
    pidstate['settemp'] = conf.set_temp
    pidstate['avgpid'] = 0.

    processes = []

    # Start Scheduler thread
    s = Process(target=scheduler, args=(1, pidstate))
    s.daemon = True
    s.start()
    processes.append(s)

    # Start PID thread
    p = Process(target=pid_loop, args=(1, pidstate))
    p.daemon = True
    p.start()
    processes.append(p)

    # Start HE Control thread
    h = Process(target=he_control_loop, args=(1, pidstate))
    h.daemon = True
    h.start()
    processes.append(h)

    # Start REST Server thread
    r = Process(target=rest_server, args=(1, pidstate))
    r.daemon = True
    r.start()
    processes.append(r)

    # Start Watchdog loop
    processes.append(Process(target=watchdog, args=(1, pidstate, processes)))
    processes[-1].start()

    # Additional logic to keep the main process alive
    try:
        while all(process.is_alive() for process in processes):
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            process.terminate()
            process.join()

def watchdog(dummy, state, processes):
    # Watchdog loop implementation
    pass
def watchdog(dummy, state, processes):
    url_healthcheck = 'http://localhost:' + str(conf.port) + '/healthcheck'
    pid_err = 0
    web_err = 0
    web_err_flag = 0

    last_i = pidstate['i']
    sleep(1)

    while all(process.is_alive() for process in processes):
        cur_i = pidstate['i']
        if cur_i == last_i:
            pid_err += 1
        else:
            pid_err = 0

        last_i = cur_i

        if pid_err > 9:
            log_to_file("watchdog.log", 'ERROR IN PID THREAD, RESTARTING')
            processes[1].terminate()

        try:
            health_check = urlopen(url_healthcheck, timeout=2)
        except:
            web_err_flag = 1
        else:
            if health_check.getcode() != 200:
                web_err_flag = 1

        if web_err_flag != 0:
            web_err += 1

        if web_err > 9:
            log_to_file("watchdog.log", 'ERROR IN WEB SERVER THREAD, RESTARTING')
            processes[3].terminate()

        web_err_flag = 0

        sleep(1)

       if __name__ == '__main__':
           from multiprocessing import Process, Manager

           manager = Manager()
           pidstate = manager.dict()
           pidstate['is_awake'] = True
           pidstate['sched_enabled'] = conf.sched_enabled
           pidstate['sleep_time'] = conf.sleep_time
           pidstate['wake_time'] = conf.wake_time
           pidstate['i'] = 0
           pidstate['settemp'] = conf.set_temp
           pidstate['avgpid'] = 0.

           processes = []

           # Starting Scheduler thread
           print("Starting Scheduler thread...")
           s = Process(target=scheduler, args=(1, pidstate))
           s.daemon = True
           s.start()
           processes.append(s)

           # Starting PID thread
           print("Starting PID thread...")
           p = Process(target=pid_loop, args=(1, pidstate))
           p.daemon = True
           p.start()
           processes.append(p)

           # Starting HE Control thread
           print("Starting HE Control thread...")
           h = Process(target=he_control_loop, args=(1, pidstate))
           h.daemon = True
           h.start()
           processes.append(h)

           # Starting REST Server thread
           print("Starting REST Server thread...")
           r = Process(target=rest_server, args=(1, pidstate))
           r.daemon = True
           r.start()
           processes.append(r)

           # Start Watchdog loop
           print("Starting Watchdog...")
           w = Process(target=watchdog, args=(1, pidstate, processes))
           w.daemon = True
           w.start()
           processes.append(w)

           try:
               for process in processes:
                   process.join()
           except KeyboardInterrupt:
               print("\nTerminating processes...")
               for process in processes:
                   process.terminate()
                   process.join()


 

