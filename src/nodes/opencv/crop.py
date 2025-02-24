import os
from qtpy.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QSlider, QSizePolicy)
from qtpy.QtCore import Qt, QTimer
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_CROP
from src.node_editor.numeric_text_line import NumericLineEdit
import numpy as np
from src.nodes.css.cv_css import CV2_CSS

class CropContent(Content):
    def __init__(self, node):
        super().__init__(node)
        self.img_width = 0
        self.img_height = 0
        
    def initUI(self):
        super().initUI()
        self.setStyleSheet(CV2_CSS)
        
        # Slider ve input alanları oluşturma
        self.x_slider, self.x_text = self.create_slider_input("X:")
        self.y_slider, self.y_text = self.create_slider_input("Y:")
        self.w_slider, self.w_text = self.create_slider_input("Genişlik:")
        self.h_slider, self.h_text = self.create_slider_input("Yükseklik:")

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_control_group("X Kontrol", self.x_slider, self.x_text))
        main_layout.addLayout(self.create_control_group("Y Kontrol", self.y_slider, self.y_text))
        main_layout.addLayout(self.create_control_group("Genişlik Kontrol", self.w_slider, self.w_text))
        main_layout.addLayout(self.create_control_group("Yükseklik Kontrol", self.h_slider, self.h_text))
        self.layout.addLayout(main_layout) 
        self.setup_connections()

    def create_slider_input(self, label_text):
        slider = QSlider(Qt.Horizontal)
        slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        text = NumericLineEdit(self)
        text.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return slider, text

    def create_control_group(self, title, slider, text):
        layout = QHBoxLayout()
        label = QLabel(title)
        layout.addWidget(label, 1)
        layout.addWidget(slider, 4)
        layout.addWidget(text, 1)
        return layout

    def setup_connections(self):
        # Slider ve text input bağlantıları
        self.x_slider.valueChanged.connect(lambda v: self.update_from_slider(v, self.x_text))
        self.y_slider.valueChanged.connect(lambda v: self.update_from_slider(v, self.y_text))
        self.w_slider.valueChanged.connect(lambda v: self.update_from_slider(v, self.w_text))
        self.h_slider.valueChanged.connect(lambda v: self.update_from_slider(v, self.h_text))

        self.x_text.textChanged.connect(lambda: self.update_from_text(self.x_slider, self.x_text))
        self.y_text.textChanged.connect(lambda: self.update_from_text(self.y_slider, self.y_text))
        self.w_text.textChanged.connect(lambda: self.update_from_text(self.w_slider, self.w_text))
        self.h_text.textChanged.connect(lambda: self.update_from_text(self.h_slider, self.h_text))

    def update_image_size(self, width, height):
        self.img_width = width
        self.img_height = height
        
        # Slider limitlerini güncelle
        self.x_slider.setMaximum(max(0, width-1))
        self.y_slider.setMaximum(max(0, height-1))
        self.w_slider.setMaximum(max(1, width - self.x_slider.value()))
        self.h_slider.setMaximum(max(1, height - self.y_slider.value()))

    def update_from_slider(self, value, text_input):
        text_input.blockSignals(True)
        text_input.setText(str(value))
        text_input.blockSignals(False)
        self.node.cropImg()

    def update_from_text(self, slider, text_input):
        try:
            value = int(text_input.text())
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            self.node.cropImg()
        except:
            pass

    def serialize(self):
        res = super().serialize()
        res.update({
            'x': self.x_slider.value(),
            'y': self.y_slider.value(),
            'w': self.w_slider.value(),
            'h': self.h_slider.value()
        })
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        self.x_slider.setValue(data.get('x', 0))
        self.y_slider.setValue(data.get('y', 0))
        self.w_slider.setValue(data.get('w', 100))
        self.h_slider.setValue(data.get('h', 100))
        return True

@register_node(NODE_CROP)
class CropNode(Node):
    op_code = NODE_CROP
    op_title = "Kırp"
    content_label_objname = "crop_node"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    def __init__(self, scene, parent=None):
        super().__init__(scene)
        self.img = None
        self.addInput("IMG")
        self.addOutput("Çıkış")
        self.addOutput("Orjinal")
        self.create()

    def initInnerClasses(self):
        self.content = CropContent(self)
        self.grNode = Graphics(self)
    
    def cropImg(self):
        if isinstance(self.img, np.ndarray):
            # Resim boyutlarını content'e gönder
            h, w = self.img.shape[:2]
            self.content.update_image_size(w, h)
            
            # Slider değerlerini al
            x = self.content.x_slider.value()
            y = self.content.y_slider.value()
            width = self.content.w_slider.value()
            height = self.content.h_slider.value()

            # Sınır kontrolleri
            x = max(0, min(x, w - 1))
            y = max(0, min(y, h - 1))
            width = max(1, min(width, w - x))
            height = max(1, min(height, h - y))

            # Kırpma işlemi
            crop = self.img[y:y+height, x:x+width]
            self.sendEval("Çıkış", crop)
            self.markDirty(False)

    def evalImplementation(self, name=None, data=None):
        if name == "IMG" and isinstance(data, np.ndarray):
            self.img = data.copy()
            self.sendEval("Orjinal", self.img)
            self.cropImg()