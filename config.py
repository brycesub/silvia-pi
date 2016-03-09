#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
he_pin = 26

# Default goal temperature
set_temp = 221.

# Default alarm time
snooze = '07:00'

# Main loop sample rate in seconds
sample_time = 0.1

# PID Proportional, Integral, and Derivative values
Pc = 3.5
Ic = 0.3
Dc = 25.0

Pw = 2.8
Iw = 0.3
Dw = 50.0

#Web/REST Server Options
port = 8080
