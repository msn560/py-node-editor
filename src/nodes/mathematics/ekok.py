import os
from qtpy.QtWidgets import QLineEdit 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_MATHEMATICS_EKOK
from  src.node_editor.numeric_text_line import NumericLineEdit

class lineIntContent(Content):
    def initUI(self):
        super().initUI()   
        self.edit = NumericLineEdit(parent=self ,allow_float=True)
        self.edit.setAlignment(Qt.AlignLeft) 
        self.edit.setObjectName(self.node.content_label_objname) 
        self.edit.setReadOnly(True)
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

@register_node(NODE_MATHEMATICS_EKOK) 
class InputINTNode(Node): 
    width = 400
    height = 80 
    op_code = NODE_MATHEMATICS_EKOK
    op_title = "EKOK"
    content_label_objname = "line_int_sum"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    def __init__(self, scene,parent=None ): 
        super().__init__(scene)  
        self.addInput("A")  
        self.addInput("B")  
        self.addOutput("Sonuç")  
        self.create() 
         

    def initInnerClasses(self):
        self.content = lineIntContent(self)
        self.grNode = Graphics(self) 
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    def lcm(self,a, b):
        return abs(a * b) // self.gcd(a, b)
    
    def evalImplementation(self, name=None, data=None):
        a = self.get_input("A",True)
        b = self.get_input("B",True)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            ekok = self.lcm(a,b)
            self.sendData("Sonuç", ekok)
            self.content.edit.setText(str( ekok))
        else:
            self.sendData("Sonuç", None)  # Hatalı giriş durumunda None gönder
            self.content.edit.setText("Geçersiz Girdi")
             