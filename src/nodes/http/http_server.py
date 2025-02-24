import os
import json
import cv2
from http.server import HTTPServer, BaseHTTPRequestHandler
from qtpy.QtWidgets import QLineEdit, QPushButton, QTextEdit
from qtpy.QtCore import QThread, Signal
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_HTTP_SERVER  # Bu sabiti projenize uygun tanımlayın
import numpy as np
from src.nodes.css.cv_css import CV2_CSS
###########################################################################
# Senkron HTTP Request Handler (http.server kullanılarak)
###########################################################################
class SyncHttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
        
    def do_POST(self):
        self.handle_request()
        
    def handle_request(self):
        try:
            # HTTPServer örneğinde atanan get_data callback çağrılıyor.
            data = self.server.get_data()
            # Gelen veri tipine göre yanıt içeriği ve Content-Type belirleniyor
            if isinstance(data, (dict, list)):
                body = json.dumps(data)
                content_type = "application/json"
            elif isinstance(data, bytes):
                body = data
                content_type = "application/octet-stream"
            else:
                body = str(data)
                content_type = "text/plain"
            if not isinstance(body, bytes):
                body = body.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        # Varsayılan loglamayı kapatıyoruz (isterseniz buraya loglama ekleyebilirsiniz)
        pass

###########################################################################
# QThread içerisinde senkron HTTP Server çalıştıran sınıf
###########################################################################
class HttpServerThread(QThread):
    log_signal = Signal(str)
    
    def __init__(self, port, get_data_callback, parent=None):
        super().__init__(parent)
        self.port = port
        self.get_data = get_data_callback
        self.httpd = None
        
    def run(self):
        try:
            self.httpd = HTTPServer(('localhost', self.port), SyncHttpRequestHandler)
            # RequestHandler içinden erişilebilmesi için callback’i sunucu örneğine atıyoruz
            self.httpd.get_data = self.get_data
            self.log_signal.emit(f"HTTP Server {self.port} portunda başlatıldı.")
            self.httpd.serve_forever()
        except Exception as e:
            self.log_signal.emit(f"HTTP Server hatası: {e}")
    
    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.log_signal.emit("HTTP Server durduruldu.")
        self.quit()

###########################################################################
# Node İçerik: Arayüz elemanlarını oluşturur (port, buton, log ekranı)
###########################################################################
class HttpServerContent(Content):
    def initUI(self):
        super().initUI()
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.port_edit = QLineEdit(self)
        self.port_edit.setPlaceholderText("Port (örn: 8080)")
        
        self.start_button = QPushButton("Server Başlat", self)
        
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        
        self.layout.addWidget(self.port_edit)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.log_display)
        self.setStyleSheet(CV2_CSS)
        self.setLayout(self.layout)
    
    def serialize(self):
        res = super().serialize()
        res['port'] = self.port_edit.text()
        res['log'] = self.log_display.toPlainText()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.port_edit.setText(data.get('port', ''))
            self.log_display.setPlainText(data.get('log', ''))
        except Exception as e:
            dumpException(e)
        return res

###########################################################################
# HTTP Server Node: Gelen veriyi depolar ve HTTP isteklerine cevap verir
###########################################################################
@register_node(NODE_HTTP_SERVER)
class HttpServerNode(Node):
    op_code = NODE_HTTP_SERVER
    op_title = "HTTP Server Node (Sync)"
    content_label_objname = "http_server"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    width = 350
    height = 200

    def __init__(self, scene, parent=None):
        super().__init__(scene)
        # Çıkış soketi; diğer nodelara veri aktarımı için (opsiyonel)
        self.addInput("Data")
        self.addOutput("Çıktı")
        self.create()
        self.server_thread = None
        self.current_data = None  # Güncel veri, diğer nodelardan gelen verilerle güncellenebilir

    def initInnerClasses(self):
        self.content = HttpServerContent(self)
        self.grNode = Graphics(self)
        self.content.start_button.clicked.connect(self.toggleServer)

    def toggleServer(self):
        if self.server_thread and self.server_thread.isRunning():
            self.stopServer()
            self.content.start_button.setText("Server Başlat")
        else:
            try:
                port = int(self.content.port_edit.text())
            except ValueError:
                self.content.log_display.append("Geçersiz port numarası.")
                return
            self.startServer(port)
            self.content.start_button.setText("Server Durdur")

    def startServer(self, port):
        if self.server_thread and self.server_thread.isRunning():
            self.content.log_display.append("Server zaten çalışıyor.")
            return
        self.server_thread = HttpServerThread(port, self.getData)
        self.server_thread.log_signal.connect(self.appendLog)
        self.server_thread.start()
        self.content.log_display.append(f"Server {port} portunda başlatıldı.")

    def stopServer(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread = None
            self.content.log_display.append("Server durduruldu.")

    def appendLog(self, text):
        self.content.log_display.append(text)

    def getData(self):
        """
        HTTP isteği geldiğinde, bu metod çağrılarak node içerisindeki güncel veriyi döndürür.
        Veri; dict, byte, list veya str olabilir. Eğer veri yoksa varsayılan mesaj döner.
        """
        return self.current_data if self.current_data is not None else "No Data"

    def evalImplementation(self, name=None, data=None):
        """
        Bağlı düğümlerden veri aldığında, node içerisindeki veriyi günceller, log ekranında gösterir
        ve çıkış soketi üzerinden veri aktarır.
        """
        if data is not None:
            if isinstance(data, np.ndarray): 
                success, encoded_image = cv2.imencode('.png', data)
                if success:
                    self.current_data = encoded_image.tobytes() 
                #self.content.log_display.append(f"Gelen veri: {data}")
            else:
                self.current_data =  data
        self.sendData("Çıktı", data)
