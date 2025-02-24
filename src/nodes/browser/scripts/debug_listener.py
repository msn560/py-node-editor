import json
import requests
import websocket
from threading import Event
from urllib.parse import urlparse
from PyQt5.QtCore import QThread, pyqtSignal

class WebSocketThread(QThread):
    finished = pyqtSignal()
    data_updated = pyqtSignal(dict)  # Optional: For real-time updates

    def __init__(self, parent=None,debug_host="127.0.0.1" , debug_port=1250, exclude=None):
        super().__init__( )
        self.parent = parent
        self.debug_url = f"http://{debug_host}:{debug_port}/"
        self.stop_event = Event()
        self.exclude = exclude or ["data:", ".ico", ".js", ".css", ".png", ".jpg", ".mp3", ".woff"]
        self.data = {}
        self.ws = None

    def run(self):
        """Main thread execution"""
        self.get_tab_id()
        
        if not self.webSocketDebuggerUrl:
            print("No WebSocket URL found")
            self.finished.emit()
            return

        try:
            self.ws = websocket.create_connection(
                self.webSocketDebuggerUrl,
                timeout=1  # Allows periodic stop checks
            )
            print("WebSocket connection established!")
            self.ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
            
            while not self.stop_event.is_set():
                try:
                    msg = self.ws.recv()
                    self.process_message(msg)
                    
                except websocket.WebSocketTimeoutException:
                    continue  # Timeout for stop check
                except websocket.WebSocketConnectionClosedException:
                    print("Connection closed by server")
                    break
                except Exception as e:
                    print(f"WebSocket error: {str(e)}")
                    break

        except Exception as e:
            print(f"Connection failed: {str(e)}")
        finally:
            self.cleanup()
            self.finished.emit()

    def process_message(self, msg):
        """Process incoming WebSocket messages"""
        data = json.loads(msg)
        if data.get("method") == "Network.responseReceived":
            response = data.get("params", {}).get("response", {})
            url = response.get("url", "")
            
            if any(ex in url for ex in self.exclude):
                return

            parsed_url = urlparse(self.parent.url)
            domain = parsed_url.netloc
            
            new_data = {
                "url": url,
                "status": response.get("status"),
                "response_headers": response.get("headers", {}),
                "requestHeaders": response.get("requestHeaders", {})
            }
            
            self.data.setdefault(domain, []).append(new_data)
            # Optional: Emit update signal
            self.data_updated.emit(self.data)

    def get_tab_id(self):
        """Fetch WebSocket debug URL"""
        try:
            response = requests.get(f"{self.debug_url}json/list")
            tabs = response.json()
            if tabs and "webSocketDebuggerUrl" in tabs[0]:
                self.webSocketDebuggerUrl = tabs[0]["webSocketDebuggerUrl"]
        except Exception as e:
            print(f"Failed to get tab ID: {str(e)}")

    def stop(self):
        """Graceful thread shutdown"""
        print("🛑 Stopping WebSocket thread...")
        self.stop_event.set()
        # Force close connection if still open
        if self.ws and self.ws.connected:
            self.ws.close()

    def cleanup(self):
        """Ensure resources are released"""
        print("⛔ WebSocket loop stopped!")
        if self.ws:
            self.ws.close()

class BrowserDebugListen:
    def __init__(self, parent=None):
        self.parent = parent
        self.thread = WebSocketThread(parent=parent)
        self.thread.finished.connect(self.on_thread_finished)

    def start(self):
        """Start the WebSocket thread"""
        self.thread.start()

    def stop(self):
        """Stop the WebSocket thread"""
        self.thread.stop()

    def on_thread_finished(self):
        """Handle thread completion"""
        print("WebSocket thread finished")
        # Access collected data through self.thread.data
        # Optional: Add cleanup logic here

    def set_exclude(self, exclude_list):
        """Update exclusion list"""
        self.thread.exclude = exclude_list

    def get_data(self):
        """Get collected data"""
        return self.thread.data
    

"""
Usage example:


# In your main window/QObject
def __init__(self):
    self.debug_listener = BrowserDebugListen(self)
    # Optional: Connect to data updates
    self.debug_listener.thread.data_updated.connect(self.handle_data_update)

def start_listening(self):
    self.debug_listener.start()

def stop_listening(self):
    self.debug_listener.stop()

def handle_data_update(self, data):
    # Update UI with new data
    print("New data received:", data)

"""