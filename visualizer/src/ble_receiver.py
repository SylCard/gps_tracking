import json
import logging
from typing import Dict, Optional, Callable
from bleak import BleakScanner, BleakClient
import asyncio

class BLEReceiver:
    """Handles receiving GPS data over Bluetooth Low Energy."""
    
    SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"  # Match transmitter
    CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"     # Match transmitter
    
    def __init__(self, data_callback: Callable[[Dict], None]):
        """Initialize BLE receiver with callback for received data."""
        self.data_callback = data_callback
        self.client = None
        self.device = None
        self.chunks = []
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def scan_for_device(self, device_name: str = "NetGuardian") -> bool:
        """Scan for BLE device with given name."""
        try:
            self.logger.info(f"Scanning for device: {device_name}")
            devices = await BleakScanner.discover()
            for d in devices:
                if d.name and device_name in d.name:
                    self.device = d
                    self.logger.info(f"Found device: {d.name} ({d.address})")
                    return True
            self.logger.error(f"Device {device_name} not found")
            return False
        except Exception as e:
            self.logger.error(f"Error scanning for devices: {e}")
            return False
    
    def notification_handler(self, _, data: bytearray):
        """Handle incoming BLE notifications."""
        try:
            # Decode chunk
            chunk = data.decode()
            
            # Add to chunks list
            self.chunks.append(chunk)
            
            # Check if this is the end of the message (less than max chunk size)
            if len(chunk) < 20:
                # Combine chunks and parse JSON
                full_data = ''.join(self.chunks)
                gps_data = json.loads(full_data)
                
                # Clear chunks for next message
                self.chunks = []
                
                # Call callback with parsed data
                self.data_callback(gps_data)
        except Exception as e:
            self.logger.error(f"Error processing notification: {e}")
            self.chunks = []
    
    async def connect_and_listen(self) -> bool:
        """Connect to device and start listening for data."""
        if not self.device:
            self.logger.error("No device found. Run scan_for_device first.")
            return False
            
        try:
            self.client = BleakClient(self.device)
            await self.client.connect()
            self.logger.info(f"Connected to {self.device.name}")
            
            # Subscribe to notifications
            await self.client.start_notify(
                self.CHAR_UUID,
                self.notification_handler
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to device: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from BLE device."""
        if self.client:
            await self.client.disconnect()
            self.logger.info("Disconnected from device")
            self.client = None 