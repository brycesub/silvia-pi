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
Pcold = 3.6
Icold = 0.3
Dcold = 25.0

Pwarm = 3.0
Iwarm = 0.1
Dwarm = 18.0

#Web/REST Server Options
port = 8080
