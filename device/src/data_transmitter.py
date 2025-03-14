import json
import logging
from typing import Dict, Optional
from bluepy import btle
import time
from gps_reader import GPSReader

class BLEDataTransmitter:
    """Handles transmission of GPS data over Bluetooth Low Energy."""
    
    SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"  # Custom service UUID
    CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"     # Custom characteristic UUID
    
    def __init__(self, device_name: str = "NetGuardian"):
        """Initialize BLE transmitter with device name."""
        self.device_name = device_name
        self.peripheral = None
        self.characteristic = None
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def start_advertising(self):
        """Start BLE advertising."""
        try:
            self.peripheral = btle.Peripheral()
            self.peripheral.setAdvertisementData(
                localName=self.device_name,
                serviceUUIDs=[self.SERVICE_UUID]
            )
            self.characteristic = self.peripheral.getCharacteristics(uuid=self.CHAR_UUID)[0]
            self.logger.info(f"Started BLE advertising as {self.device_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start BLE advertising: {e}")
            return False
    
    def stop_advertising(self):
        """Stop BLE advertising and disconnect."""
        try:
            if self.peripheral:
                self.peripheral.disconnect()
                self.peripheral = None
                self.characteristic = None
            self.logger.info("Stopped BLE advertising")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping BLE advertising: {e}")
            return False
    
    def transmit_data(self, gps_data: Dict) -> bool:
        """Transmit GPS data over BLE."""
        if not self.peripheral or not self.characteristic:
            self.logger.error("BLE not initialized")
            return False
            
        try:
            # Convert GPS data to JSON string
            data_str = json.dumps(gps_data)
            
            # Split data into chunks if necessary (BLE has packet size limits)
            chunk_size = 20  # Standard BLE MTU size
            chunks = [data_str[i:i + chunk_size] for i in range(0, len(data_str), chunk_size)]
            
            # Send each chunk
            for chunk in chunks:
                self.characteristic.write(chunk.encode())
                time.sleep(0.1)  # Small delay between chunks
                
            self.logger.info("GPS data transmitted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to transmit GPS data: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if BLE is connected and ready."""
        return bool(self.peripheral and self.characteristic) 

if __name__ == "__main__":
    # Initialize components
    gps = GPSReader(update_interval=5)  # Update every 5 seconds
    transmitter = BLEDataTransmitter(device_name="NetGuardian")
    
    # Connect to GPS
    if not gps.connect():
        logging.error("Failed to connect to GPS. Exiting.")
        exit(1)
    
    # Start BLE advertising
    if not transmitter.start_advertising():
        logging.error("Failed to start BLE advertising. Exiting.")
        exit(1)
    
    logging.info("GPS Tracker started. Waiting for GPS fix...")
    
    try:
        while True:
            # Get GPS position
            position = gps.get_current_position()
            if position:
                # Transmit if we have a valid position
                transmitter.transmit_data(position)
            time.sleep(5)  # Wait before next update
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        transmitter.stop_advertising() 