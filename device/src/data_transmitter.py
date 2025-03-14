import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import subprocess
import time
import re

class GPSDataHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that serves GPS data."""
    
    def do_GET(self):
        """Serve GPS data as JSON."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Get raw satellite data
            sky_data = subprocess.run(['gpspipe', '-w', '-n', '10'], capture_output=True, text=True, timeout=3)
            
            # Extract SKY data which contains satellite info
            sky_json = None
            for line in sky_data.stdout.splitlines():
                if '"class":"SKY"' in line:
                    sky_json = json.loads(line)
                    break
            
            # Extract TPV data which contains position info
            tpv_json = None
            for line in sky_data.stdout.splitlines():
                if '"class":"TPV"' in line:
                    tpv_json = json.loads(line)
                    break
            
            # Get device info
            device_info = subprocess.run(['gpspipe', '-w', '-n', '5'], capture_output=True, text=True, timeout=2)
            device_json = None
            for line in device_info.stdout.splitlines():
                if '"class":"DEVICE"' in line or '"class":"DEVICES"' in line:
                    device_json = json.loads(line)
                    break
            
            # Run cgps to get a formatted display
            cgps_output = subprocess.run(['cgps', '-s'], capture_output=True, text=True, timeout=1)
            
            # Format satellite data for display
            satellites = []
            if sky_json and 'satellites' in sky_json:
                for sat in sky_json['satellites']:
                    satellites.append({
                        'PRN': sat.get('PRN', 'N/A'),
                        'Elevation': sat.get('el', 'N/A'),
                        'Azimuth': sat.get('az', 'N/A'),
                        'SNR': sat.get('ss', 'N/A'),
                        'Used': sat.get('used', False)
                    })
            
            # Get fix status
            fix_status = "NO FIX"
            if tpv_json and 'mode' in tpv_json:
                mode = tpv_json['mode']
                if mode == 1:
                    fix_status = "NO FIX"
                elif mode == 2:
                    fix_status = "2D FIX"
                elif mode == 3:
                    fix_status = "3D FIX"
            
            # Extract position if available
            position = None
            if tpv_json and 'lat' in tpv_json and 'lon' in tpv_json:
                position = {
                    'latitude': tpv_json.get('lat', 'N/A'),
                    'longitude': tpv_json.get('lon', 'N/A'),
                    'altitude': tpv_json.get('alt', 'N/A'),
                    'speed': tpv_json.get('speed', 'N/A'),
                    'track': tpv_json.get('track', 'N/A')
                }
            
            # Extract visible satellites count
            visible_sats = len(satellites) if satellites else 0
            used_sats = sum(1 for sat in satellites if sat['Used'])
            
            # Create a nicely formatted response
            response = {
                'gps_status': {
                    'fix_status': fix_status,
                    'visible_satellites': visible_sats,
                    'used_satellites': used_sats,
                    'device_type': device_json['devices'][0]['driver'] if device_json and 'devices' in device_json and len(device_json['devices']) > 0 else 'Unknown',
                    'device_path': device_json['devices'][0]['path'] if device_json and 'devices' in device_json and len(device_json['devices']) > 0 else 'Unknown'
                },
                'position': position,
                'satellites': satellites,
                'raw_display': cgps_output.stdout,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'gps_status': 'Error retrieving GPS data',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass

class GPSTransmitter:
    """Simple HTTP server that serves GPS data."""
    
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
    
    def stop_server(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info("Server stopped")

if __name__ == "__main__":
    transmitter = GPSTransmitter(port=8000)
    
    # Start server
    if not transmitter.start_server():
        logging.error("Failed to start server. Exiting.")
        exit(1)
    
    logging.info("GPS data server started...")
    
    try:
        # Keep main thread alive
        while True:
            threading.Event().wait(5)
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        transmitter.stop_server() 