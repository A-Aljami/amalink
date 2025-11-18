from http.server import BaseHTTPRequestHandler
import yt_dlp
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            url = data.get('url')
            
            if not url:
                self._send_error(400, 'URL required')
                return
            
            print(f'📥 Processing: {url}')
            
            # yt-dlp options
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                video_url = info.get('url')
                thumbnail = info.get('thumbnail')
                title = info.get('title', 'video')
                
                if not video_url:
                    raise ValueError('Unable to extract video URL')
                
                result = {
                    'downloadUrl': video_url,
                    'thumbnail': thumbnail,
                    'type': 'video',
                    'quality': 'HD',
                    'platform': 'social_media',
                    'title': title
                }
                
                print('✅ Success!')
                self._send_json(200, result)
                
        except Exception as e:
            error_msg = str(e)
            print(f'❌ Error: {error_msg}')
            self._send_error(500, error_msg)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
