import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import urllib.parse
from urllib.parse import urlparse, parse_qs
import json

class ProxyHandler(BaseHTTPRequestHandler):
    
    TARGET_DOMAIN = os.getenv("TARGET_DOMAIN", default="")
    
    def do_GET(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            if not self.path.startswith('/api'):
                self.send_error(403, f"Forbidden")
                return
            
            target_url = f"https://{self.TARGET_DOMAIN}{self.path}"
            
            headers = {
                'Host': self.TARGET_DOMAIN,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'x-vercel-protection-bypass': os.getenv("VERCEL_PROTECTION_BYPASS_TOKEN", default="")
            }
            
            body = None
            
            print(f"Request: {self.command} {target_url}")
            
            response = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            print(f"Response: {response.status_code}")
            
            self.send_response(200 if response.status_code == 200 else response.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if response.content:
                self.wfile.write(response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"Requset Error: {str(e)}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Gateway Error"}')
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Error"}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{self.date_time_string()}] {self.address_string()} - {format % args}")

def run_proxy_server(host='localhost', port=8080):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    print(f"Starting API Gateway: http://{host}:{port}")
    print(f"Target: https://{ProxyHandler.TARGET_DOMAIN}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Gateway...")
        httpd.server_close()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 8080
    
    run_proxy_server(HOST, PORT)
