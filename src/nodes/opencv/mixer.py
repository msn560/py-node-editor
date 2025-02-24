import cv2
import os
import numpy as np
from qtpy.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QSlider, QLineEdit
from qtpy.QtCore import Qt, Signal
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from src.node_editor.constants import MIXER_NODE
from src.nodes.css.cv_css import CV2_CSS

class VideoMixerContent(Content):
    def initUI(self):
        super().initUI()
        self.setStyleSheet(CV2_CSS)
        
        self.controls = {}
        self.max_width = 1920  # Varsayılan değerler
        self.max_height = 1080
        
        params = [
            ('x', 'X:', 0, self.max_width),
            ('y', 'Y:', 0, self.max_height),
            ('width', 'Genişlik:', 10, self.max_width),
            ('height', 'Yükseklik:', 10, self.max_height),
            ('alpha', 'Alpha:', 0, 100)
        ]

        for key, label, min_val, max_val in params:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_val, max_val)
            text = QLineEdit()
            
            if key == 'alpha':
                slider.setRange(0, 100)
                text.setValidator(QDoubleValidator(0.0, 1.0, 2))
                text.setText("0.5")
                slider.setValue(50)
            else:
                slider.setRange(min_val, max_val)
                text.setValidator(QIntValidator(min_val, max_val))
                text.setText(str(min_val))
            
            self.controls[key] = (slider, text)
            
            control_layout = QHBoxLayout()
            control_layout.addWidget(QLabel(label))
            control_layout.addWidget(slider)
            control_layout.addWidget(text)
            self.layout.addLayout(control_layout)

        self.warning_label = QLabel("")
        self.warning_label.setObjectName("warning_label")
        self.layout.addWidget(self.warning_label)
        
        self.setup_connections()

    def setup_connections(self):
        for key, (slider, text) in self.controls.items():
            slider.valueChanged.connect(
                lambda value, t=text, k=key: self._handle_slider_change(value, t, k)
            )
            text.textChanged.connect(
                lambda text, s=slider, k=key: self._handle_text_change(text, s, k)
            )
    def update_max_values(self, width, height):
        """Dışarıdan gelen görüntü boyutlarına göre maksimum değerleri güncelle"""
        self.max_width = max(10, width)
        self.max_height = max(10, height)
        
        # X ve Y için maksimumlar
        self.controls['x'][0].setMaximum(self.max_width)
        self.controls['y'][0].setMaximum(self.max_height)
        
        # Genişlik ve Yükseklik için maksimumlar
        self.controls['width'][0].setMaximum(self.max_width)
        self.controls['height'][0].setMaximum(self.max_height)
        
        # Validator'ları güncelle
        self.controls['x'][1].setValidator(QIntValidator(0, self.max_width))
        self.controls['y'][1].setValidator(QIntValidator(0, self.max_height))
        self.controls['width'][1].setValidator(QIntValidator(10, self.max_width))
        self.controls['height'][1].setValidator(QIntValidator(10, self.max_height))

    def _handle_slider_change(self, value, text_widget, key):
        text_widget.blockSignals(True)
        if key == 'alpha':
            text_widget.setText(f"{value/100:.2f}")
        else:
            text_widget.setText(str(value))
        text_widget.blockSignals(False)
        self.node.update_blend()

    def _handle_text_change(self, text, slider_widget, key):
        try:
            if key == 'alpha':
                value = float(text)
                slider_widget.setValue(int(value * 100))
            else:
                value = int(text)
                slider_widget.setValue(value)
            
            slider_widget.blockSignals(True)
            slider_widget.setValue(value if key == 'alpha' else int(value))
            slider_widget.blockSignals(False)
            self.warning_label.setText("")
            self.node.update_blend()
        except ValueError:
            self.warning_label.setText("Geçersiz değer!")

    def get_values(self):
        values = {}
        for key, (slider, text) in self.controls.items():
            if key == 'alpha':
                values[key] = slider.value() / 100.0
            else:
                values[key] = slider.value()
        return values
    def serialize(self):
        res = super().serialize() 
        res['values'] = self.get_values()
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        if 'values' in data:
            for key,val in data.get("values", {}).items():
                slider, text = self.controls[key]
                
                if key == 'alpha':
                    value = float(val)
                    slider.setValue(int(value * 100))
                    text.setText(f"{value:.2f}")
                else:
                    value = int(val)
                    slider.setValue(value)
                    text.setText(str(value)) 
        return True
