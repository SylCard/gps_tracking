#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y gpsd gpsd-clients python3-pip

# Install Python requirements
pip3 install -r requirements.txt

# Configure gpsd to use the VK-162 GPS dongle
sudo echo 'DEVICES="/dev/ttyACM0"' > /etc/default/gpsd
sudo systemctl enable gpsd
sudo systemctl start gpsd

# Install service file
sudo cp systemd/net-guardian.service /etc/systemd/system/
sudo systemctl enable net-guardian
sudo systemctl start net-guardian

echo "Setup complete! Net Guardian will start automatically on boot." 