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
   - Enable SSH (for initial setup only)
   - Set username and password
   - Configure WiFi:
     - SSID: Your phone's hotspot name
     - Password: Your hotspot password
7. Click "WRITE" and wait for the process to complete
8. After writing is complete, remove and reinsert the microSD card
9. Create an empty file named `ssh` in the boot partition of the SD card
10. Create a file named `config.txt` in the boot partition (or edit if it exists) and add:
    ```
    dtoverlay=dwc2
    ```
11. Edit `cmdline.txt` in the boot partition and add after `rootwait`:
    ```
    modules-load=dwc2,g_ether
    ```

### 2. Connection Options

You have two options for the initial setup:

#### Option A: Phone Hotspot Method (Recommended)

1. Enable your phone's hotspot with the same SSID and password you configured in step 6
2. Insert the microSD card into your Raspberry Pi Zero 2 W
3. Connect the VK-162 GPS dongle to the USB port
4. Power up the Raspberry Pi using a power bank or power supply
5. On your laptop, connect to the same phone hotspot
6. Wait about 2 minutes for the Pi to boot and connect
7. The Pi will automatically connect to your phone's hotspot
8. Find your Pi's IP address using one of these methods:
   - Check your phone's hotspot settings for connected devices
   - Use a network scanner app on your phone
   - Try: `ping netguardian.local` from your laptop

#### Option B: USB Connection Method

1. Insert the microSD card into your Raspberry Pi Zero 2 W
2. Connect the VK-162 GPS dongle to the USB port using a USB OTG adapter
3. Connect the Raspberry Pi to your computer using the USB data port (not the power port)
   - Use the port marked "USB" on the Pi, not the one marked "PWR"
   - This will create both a power and network connection
4. Power up the Raspberry Pi
5. Wait about 2 minutes for the initial boot

### 3. Connect to Your Raspberry Pi

If using phone hotspot (Option A):
```bash
# If your laptop supports mDNS (.local domains)
ssh pi@netguardian.local

# Or using the IP address you found
ssh pi@<pi-ip-address>
```

If using USB connection (Option B):

For macOS/Linux:
```bash
# The Pi should be automatically assigned an address
ssh pi@raspberrypi.local
```

For Windows:
1. Install Bonjour Print Services if not already installed
2. Open PowerShell and connect:
```bash
ssh pi@raspberrypi.local
```

If the .local address doesn't work:
- On Windows: The Pi should appear as a new Ethernet device with address 192.168.7.1
- On macOS/Linux: Use address 192.168.7.1
```bash
ssh pi@192.168.7.1
```

### 4. Install Net Guardian

Once connected via USB-SSH, run these commands:

```bash
# Update package list
sudo apt update

# Install Git and Bluetooth packages
sudo apt install -y git bluetooth bluez python3-pip python3-bluez

# Enable Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

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

4. Check Bluetooth status:
```bash
sudo bluetoothctl
power on
show
```
You should see your Bluetooth adapter information and status.

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

If Bluetooth isn't working:

1. Check Bluetooth service:
```bash
sudo systemctl status bluetooth
```

2. Reset Bluetooth:
```bash
sudo systemctl restart bluetooth
```

3. Check logs:
```bash
journalctl -u bluetooth
journalctl -u net-guardian
```

### Power Management Tips

- The Raspberry Pi Zero 2 W can be powered using a standard 5V/2.5A power bank
- Use a good quality power bank to avoid voltage drops
- The system draws approximately 120-150mA during normal operation
- A 10,000mAh power bank should provide roughly 2-3 days of operation
- BLE communication is more power-efficient than WiFi, extending battery life

### Bluetooth Configuration

To pair with the visualizer:

1. Enable Bluetooth discovery mode:
```bash
sudo bluetoothctl
discoverable on
pairable on
```

2. Note the Bluetooth address shown in:
```bash
show
```

3. Use this address when configuring the visualizer application

## Next Steps

Once installation is complete, proceed to [usage.md](usage.md) for instructions on using the Net Guardian system. 