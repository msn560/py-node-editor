import os
import cv2
import pyautogui
import numpy as np
from qtpy.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, 
                           QSlider, QLineEdit, QPushButton)
from qtpy.QtCore import Qt, QTimer
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_SCREEN_SENDER
from src.nodes.css.cv_css import CV2_CSS

class ScreenContent(Content):
    def __init__(self, node):
        super().__init__(node)
        self.screen_width, self.screen_height = pyautogui.size()
        self._block_updates = False

    def initUI(self):
        super().initUI()
        self.setStyleSheet(CV2_CSS)
        try:
            # Ekran boyutlarını alma işlemini try-except içine aldık
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception as e:
            print(f"Ekran boyutu alınamadı: {str(e)}")
            self.screen_width, self.screen_height = 1920, 1080  
        # Kontrol elemanları
        self.left_slider, self.left_text = self.create_control("Left:", 0, self.screen_width)
        self.top_slider, self.top_text = self.create_control("Top:", 0, self.screen_height)
        self.width_slider, self.width_text = self.create_control("Width:", 1, self.screen_width)
        self.height_slider, self.height_text = self.create_control("Height:", 1, self.screen_height)
        
        # Capture butonu
        self.capture_btn = QPushButton("Yakala", self)
        self.capture_btn.setObjectName("screen_button")
        self.capture_btn.clicked.connect(self.node._capture_screen)
        
        # Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_control_group("Left", self.left_slider, self.left_text))
        main_layout.addLayout(self.create_control_group("Top", self.top_slider, self.top_text))
        main_layout.addLayout(self.create_control_group("Width", self.width_slider, self.width_text))
        main_layout.addLayout(self.create_control_group("Height", self.height_slider, self.height_text))
        main_layout.addWidget(self.capture_btn)
        main_layout.addStretch()
        
        self.layout.addLayout(main_layout)
        self.setup_connections()

    def create_control(self, label_text, min_val, max_val):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        text = QLineEdit(self)
        text.setText(str(min_val))
        return slider, text

    def create_control_group(self, title, slider, text):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(slider, 4)
        layout.addWidget(text, 1)
        return layout

    def setup_connections(self):
        controls = [
            (self.left_slider, self.left_text),
            (self.top_slider, self.top_text),
            (self.width_slider, self.width_text),
            (self.height_slider, self.height_text)
        ]
        
        for slider, text in controls:
            slider.valueChanged.connect(lambda v, t=text: self.update_from_slider(v, t))
            # DÜZELTİLMİŞ KISIM:
            text.textChanged.connect(self.update_from_text)  # Lambda kaldırıldı

    def update_from_slider(self, value, text_input):
        text_input.blockSignals(True)
        text_input.setText(str(value))
        text_input.blockSignals(False)
        self.adjust_dimensions()

    def update_from_text(self):
        """Text input değiştiğinde slider'ı güncelle"""
        try:
            if self._block_updates: return
            
            # Değişen text inputu bul
            text_input = self.sender()
            slider = self._find_connected_slider(text_input)
            
            if slider:
                value = int(text_input.text())
                self._set_control_value(slider, text_input, value)
                
        except ValueError:
            pass

    def adjust_dimensions(self):
        # Width ve Height sınır kontrolü
        max_width = self.screen_width - self.left_slider.value()
        self.width_slider.setMaximum(max_width)
        self.width_text.setPlaceholderText(f"Max: {max_width}")

        max_height = self.screen_height - self.top_slider.value()
        self.height_slider.setMaximum(max_height)
        self.height_text.setPlaceholderText(f"Max: {max_height}")

    def serialize(self):
        res = super().serialize()
        res.update({
            'left': self.left_slider.value(),
            'top': self.top_slider.value(),
            'width': self.width_slider.value(),
            'height': self.height_slider.value()
        })
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        self.left_slider.setValue(data.get('left', 0))
        self.top_slider.setValue(data.get('top', 0))
        self.width_slider.setValue(data.get('width', 100))
        self.height_slider.setValue(data.get('height', 100))
        return True
    def _set_control_value(self, slider, text_input, value):
        """Slider ve text input değerlerini güvenle günceller"""
        if self._block_updates:
            return
            
        self._block_updates = True
        
        try:
            # Değer sınırlamaları
            value = max(slider.minimum(), min(value, slider.maximum()))
            
            # Slider ve text'i güncelle
            slider.setValue(int(value))
            text_input.setText(str(int(value)))
            
            # Boyut sınırlarını yeniden hesapla
            self.adjust_dimensions()
        finally:
            self._block_updates = False
    def update_from_slider(self, value, text_input):
        """Slider değişimlerini işler"""
        if self._block_updates: return
        self._set_control_value(self.sender(), text_input, value)

    def update_from_text(self):
        """Text input değişimlerini işler"""
        if self._block_updates: return
        text_input = self.sender()
        try:
            value = int(text_input.text())
            slider = self._find_connected_slider(text_input)
            if slider:
                self._set_control_value(slider, text_input, value)
        except ValueError:
            pass

    def _find_connected_slider(self, text_input):
        """Text inputa bağlı slider'ı bul"""
        controls = {
            self.left_text: self.left_slider,
            self.top_text: self.top_slider,
            self.width_text: self.width_slider,
            self.height_text: self.height_slider
        }
        return controls.get(text_input)

