#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
boiler_pin=26

# Default goal temperature
set_temp = 200.

# Main loop sample rate in seconds
sample_time=0.1

# PID Proportional, Integral, and Derivative values
P=3.0
I=0.01
D=10.
