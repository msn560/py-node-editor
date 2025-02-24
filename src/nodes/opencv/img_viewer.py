import os
from qtpy.QtWidgets import QLineEdit ,QLabel,QVBoxLayout
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_CV2_CAM_VIEWER 

import numpy as np
import cv2
from qtpy.QtGui import QImage
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QTimer, QCoreApplication,QSize
from src.nodes.css.cv_css import CV2_CSS
 
class cv2Content(Content):
    img = None
    def initUI(self):
        super().initUI()   
        self.setStyleSheet(CV2_CSS)  
    
    def viewCam(self, img): 
        if img is None:
            return
        if not isinstance(img, np.ndarray): 
            return
        stretch_near = cv2.resize( img, (self.lbl.width(),self.lbl.height()), interpolation=cv2.INTER_LINEAR)
        # color Type Change
        image = cv2.cvtColor(stretch_near, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        step = channel * width 
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888) 
        self.lbl.setPixmap(QPixmap.fromImage(qImg))

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

@register_node(NODE_CV2_CAM_VIEWER) 
class CV2ViewerNode(Node): 
    width = 640
    height = 480 
    op_code = NODE_CV2_CAM_VIEWER
    op_title = "CV2 IMG VİEWER"
    content_label_objname = "cv2_viewer"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    img = None
    def __init__(self, scene,parent=None ): 
        super().__init__(scene,parent)  
        self.parent = parent
        self.addInput("IMG"  )  
        self.addOutput("Çıkış")  
        self.create() 
    
    def updateImg(self):
        img = self.get_input("IMG")
        if img is None:
            return None
        
     

    def initInnerClasses(self):
        self.content = cv2Content(self)
        self.grNode = Graphics(self) 

    def evalImplementation(self, name=None, data=None):
        if name =="IMG" and data is not None:
            if isinstance(data, np.ndarray): 
                self.img = data
                self.content.viewCam(self.img)
        self.sendEval("Çıkış",data)