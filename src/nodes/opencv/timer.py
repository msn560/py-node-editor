import os
from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout
from qtpy.QtCore import Qt, QTimer
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_TIMER
from  src.node_editor.numeric_text_line import NumericLineEdit
import time
from src.nodes.css.cv_css import CV2_CSS
class TimerContent(Content):
    fps = 0
    last_time = 0
    last_count = 0
    def initUI(self):
        super().initUI() 
        
        self.mslinetext = NumericLineEdit(self)
        # Status Label
        self.status_label = QLabel("Pasif", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("timer_status") 
        self.status_label.setProperty("class", "inactive")

        # FPS Label
        self.fps_label = QLabel("FPS : 0", self)
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setObjectName("timer_fps")  

        # Toggle Button
        self.toggle_btn = QPushButton("Başlat/Durdur", self)
        self.toggle_btn.setObjectName("timer_button")
        self.toggle_btn.clicked.connect(self.toggle_timer)

        # Timer Setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timeout)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.mslinetext)
        self.layout.addLayout(layout)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.layout.addLayout(layout)
        layout = QVBoxLayout()
        layout.addWidget(self.fps_label)
        self.layout.addLayout(layout)
        layout = QVBoxLayout()
        layout.addWidget(self.toggle_btn) 
        self.layout.addLayout(layout)
        self.setStyleSheet(CV2_CSS) 

    def toggle_timer(self):
        """Timer durumunu değiştir"""
        if self.timer.isActive():
            self.timer.stop()
            self.status_label.setText("Pasif")
            self.status_label.setProperty("class", "inactive")
            self.fps_label.setText("FPS : {}".format(str(self.fps)))
        else:
            _ms = self.mslinetext.getInt(default=30 , _min=10) 
            self.mslinetext.setText(_ms)
            self.timer.start(_ms)  
            self.status_label.setText("Aktif")
            self.status_label.setProperty("class", "active")
        
        # CSS güncelleme
        self.status_label.style().polish(self.status_label)
        self.node.sendSignal()

    def on_timeout(self):
        """
        Timer tetiklendiğinde sinyal gönder 
        fps = 0
        last_time = 0
        last_count = 0
        """
        
        if (time.time() - self.last_time ) > 1:
            self.last_time = time.time()
            self.fps = self.last_count 
            self.last_count = 1 
            self.fps_label.setText("FPS : {}".format(str(self.fps)))
        else:
            self.last_count += 1 
        

        self.node.sendSignal()

    def serialize(self):
        res = super().serialize()
        res['interval'] = self.timer.interval()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        self.timer.setInterval(data.get('interval', 1000))
        return res

@register_node(NODE_TIMER)
class TimerNode(Node):
    op_code = NODE_TIMER
    op_title = "Zamanlayıcı"
    content_label_objname = "timer_node"
    category =  os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, scene ,parent = None):
        self.parent = parent
        super().__init__(scene)
        self.addOutput("Çıkış")
        self.create()

    def initInnerClasses(self):
        self.content = TimerContent(self)
        self.grNode = Graphics(self)

    def sendSignal(self):
        """Sinyal gönder"""
        self.sendData("Çıkış", True)

    def evalImplementation(self, name=None, data=None):
        pass  # Harici tetikleme gerekmiyor
 