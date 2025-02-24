import os
from qtpy.QtWidgets import QLineEdit 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_INPUT 

class lineTextContent(Content):
    def initUI(self):
        super().initUI()   
        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignLeft) 
        self.edit.setObjectName(self.node.content_label_objname)
        self.edit.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                font: 14px 'Segoe UI';
                border: 2px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                selection-background-color: #88C0D0;
            }
            QLineEdit:focus {
                border: 2px solid #81A1C1;
                background-color: #3B4252;
            }
        """) 
        self.layout.addWidget(self.edit)

        self.setLayout(self.layout)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(NODE_INPUT) 
class InputNode(Node): 
    width = 400
    height = 80 
    op_code = NODE_INPUT
    op_title = "Yazı"
    content_label_objname = "line_text"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    def __init__(self, scene,parent=None ): 
        super().__init__(scene)  
        self.addInput("Giriş"  )  
        self.addOutput("Çıkış")  
        self.create() 
         

    def initInnerClasses(self):
        self.content = lineTextContent(self)
        self.grNode = Graphics(self)
        self.content.edit.textChanged.connect(self.onInputTextChanged) 

    def evalImplementation(self, name=None, data=None):
        self.content.edit.setText(str(data))

    def onInputTextChanged(self ):
        text = self.content.edit.text()   
        self.sendData("Çıkış",text)