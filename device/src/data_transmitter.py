import json
import logging
import subprocess
import time
from gps_reader import GPSReader

class BLEDataTransmitter:
    """Simple BLE transmitter that broadcasts GPS coordinates."""
    
    def __init__(self, device_name: str = "NetGuardian"):
        self.device_name = device_name
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _run_cmd(self, cmd: str) -> bool:
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            self.logger.error(f"Command failed: {cmd}")
            self.logger.error(f"Error: {e}")
            return False
    
    def start_advertising(self):
        """Start BLE advertising."""
        try:
            # Basic BLE setup
            cmds = [
                "sudo hciconfig hci0 up",
                f"sudo hciconfig hci0 name {self.device_name}",
                "sudo hciconfig hci0 leadv 3"  # Non-connectable advertising
            ]
            
            for cmd in cmds:
                if not self._run_cmd(cmd):
                    return False
                
            self.logger.info(f"Started BLE advertising as {self.device_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start advertising: {e}")
            return False
    
    def transmit_data(self, gps_data: dict) -> bool:
        """Broadcast GPS data as BLE advertising data."""
        try:
            # Format coordinates as compact string: "lat,lon"
            data = f"{gps_data['latitude']:.6f},{gps_data['longitude']:.6f}"
            
            # Convert to hex
            hex_data = ''.join([hex(ord(c))[2:].zfill(2) for c in data])
            
            # Set advertising data (max 31 bytes)
            cmd = f"sudo hcitool -i hci0 cmd 0x08 0x0008 {len(hex_data)//2 + 2} 02 01 06 {len(hex_data)//2} FF {hex_data}"
            if not self._run_cmd(cmd):
                return False
                
            self.logger.info(f"Broadcasting: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to transmit: {e}")
            return False
    
    def stop_advertising(self):
        """Stop BLE advertising."""
        try:
            self._run_cmd("sudo hciconfig hci0 noleadv")
            self.logger.info("Stopped advertising")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping: {e}")
            return False

if __name__ == "__main__":
    # Initialize components
    gps = GPSReader(update_interval=5)
    transmitter = BLEDataTransmitter()
    
    # Connect to GPS
    if not gps.connect():
        logging.error("Failed to connect to GPS. Exiting.")
        exit(1)
    
    # Start advertising
    if not transmitter.start_advertising():
        logging.error("Failed to start advertising. Exiting.")
        exit(1)
    
    logging.info("GPS Tracker started. Waiting for GPS fix...")
    
    try:
        while True:
            position = gps.get_current_position()
            if position:
                transmitter.transmit_data(position)
            time.sleep(5)
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        transmitter.stop_advertising() 