@register_node(NODE_SCREEN_SENDER) 
class ScreenNode(Node):
    op_code = NODE_SCREEN_SENDER
    op_title = "Ekran Yakalayıcı"
    content_label_objname = "screen_sender"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    width = 480
    height = 240 
    def __init__(self, scene, parent=None):
        super().__init__(scene)
        self.addInput("Trigger")
        self.addInput("Left")
        self.addInput("Top")
        self.addInput("Width")
        self.addInput("Height")
        self.addOutput("IMG")
        self.addOutput("Dimensions")
        self.create()

    def initInnerClasses(self):
        self.content = ScreenContent(self)
        self.grNode = Graphics(self)

    def updateImg(self):
        try:
            left = self.content.left_slider.value()
            top = self.content.top_slider.value()
            width = self.content.width_slider.value()
            height = self.content.height_slider.value()
            
            image = self.screenBGR(left, top, width, height)
            self.sendEval("IMG", image)
            self.sendEval("Dimensions", (width, height))
        except Exception as e:
            dumpException(e)

    def screen(self, left=None, top=None, width=None, height=None):
        region = (left, top, width, height) if all([v is not None for v in [left, top, width, height]]) else None
        return pyautogui.screenshot(region=region)

    def screenBGR(self, left=None, top=None, width=None, height=None):
        return cv2.cvtColor(np.array(self.screen(left, top, width, height)), cv2.COLOR_RGB2BGR)

    def get_dimension_values(self):
        """Tüm boyut değerlerini iç/dış inputlardan al"""
        return {
            'left': self.get_input_value('Left', self.content.left_slider),
            'top': self.get_input_value('Top', self.content.top_slider),
            'width': self.get_input_value('Width', self.content.width_slider),
            'height': self.get_input_value('Height', self.content.height_slider)
        }

    def get_input_value(self, input_name, slider):
        """Bağlı input varsa onu kullan, yoksa slider değerini"""
        input_socket = self.getInputSocket(input_name)
        if input_socket and input_socket.hasEdge():
            data = input_socket.getData()
            if data is not None:
                return int(data)
        return slider.value()

    def update_ui_from_inputs(self):
        """Harici input değerlerini UI'ya yansıt"""
        inputs = {
            'Left': (self.content.set_left, 0, self.content.screen_width),
            'Top': (self.content.set_top, 0, self.content.screen_height),
            'Width': (self.content.set_width, 1, self.content.screen_width),
            'Height': (self.content.set_height, 1, self.content.screen_height)
        }

        for input_name, (set_func, min_val, max_val) in inputs.items():
            input_socket = self.getInputSocket(input_name)
            if input_socket and input_socket.hasEdge():
                data = input_socket.getData()
                if data is not None:
                    clamped = max(min_val, min(int(data), max_val))
                    set_func(clamped)

    def evalImplementation(self, name=None, data=None):
        # Input değişikliklerini işle
        if name in ["Left", "Top", "Width", "Height"] and data is not None: 
            if name == "Left":
                self.content.left_text.setText(str(data))
            if name == "Top":
                self.content.top_text.setText(str(data))
            if name == "Width":
                self.content.width_text.setText(str(data))
            if name == "Height":
                self.content.height_text.setText(str(data))
            self.content.update_from_text()
            self._process_dimension_input(name, data)
        elif name == "Trigger":
            self._capture_screen()

    def _process_dimension_input(self, name, data):
        """Harici boyut verilerini işler"""
        try:
            value = int(data)
            setter = getattr(self.content, f'set_{name.lower()}', None)
            if setter:
                # Ekran boyutlarını güncel tut
                self.content.update_screen_size()
                
                # Maksimum sınırları belirle
                max_val = {
                    'left': self.content.screen_width,
                    'top': self.content.screen_height,
                    'width': self.content.screen_width - self.content.left_slider.value(),
                    'height': self.content.screen_height - self.content.top_slider.value()
                }[name.lower()]
                
                # Değeri kısıtla ve uygula
                clamped_value = max(0, min(value, max_val))
                setter(clamped_value)
                
        except (ValueError, TypeError) as e:
            print(f"Geçersiz veri: {name}={data} ({type(data)})")
            self.markInvalid(f"Geçersiz {name} değeri: {data}")

    def _capture_screen(self):
        """Ekran görüntüsünü yakala ve gönder"""
        try:
            params = {
                'left': self.content.left_slider.value(),
                'top': self.content.top_slider.value(),
                'width': self.content.width_slider.value(),
                'height': self.content.height_slider.value()
            }
            image = self.screenBGR(**params)
            self.sendEval("IMG", image)
            self.sendEval("Dimensions", (params['width'], params['height']))
            self.markDirty(False)
        except Exception as e:
            dumpException(e)
            self.markInvalid(f"Yakalama hatası: {str(e)}")