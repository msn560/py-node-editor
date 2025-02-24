import os
from qtpy.QtWidgets import QLineEdit ,QLabel,QVBoxLayout,QPushButton 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_CV2_CAM_SENDER 

import cv2
from qtpy.QtGui import QImage
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QTimer, QCoreApplication,QSize 
from src.nodes.css.cv_css import CV2_CSS
 
class cv2CamContent(Content):
    img = None
    def initUI(self):
        super().initUI()    
        self.status_label = QLabel("Pasif", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("status_label" ) 
        self.status_label.setProperty("class", "inactive")
        
        self.toggle_btn = QPushButton("Başlat/Durdur", self)
        self.toggle_btn.setObjectName("cam_button")
        self.toggle_btn.clicked.connect(self.toggle_cam)
        
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.layout.addLayout(layout)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toggle_btn)
        self.setStyleSheet(CV2_CSS) 
        self.layout.addLayout(layout)
 

         
    def toggle_cam(self):
        if self.node.cap is  None: 
            self.status_label.setText("Aktif")
            self.node.camStart()
            self.status_label.setProperty("class", "active")
        else:
            self.status_label.setText("Pasif")
            self.node.camStop()
            self.status_label.setProperty("class", "inactive")
            
    def serialize(self):
        res = super().serialize() 
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try: 
            return res
        except Exception as e:
            dumpException(e)
        return res

@register_node(NODE_CV2_CAM_SENDER) 
class CamSendeNode(Node): 
    width = 360
    height = 120 
    op_code = NODE_CV2_CAM_SENDER
    op_title = "Kamera Yakalayıcı"
    content_label_objname = "cv2_viewer"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    signal = "UPDATE SIGNAL"
    cap = None
    def __init__(self, scene,parent=None ): 
        super().__init__(scene,parent)  
        self.parent = scene.parent_app
        self.addInput("Başlat & Durdur")  
        self.addInput(self.signal)  
        self.addOutput("IMG")  
        self.create() 
        
     
    
    def updateImg(self):
        if self.cap is None:
            return
        ret, image = self.cap.read()  
        self.sendEval("IMG",image)

    def camStart(self):
        if self.cap is None:
            self.cap = self.parent.camStart()
        self.updateImg() 
        print("self.cap camStart",self.cap)

    def camStop(self): 
        if self.cap is not None:
            self.cap = self.parent.camStop() 
        print("self.cap camStop",self.cap)
    
    def initInnerClasses(self):
        self.content = cv2CamContent(self)
        self.grNode = Graphics(self) 

    def evalImplementation(self, name=None, data=None):
         if name =="Başlat & Durdur" and data is not None:
            if self.cap is None:
                self.camStart()
            else:
                self.camStop()

         if name == self.signal and data is not None:
             self.updateImg()
            

     