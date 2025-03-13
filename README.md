# Net Guardian

A Raspberry Pi-based GPS tracking system for monitoring ghost fishing nets.

## Overview

Net Guardian is a two-part system consisting of:
- A Raspberry Pi device that collects and transmits GPS coordinates
- A laptop visualization application that displays the tracking data on an interactive map

## Features

Device:
- Real-time GPS tracking using VK-162 USB GPS dongle
- Automatic data transmission over WiFi/network
- Local storage during connection loss
- Adjustable transmission frequency
- Auto-starts on boot

Visualizer:
- Real-time position display on interactive map
- Historical path tracking with timestamps
- Visual indicators for live/estimated positions
- Data export to CSV/JSON

## Quick Start

For detailed setup instructions, especially for first-time Raspberry Pi users, see:
[Installation Guide](docs/installation.md)

### Basic Setup Steps

### Device Setup (Raspberry Pi)
1. Clone this repository
2. Navigate to the device directory
3. Run the setup script:
   ```bash
   cd device
   chmod +x setup.sh
   ./setup.sh
   ```

### Visualizer Setup (Laptop)
1. Navigate to the visualizer directory
2. Install requirements:
   ```bash
   cd visualizer
   pip install -r requirements.txt
   ```
3. Run the visualizer:
   ```bash
   python src/main.py
   ```

## Documentation

See the [docs](docs/) directory for detailed installation and usage instructions.

## License

MIT License