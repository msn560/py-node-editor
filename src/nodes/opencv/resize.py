import os
import cv2
import numpy as np
from qtpy.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, 
                           QSlider, QCheckBox, QSizePolicy)
from qtpy.QtCore import Qt
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_CV2_RESIZE
from src.node_editor.numeric_text_line import NumericLineEdit
from src.nodes.css.cv_css import CV2_CSS
 

class ResizeContent(Content):
    def __init__(self, node):
        super().__init__(node)
        self.orig_width = 0
        self.orig_height = 0
        self.lock_aspect_ratio = True
        
    def initUI(self):
        super().initUI()
        self.setStyleSheet(CV2_CSS)
        
        # Kontrol elemanları
        self.percentage_slider, self.percentage_text = self.create_control("Yüzde:", 10, 400, 100)
        self.width_slider, self.width_text = self.create_control("Genişlik:", 1, 4096, 640)
        self.height_slider, self.height_text = self.create_control("Yükseklik:", 1, 4096, 480)
        self.aspect_check = QCheckBox("En-Boy Oranını Koru", self)
        self.aspect_check.setChecked(True)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_control_group("Boyutlandırma Yüzdesi", self.percentage_slider, self.percentage_text))
        main_layout.addLayout(self.create_control_group("Genişlik", self.width_slider, self.width_text))
        main_layout.addLayout(self.create_control_group("Yükseklik", self.height_slider, self.height_text))
        main_layout.addWidget(self.aspect_check)
        main_layout.addStretch()
        
        self.layout.addLayout(main_layout)
        self.setup_connections()

    def create_control(self, label_text, min_val, max_val, default):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        text = NumericLineEdit(self)
        text.setText(str(default))
        return slider, text

    def create_control_group(self, title, slider, text):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(slider, 4)
        layout.addWidget(text, 1)
        return layout

    def setup_connections(self):
        controls = [
            (self.percentage_slider, self.percentage_text, self.update_from_slider),
            (self.width_slider, self.width_text, self.update_size),
            (self.height_slider, self.height_text, self.update_size)
        ]
        
        for slider, text, callback in controls:
            slider.valueChanged.connect(lambda v, t=text: callback(v, t))
            text.textChanged.connect(lambda _, s=slider: self.update_from_text(s))

        self.aspect_check.stateChanged.connect(self.toggle_aspect_ratio)

    def update_original_size(self, width, height):
        self.orig_width = width
        self.orig_height = height
        self.width_slider.setMaximum(width * 4)
        self.height_slider.setMaximum(height * 4)

    def toggle_aspect_ratio(self, state):
        self.lock_aspect_ratio = state == Qt.Checked

    def update_from_slider(self, value, text_input):
        text_input.blockSignals(True)
        text_input.setText(str(value))
        text_input.blockSignals(False)
        self.calculate_dimensions()

    def update_from_text(self, slider):
        try:
            value = int(slider.sender().text())
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            self.calculate_dimensions()
        except:
            pass

    def update_size(self, value, text_input):
        self.update_from_slider(value, text_input)
        if self.lock_aspect_ratio:
            self.adjust_aspect_ratio()

    def adjust_aspect_ratio(self):
        if self.orig_width == 0 or self.orig_height == 0:
            return
            
        ratio = self.orig_width / self.orig_height
        if self.sender() == self.width_slider:
            new_height = int(self.width_slider.value() / ratio)
            self.height_slider.setValue(new_height)
        else:
            new_width = int(self.height_slider.value() * ratio)
            self.width_slider.setValue(new_width)

    def calculate_dimensions(self):
        percentage = self.percentage_slider.value() / 100.0
        new_width = int(self.orig_width * percentage)
        new_height = int(self.orig_height * percentage)
        
        self.width_slider.blockSignals(True)
        self.height_slider.blockSignals(True)
        
        self.width_slider.setValue(new_width)
        self.height_slider.setValue(new_height)
        
        self.width_slider.blockSignals(False)
        self.height_slider.blockSignals(False)

    def serialize(self):
        res = super().serialize()
        res.update({
            'percentage': self.percentage_slider.value(),
            'width': self.width_slider.value(),
            'height': self.height_slider.value(),
            'lock_aspect': self.lock_aspect_ratio
        })
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        self.percentage_slider.setValue(data.get('percentage', 100))
        self.width_slider.setValue(data.get('width', 640))
        self.height_slider.setValue(data.get('height', 480))
        self.aspect_check.setChecked(data.get('lock_aspect', True))
        return True

@register_node(NODE_CV2_RESIZE)
class ResizeNode(Node):
    op_code = NODE_CV2_RESIZE
    op_title = "Resim Boyutlandırıcı"
    content_label_objname = "resize_node"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    def __init__(self, scene, parent=None):
        super().__init__(scene)
        self.original_image = None
        self.addInput("Giriş")
        self.addOutput("Çıkış")
        self.addOutput("Orjinal")
        self.create()

    def initInnerClasses(self):
        self.content = ResizeContent(self)
        self.grNode = Graphics(self)

    def process_image(self):
        if self.original_image is None:
            return

        try:
            width = self.content.width_slider.value()
            height = self.content.height_slider.value()
            
            resized = cv2.resize(self.original_image, (width, height), 
                              interpolation=cv2.INTER_AREA)
            
            self.sendEval("Çıkış", resized)
            self.markDirty(False)
        except Exception as e:
            dumpException(e)

    def evalImplementation(self, name=None, data=None):
        if name == "Giriş" and isinstance(data, np.ndarray):
            self.original_image = data.copy()
            h, w = data.shape[:2]
            self.content.update_original_size(w, h)
            self.sendEval("Orjinal", self.original_image)
            self.process_image()