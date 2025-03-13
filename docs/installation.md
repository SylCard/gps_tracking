# Net Guardian Installation Guide

## Raspberry Pi Zero 2 W Setup

### 1. Initial Raspberry Pi Setup

1. Download the Raspberry Pi Imager from: https://www.raspberrypi.com/software/
2. Insert your microSD card into your computer
3. Open Raspberry Pi Imager
4. Click "CHOOSE OS" and select "Raspberry Pi OS (32-bit) Lite"
5. Click "CHOOSE STORAGE" and select your microSD card
6. Click the settings icon (gear symbol) and:
   - Set hostname: netguardian
   - Enable SSH
   - Set username and password
   - Configure your WiFi network
7. Click "WRITE" and wait for the process to complete

### 2. First Boot

1. Insert the microSD card into your Raspberry Pi Zero 2 W
2. Connect the VK-162 GPS dongle to the USB port (you may need a micro USB adapter)
3. Power up the Raspberry Pi
4. Wait about 2 minutes for the initial boot

### 3. Connect to Your Raspberry Pi

From your computer, open a terminal/command prompt:

```bash
# For Windows, use PowerShell or Command Prompt
ssh pi@netguardian.local

# If the above doesn't work, find your Pi's IP address from your router
# and use:
ssh pi@<your-pi-ip-address>
```

### 4. Install Net Guardian

Once connected via SSH, run these commands:

```bash
# Update package list
sudo apt update

# Install Git
sudo apt install -y git

# Clone the repository
git clone https://github.com/yourusername/net-guardian.git

# Navigate to device directory
cd net-guardian/device

# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

### 5. Verify Installation

1. Check if GPS daemon is running:
```bash
systemctl status gpsd
```

2. Check if Net Guardian service is running:
```bash
systemctl status net-guardian
```

3. Test GPS data reception:
```bash
cgps -s
```
You should see GPS data if the dongle is working correctly. It might take a few minutes to get the first fix, especially indoors.

### 6. Troubleshooting

If the GPS isn't working:

1. Check USB connection:
```bash
lsusb
```
You should see "VK-162 GPS" listed

2. Check if device is recognized:
```bash
ls -l /dev/ttyACM0
```

3. Restart GPS daemon:
```bash
sudo systemctl restart gpsd
```

4. Check logs:
```bash
journalctl -u gpsd
journalctl -u net-guardian
```

### Power Management Tips

- The Raspberry Pi Zero 2 W can be powered using a standard 5V/2.5A power bank
- Use a good quality power bank to avoid voltage drops
- The system draws approximately 120-150mA during normal operation
- A 10,000mAh power bank should provide roughly 2-3 days of operation

### Network Configuration

If you need to change WiFi settings later:

1. Edit the wpa_supplicant configuration:
```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

2. Add your network:
```
network={
    ssid="Your_WiFi_Name"
    psk="Your_WiFi_Password"
}
```

3. Restart networking:
```bash
sudo systemctl restart networking
```

## Next Steps

Once installation is complete, proceed to [usage.md](usage.md) for instructions on using the Net Guardian system. 