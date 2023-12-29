#!/usr/bin/python

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

# Pin number for relay connected to heating element
heating_element_pin = 26

# Default goal temperature
default_goal_temperature = 221.0

# Default sleep/wake times
scheduled_enabled = True
wake_time = '06:30'
sleep_time = '10:00'

# Main loop sample rate in seconds
sample_rate = 0.1

# PID Proportional, Integral, and Derivative values for cooling
cooling_pid_constants = {
    'P': 3.4,
    'I': 0.3,
    'D': 40.0
}

# PID Proportional, Integral, and Derivative values for warming
warming_pid_constants = {
    'P': 2.9,
    'I': 0.3,
    'D': 40.0
}

# Web/REST Server Options
server_port = 808
