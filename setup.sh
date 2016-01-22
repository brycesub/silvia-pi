#!/bin/bash

if [[ $(whoami) -ne 'root' ]]; then
  echo "Must run as root!"
  exit -1
fi

echo "Installing Adafruit GPIO library..."
cd ~
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd ~/Adafruit_Python_GPIO
python setup.py install

echo "Installing MAX31855 Thermocouple Amp library..."
cd ~
git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
cd ~/Adafruit_Python_MAX31855
python setup.py install

echo "Installing ivPID library..."
cd ~
git clone https://github.com/ivmech/ivPID.git
cp ~/ivPID/PID.py ~/silvia-pi/

echo "Setting crontab entry to reboot @ midnight"
echo "0 0 * * * reboot" >> /var/spool/cron/crontabs/root

echo "Adding entry to /etc/rc.local"
cp /etc/rc.local /etc/rc.local.bak
cat /etc/rc.local | sed 's|exit 0|/root/siliva-pi/silvia_pid.py > /root/silvia-pi/silvia_pi.log 2>\&1 \&\n\nexit 0|g' > /etc/rc.local.new
mv /etc/rc.local.new /etc/rc.local

echo "Installation complete.  Please reboot."