@register_node(MIXER_NODE)
class VideoMixerNode(Node):
    op_code = MIXER_NODE
    op_title = "Görüntü Mikser Pro"
    content_label_objname = "video_mixer_pro"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    width = 300
    height = 240
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.last_inputs = {}
        self.addInput("A Görüntüsü")
        self.addInput("B Görüntüsü")
        self.addInput("X")
        self.addInput("Y")
        self.addInput("Genişlik")
        self.addInput("Yükseklik")
        self.addInput("Alpha")
        self.addOutput("Birleşik Görüntü")
        self.addOutput("ROI Bilgisi")
        self.create()

    def initInnerClasses(self):
        self.content = VideoMixerContent(self)
        self.grNode = Graphics(self) 

    def update_blend(self):
        self.eval()

    def blend_images(self, screen, camera):
        try:
            values = self.content.get_values()
            x = values['x']
            y = values['y']
            w = values['width']
            h = values['height']
            alpha = values['alpha']

            # Optimize: Gereksiz kopyalamaları önle
            h = min(h, screen.shape[0] - y) if y < screen.shape[0] else 0
            w = min(w, screen.shape[1] - x) if x < screen.shape[1] else 0
            if h <= 0 or w <= 0:
                return None, None

            # Hızlı resize için INTER_NEAREST
            resized_cam = cv2.resize(camera, (w, h), interpolation=cv2.INTER_NEAREST)
            
            # Performans için görüntü kopyalama sadece gerekliyse yap
            blended = screen.copy() if screen.flags.writeable else np.copy(screen)
            roi = blended[y:y+h, x:x+w]
            blended[y:y+h, x:x+w] = cv2.addWeighted(roi, alpha, resized_cam, 1 - alpha, 0)
            
            return blended, (x, y, w, h)
        except Exception as e:
            self.markInvalid(f"Hata: {str(e)}")
            return None, None

    def evalImplementation(self, name=None, data=None):
        # Harici inputları işle
        if name in ['X', 'Y', 'Genişlik', 'Yükseklik', 'Alpha']:
            self._handle_parameter_input(name, data)
            return

        # Görüntü işleme
        screen = self.get_input("A Görüntüsü")
        camera = self.get_input("B Görüntüsü")
        if camera is None and screen is not None:
            camera = np.zeros_like(screen)
        if isinstance(screen, np.ndarray) and isinstance(camera, np.ndarray):
            h, w = screen.shape[:2]
            self.content.update_max_values(w, h)
            blended, roi = self.blend_images(screen, camera)
            if blended is not None:
                self.sendEval("Birleşik Görüntü", blended)
                self.sendEval("ROI Bilgisi", roi)
                self.markDirty(False)

    def _handle_parameter_input(self, name, data):
        try:
            control_map = {
                'X': 'x',
                'Y': 'y',
                'Genişlik': 'width',
                'Yükseklik': 'height',
                'Alpha': 'alpha'
            }
            
            key = control_map[name]
            slider, text = self.content.controls[key]
            
            if key == 'alpha':
                value = float(data)
                slider.setValue(int(value * 100))
                text.setText(f"{value:.2f}")
            else:
                value = int(data)
                slider.setValue(value)
                text.setText(str(value))
                
            self.markDirty(True)
        except Exception as e:
            self.markInvalid(f"Geçersiz {name} değeri: {data}")

    def onRemoved(self):
        self.last_inputs.clear()
        super().onRemoved()