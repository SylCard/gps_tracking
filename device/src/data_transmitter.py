import json
import logging
from typing import Dict, Optional
import subprocess
import time
from gps_reader import GPSReader

class BLEDataTransmitter:
    """Handles transmission of GPS data over Bluetooth Low Energy."""
    
    # Custom service and characteristic UUIDs
    SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
    CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    
    def __init__(self, device_name: str = "NetGuardian"):
        """Initialize BLE transmitter with device name."""
        self.device_name = device_name
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _run_cmd(self, cmd: str) -> bool:
        """Run a shell command and return success status."""
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {cmd}")
            self.logger.error(f"Error: {e}")
            return False
    
    def start_advertising(self):
        """Start BLE advertising."""
        try:
            # Reset bluetooth interface
            cmds = [
                "sudo hciconfig hci0 down",
                "sudo hciconfig hci0 up",
                f"sudo hciconfig hci0 name {self.device_name}",
                "sudo hciconfig hci0 piscan",
                "sudo hciconfig hci0 sspmode 1",
                # Set up advertising with our service UUID
                f"sudo hcitool -i hci0 cmd 0x08 0x0008 1b 02 01 06 11 07 {self.SERVICE_UUID.replace('-', '')} 00"
            ]
            
            for cmd in cmds:
                if not self._run_cmd(cmd):
                    return False
                
            self.logger.info(f"Started BLE advertising as {self.device_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start BLE advertising: {e}")
            return False
    
    def stop_advertising(self):
        """Stop BLE advertising."""
        try:
            self._run_cmd("sudo hciconfig hci0 noleadv")
            self.logger.info("Stopped BLE advertising")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping BLE advertising: {e}")
            return False
    
    def _chunk_data(self, data: str, chunk_size: int = 20) -> list:
        """Split data into BLE-sized chunks."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    def transmit_data(self, gps_data: Dict) -> bool:
        """Transmit GPS data over BLE."""
        try:
            # Convert GPS data to JSON string
            data_str = json.dumps(gps_data)
            
            # Split into chunks
            chunks = self._chunk_data(data_str)
            
            # Send each chunk using characteristic write command
            for i, chunk in enumerate(chunks):
                chunk_hex = ''.join([hex(ord(c))[2:].zfill(2) for c in chunk])
                cmd = f"sudo gatttool -i hci0 --char-write-req --handle=0x000b --value={chunk_hex}"
                if not self._run_cmd(cmd):
                    return False
                time.sleep(0.1)  # Small delay between chunks
                
            self.logger.info(f"Transmitted GPS data: {data_str}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to transmit GPS data: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if BLE is advertising."""
        try:
            result = subprocess.run("hciconfig hci0", shell=True, capture_output=True, text=True)
            return "UP RUNNING" in result.stdout
        except:
            return False

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
                # Transmit GPS data
                transmitter.transmit_data(position)
            time.sleep(5)  # Wait before next update
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        transmitter.stop_advertising() 