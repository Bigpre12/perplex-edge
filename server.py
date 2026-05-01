import http.server
import socketserver
import urllib.parse
import os

PORT = 12345
LOG_FILE = "server_log.txt"

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        chunk_id = self.headers.get('X-Chunk-ID', 'default')
        file_path = f"stitch_code_{chunk_id}.txt"
        
        with open(file_path, 'wb') as f:
            f.write(post_data)
            
        with open(LOG_FILE, 'a') as f:
            f.write(f"POST received: {len(post_data)} bytes saved to {file_path}\n")
            
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b"Success")

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        with open(LOG_FILE, 'a') as f:
            f.write(f"GET received: {self.path}\n")
            
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b"OK")

with socketserver.TCPServer(("127.0.0.1", PORT), MyHandler) as httpd:
    with open(LOG_FILE, 'a') as f:
        f.write(f"Server started on {PORT}\n")
    httpd.serve_forever()
