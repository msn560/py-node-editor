import os
from qtpy.QtWidgets import QPlainTextEdit  
from src.node_editor.constants import NODE_OUTPUT
from nodeeditor.utils import dumpException 
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from qtpy.QtCore import Qt, Signal
class OutputViewerContent(Content):
    updateOutput = Signal(str)  # Çıktı güncelleme sinyali

    def initUI(self):
        super().initUI() 
         
        
        # Çıktı Görüntüleyici
        self.output_view = QPlainTextEdit(self)
        self.output_view.setReadOnly(True) 
         
        self.layout.addWidget(self.output_view)
        self.setLayout(self.layout)
         

    def onSendClicked(self):
        text = self.input_edit.text()
        if text:
            self.updateOutput.emit(f">> {text}")
            self.input_edit.clear()

    def updateOutputView(self, text):
        """Çıktı alanına yeni metin ekler"""
        self.output_view.setPlainText(text)
        self.output_view.verticalScrollBar().setValue(
            self.output_view.verticalScrollBar().maximum()
        )

    def serialize(self):
        res = super().serialize()
        res['output_text'] = self.output_view.toPlainText() 
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        try:
            self.output_view.setPlainText(data.get('output_text', '')) 
        except Exception as e:
            dumpException(e)
        return True

@register_node(NODE_OUTPUT)
class OutputViewerNode(Node):
    op_code = NODE_OUTPUT
    op_title = "Çıktı Görüntüleyici"
    content_label_objname = "output_viewer"
    category =os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    width = 400
    height = 300

    def __init__(self, scene,parent=None):
        super().__init__(scene,parent)
        self.addInput("Girdi", multi_connect=True)
        self.create()
        self.grNode.setZValue(-1)  # Arkada görünmesi için

    def initInnerClasses(self):
        self.content = OutputViewerContent(self)
        self.grNode = Graphics(self) 

    def eval(self, name=None, data=None):
        if self.debug:
            print("name",name)
            print("data",type(data),data)
        self.runnedEvalColor()
        if data is None:
            data = self.get_input("Girdi",True)
        self.content.updateOutputView(str(data))

    def evalImplementation(self, name=None, data=None):    
        pass
            
         