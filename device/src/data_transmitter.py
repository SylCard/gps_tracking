import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import gpsd
from gps_reader import GPSReader

class GPSDataHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that serves the latest GPS coordinates and satellite data."""
    
    # Latest position data (shared between threads)
    current_position = None
    
    def get_satellite_data(self):
        """Get current satellite data."""
        try:
            packet = gpsd.get_current()
            sky = packet.get_sky()  # Get sky view with satellite data
            
            sats = []
            if sky and hasattr(sky, 'satellites'):
                for sat in sky.satellites:
                    sats.append({
                        'PRN': sat.PRN,
                        'elevation': sat.elevation,
                        'azimuth': sat.azimuth,
                        'SNR': sat.ss if hasattr(sat, 'ss') else 0,
                        'used': sat.used
                    })
            
            return {
                'total_sats': len(sats),
                'used_sats': sum(1 for sat in sats if sat['used']),
                'satellites': sats,
                'fix_status': packet.mode if hasattr(packet, 'mode') else 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_sats': 0,
                'used_sats': 0,
                'satellites': [],
                'fix_status': 0
            }
    
    def do_GET(self):
        """Serve GPS and satellite data as JSON."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Get both position and satellite data
        sat_data = self.get_satellite_data()
        fix_status = sat_data['fix_status']
        
        response = {
            'position': self.current_position if self.current_position else None,
            'satellite_data': sat_data,
            'fix_description': {
                0: 'No data',
                1: 'No fix',
                2: '2D fix',
                3: '3D fix'
            }[fix_status],  # Just return the current status
            'timestamp': gpsd.get_current().get_time() if hasattr(gpsd.get_current(), 'get_time') else None
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

class GPSTransmitter:
    """Simple HTTP server that serves GPS coordinates and satellite data."""
    
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.server = None
        self.server_thread = None
    
    def start_server(self):
        """Start HTTP server in a background thread."""
        try:
            self.server = HTTPServer((self.host, self.port), GPSDataHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.logger.info(f"Server started at http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def update_position(self, position: dict):
        """Update the current position data."""
        GPSDataHandler.current_position = position
        self.logger.info(f"Position updated: {position}")
    
    def stop_server(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info("Server stopped")

if __name__ == "__main__":
    # Initialize components
    gps = GPSReader(update_interval=5)
    transmitter = GPSTransmitter(port=8000)
    
    # Connect to GPS
    if not gps.connect():
        logging.error("Failed to connect to GPS. Exiting.")
        exit(1)
    
    # Start server
    if not transmitter.start_server():
        logging.error("Failed to start server. Exiting.")
        exit(1)
    
    logging.info("GPS Tracker started. Waiting for GPS fix...")
    
    try:
        while True:
            position = gps.get_current_position()
            if position:
                transmitter.update_position(position)
            threading.Event().wait(5)  # Sleep without blocking shutdown
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        transmitter.stop_server() 