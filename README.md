# silvia-pi
A Raspberry Pi modification to the Rancilio Silvia Espresso Machine implementing PID temperature control.

Quick Installation instructions on Raspberry Pi 2 + Raspbian:
````
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install rpi-update git build-essential python-dev python-smbus python-pip
sudo rpi-update
sudo echo "dtparam=spi=on" >> /boot/config.txt
sudo reboot
````

After the reboot:
````
git clone https://github.com/brycesub/silvia-pi.git
cd silvia-pi
sudo ./setup.sh
````
