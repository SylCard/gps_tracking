import asyncio
import signal
import sys
import logging
from ble_receiver import BLEReceiver
import time

class GPSVisualizer:
    def __init__(self):
        """Initialize the GPS visualizer application."""
        self._setup_logging()
        self.ble_receiver = BLEReceiver(self.handle_gps_data)
        self.running = False
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_gps_data(self, gps_data):
        """Handle received GPS data."""
        lat = gps_data.get('latitude')
        lon = gps_data.get('longitude')
        print(f"\nReceived GPS coordinates: {lat}, {lon}")
    
    async def run(self):
        """Run the GPS visualizer."""
        try:
            print("Scanning for GPS tracker (will try for 5 minutes)...")
            start_time = time.time()
            timeout = 300  # 5 minutes in seconds
            
            while time.time() - start_time < timeout:
                if await self.ble_receiver.scan_for_device():
                    print("Found GPS tracker, connecting...")
                    if await self.ble_receiver.connect_and_listen():
                        print("Connected! Receiving GPS data...")
                        print("Press Ctrl+C to stop")
                        self.running = True
                        while self.running:
                            await asyncio.sleep(1)
                        break
                    else:
                        print("Failed to connect, retrying...")
                else:
                    remaining = int(timeout - (time.time() - start_time))
                    print(f"No GPS tracker found. Retrying... ({remaining} seconds remaining)")
                    await asyncio.sleep(5)  # Wait 5 seconds before retrying
            
            if not self.running:
                print("\nTimeout: No GPS tracker found after 5 minutes")
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            if self.running:
                await self.ble_receiver.disconnect()
            print("Disconnected")

def main():
    """Main entry point."""
    visualizer = GPSVisualizer()
    asyncio.run(visualizer.run())
    
if __name__ == "__main__":
    main() 