import os
from qtpy.QtWidgets import QLineEdit, QPushButton  
from nodeeditor.utils import dumpException  
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_BUTTON_INPUT 

class ButtonInputContent(Content): 

    def initUI(self): 
        super().initUI()   
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Text Input
        self.edit = QLineEdit("", self)
        self.edit.setPlaceholderText("Veri girin...") 
        
        # Action Button
        self.button = QPushButton("Gönder", self) 
        
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout) 
 

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            self.edit.setText(data.get('value', ''))
        except Exception as e:
            dumpException(e)
        return res

@register_node(NODE_BUTTON_INPUT)
class ButtonInputNode(Node):
    op_code = NODE_BUTTON_INPUT
    op_title = "Butonlu Yazı"
    content_label_objname = "button_input"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__))) 
    width = 350
    height = 130 
    def __init__(self, scene,parent=None):
        super().__init__(scene)
        self.addOutput("Çıktı" )
        self.create( )  

    def initInnerClasses(self):
        self.content = ButtonInputContent(self)
        self.grNode = Graphics(self) 
        self.content.button.clicked.connect(self.sendDataOnClick)

    def sendDataOnClick(self):
        """Buton tıklandığında veriyi sonraki node'a gönder"""
        text = self.content.edit.text()
        self.markDirty()  # Node'u değişmiş olarak işaretle
        self.sendData("Çıktı", text)

    def evalImplementation(self, **kwargs):
        # Buton tetiklemeli olduğu için burada pasif kalıyor
        pass

    def getInputData(self):
        """Diğer node'lardan veri almak için (opsiyonel)"""
        return self.content.edit.text()

    def onInputChanged(self, socket=None):
        """Input değiştiğinde otomatik gönderim (opsiyonel)"""
        #self.sendDataOnClick()  # Otomatik gönderim için aktif edilebilir