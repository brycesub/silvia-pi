#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin # for relay connected to heating element
he_pin = 26

# Default goal temperature
set_temp = 221.

# Main loop sample rate in seconds
sample_time = 0.1

# PID Proportional, Integral, and Derivative values
P = 3.3
I = 0.04
D = 2.5
