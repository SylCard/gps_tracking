import gpsd
import time
from typing import Optional, Dict
import logging

class GPSReader:
    def __init__(self, update_interval: int = 5):
        """Initialize GPS reader with specified update interval in seconds."""
        self.update_interval = update_interval
        self.last_position = None
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to the GPS daemon."""
        try:
            gpsd.connect()
            self.logger.info("Connected to GPSD successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to GPSD: {e}")
            return False
            
    def get_current_position(self) -> Optional[Dict]:
        """Get current GPS position."""
        try:
            packet = gpsd.get_current()
            if packet.mode >= 2:  # 2D or 3D fix
                position = {
                    'latitude': packet.lat,
                    'longitude': packet.lon,
                    'timestamp': time.time(),
                    'speed': packet.speed() if packet.speed() else 0,
                    'track': packet.track() if packet.track() else 0,
                }
                self.last_position = position
                return position
            return None
        except Exception as e:
            self.logger.error(f"Error reading GPS data: {e}")
            return None 