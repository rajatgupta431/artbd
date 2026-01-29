#!/usr/bin/env python3
"""
Digital Art Board Server
A self-contained server that serves embedded art board files in a browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import tempfile
import shutil
import atexit

# Configuration
PORT = 8080
HOST = "127.0.0.1"

# Global temp directory reference for cleanup
_temp_dir = None

def get_bundled_files_path():
    """Get the path to bundled static files."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - files are in _MEIPASS
        base_path = sys._MEIPASS
        bundled_path = os.path.join(base_path, 'static_files')
        if os.path.isdir(bundled_path):
            return bundled_path
        return base_path
    else:
        # Running as script - look for build folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for folder in ['build', 'dist', 'public', 'www', 'out', 'static', 'static_files']:
            path = os.path.join(script_dir, folder)
            if os.path.isdir(path):
                return path
        return script_dir

def extract_to_temp():
    """Extract bundled files to a temp directory for serving."""
    global _temp_dir
    
    bundled_path = get_bundled_files_path()
    
    # If not frozen, just return the path directly
    if not getattr(sys, 'frozen', False):
        return bundled_path
    
    # Create temp directory and copy files
    _temp_dir = tempfile.mkdtemp(prefix='artboard_')
    
    # Copy all files from bundled path to temp
    for item in os.listdir(bundled_path):
        src = os.path.join(bundled_path, item)
        dst = os.path.join(_temp_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    
    return _temp_dir

def cleanup_temp():
    """Clean up temp directory on exit."""
    global _temp_dir
    if _temp_dir and os.path.exists(_temp_dir):
        try:
            shutil.rmtree(_temp_dir)
        except:
            pass

def open_browser_delayed(url, delay=1.0):
    """Open browser after a short delay to ensure server is ready."""
    def open_browser():
        import time
        time.sleep(delay)
        webbrowser.open(url)
    
    thread = threading.Thread(target=open_browser)
    thread.daemon = True
    thread.start()

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with quieter logging and proper MIME types."""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        pass
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def guess_type(self, path):
        """Extended MIME type support."""
        base, ext = os.path.splitext(path)
        ext = ext.lower()
        
        mime_types = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.mjs': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.webp': 'image/webp',
            '.wasm': 'application/wasm',
        }
        
        return mime_types.get(ext, super().guess_type(path))

def main():
    # Register cleanup
    atexit.register(cleanup_temp)
    
    # Get/extract files
    serve_path = extract_to_temp()
    
    print("=" * 50)
    print("  Digital Art Board Server")
    print("=" * 50)
    print(f"\n  Server running at: http://{HOST}:{PORT}")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Change to serve directory
    os.chdir(serve_path)
    
    try:
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=serve_path, **kwargs)
        
        with socketserver.TCPServer((HOST, PORT), handler) as httpd:
            httpd.allow_reuse_address = True
            
            url = f"http://{HOST}:{PORT}"
            open_browser_delayed(url)
            
            print(f"\n  Browser opening to {url}...")
            print("  (If it doesn't open, manually navigate to the URL above)\n")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n  Server stopped.")
    except OSError as e:
        if "Address already in use" in str(e) or getattr(e, 'errno', 0) == 10048:
            print(f"\n  Error: Port {PORT} is already in use.")
            print(f"  Try closing other applications using this port.")
        else:
            print(f"\n  Error: {e}")
        input("\n  Press Enter to exit...")

if __name__ == "__main__":
    main()
