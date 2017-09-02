#!/bin/bash
SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

if [[ $(whoami) -ne 'root' ]]; then
  echo "Must run as root!"
  exit -1
fi

apt-get -y install rpi-update git build-essential python-dev python-smbus python-pip logrotate

echo "Installing logrotate config..."
cp $BASEDIR/silvia-pi-logrotate /etc/logrotate.d

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

echo "Installing remaining python libraries..."
pip install --upgrade -r $BASEDIR/requirements.txt

if ! grep silvia-pi.py /etc/rc.local; then
  echo "Adding entry to /etc/rc.local"
  cp /etc/rc.local /etc/rc.local.bak
  cat /etc/rc.local | sed 's|^exit 0$|/root/silvia-pi/silvia-pi.py > /root/silvia-pi/silvia-pi.log 2>\&1 \&\n\nexit 0|g' > /etc/rc.local.new
  mv /etc/rc.local.new /etc/rc.local
  chmod 755 /etc/rc.local
else
  echo "Skipping /etc/rc.local modification since entry already found"
fi

echo "Installation complete.  Please reboot."
