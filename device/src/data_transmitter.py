import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import subprocess
from gps_reader import GPSReader

class GPSDataHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that serves GPS data."""
    
    def do_GET(self):
        """Serve GPS data as JSON."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Get TPV (Time-Position-Velocity) data
            tpv = subprocess.run(['gpspipe', '-w', '-n', '1'], capture_output=True, text=True, timeout=2)
            # Get satellite data
            sky = subprocess.run(['gpspipe', '-w', '-n', '2'], capture_output=True, text=True, timeout=2)
            
            response = {
                'gps_data': tpv.stdout,
                'satellite_data': sky.stdout,
                'raw_gpsd': subprocess.run(['ps', 'aux', '|', 'grep', 'gpsd'], capture_output=True, text=True).stdout
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'gps_data': None,
                'satellite_data': None
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