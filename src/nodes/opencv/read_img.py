import os
import cv2
import numpy as np
from qtpy.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout
from qtpy.QtCore import Qt
from nodeeditor.utils import dumpException
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import IMAGE_LOADER_NODE
from src.nodes.css.cv_css import CV2_CSS

class ImageLoaderContent(Content):
    def initUI(self):
        super().initUI()
        self.setStyleSheet(CV2_CSS)
        
        # Widget'lar
        self.btn_load = QPushButton("Resim Seç", self)
        self.btn_load.setObjectName("load_button")
        self.btn_load.clicked.connect(self.load_image)
        
        self.lbl_path = QLabel("Dosya seçilmedi", self)
        self.lbl_path.setObjectName("path_label")
        self.lbl_path.setAlignment(Qt.AlignCenter)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_path) 
        self.layout.addLayout(layout)
        self.image = None

    def load_image(self):
        """Dosya seçme dialogunu açar ve resmi yükler"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Resim Dosyası Seç",
            filter="Image Files (*.png *.jpg *.jpeg *.bmp)",
            options=options
        )
        
        if file_path:
            self.lbl_path.setText(os.path.basename(file_path))
            self.node.set_file_path(file_path)
            self.node.read_image()

    def serialize(self):
        res = super().serialize()
        res['file_path'] = self.node.file_path if hasattr(self.node, 'file_path') else ""
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        if 'file_path' in data:
            self.node.set_file_path(data['file_path'])
            self.node.read_image()
            self.lbl_path.setText(os.path.basename(data['file_path'])) 
        return True

@register_node(IMAGE_LOADER_NODE)
class ImageLoaderNode(Node):
    op_code = IMAGE_LOADER_NODE
    op_title = "Resim Yükleyici"
    content_label_objname = "image_loader"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    signal = "Sinyal"
    def __init__(self, scene,parent = None):
        super().__init__(scene,parent)
        self.parent = parent
        self.file_path = ""
        self.image_data = None
        
        self.addInput(self.signal)
        self.addOutput("Çıkış")
        self.create()

    def initInnerClasses(self):
        self.content = ImageLoaderContent(self)
        self.grNode = Graphics(self)
        self.grNode.width = 200
        self.grNode.height = 120

    def set_file_path(self, path):
        self.file_path = path
        self.markDirty(True)

    def read_image(self  ):
        """Resmi diskten okuyup işler"""
        try: 
            if os.path.exists(self.file_path):
                self.image_data = cv2.imread(self.file_path)
                if self.image_data is not None:
                    self.markDirty(False)
                    self.markInvalid(False)
                else:
                    self.markInvalid("Geçersiz resim formatı!")
            else:
                self.markInvalid("Dosya bulunamadı!")
            self.sendEval("Çıkış", self.image_data.copy())
        except Exception as e:
            self.markInvalid(str(e))
            dumpException(e)

    def evalImplementation(self, name=None, data=None):
        if self.image_data is not None:
            self.sendEval("Çıkış", self.image_data.copy())
        else:
            self.markInvalid("Resim yüklenmedi!") 