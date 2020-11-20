#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
he_pin = 7

# Default goal temperature
set_temp = 221.

# Default sleep/wake times
sched_enabled = True
wake_time = '06:30'
sleep_time = '10:00'

# Main loop sample rate in seconds
sample_time = 0.1

# PID Proportional, Integral, and Derivative values
Pc = 3.4
Ic = 0.3
Dc = 40.0

Pw = 2.9
Iw = 0.3
Dw = 40.0

#Web/REST Server Options
port = 8080
