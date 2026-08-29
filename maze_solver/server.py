"""
Localhost Web Server for A* Maze Solver.
Runs entirely on your local machine at http://localhost:5000 (private to your computer).
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

PORT = 5000
WEB_DIR = Path(__file__).parent / "web"

class LocalhostHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        # Clean local request logs
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server():
    os.chdir(WEB_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("127.0.0.1", PORT), LocalhostHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 60)
        print(f">> A* Maze Solver is running LOCALLY at: {url}")
        print(">> Note: This is 100% PRIVATE to your computer (127.0.0.1).")
        print(">> Nobody else on the internet can see or access it.")
        print(">> Press Ctrl+C anytime in the terminal to stop the server.")
        print("=" * 60)
        
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down localhost server...")
            httpd.server_close()
            sys.exit(0)

if __name__ == "__main__":
    run_server()
