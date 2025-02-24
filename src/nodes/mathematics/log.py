import os
from qtpy.QtWidgets import QLineEdit 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_MATHEMATICS_LOG
from  src.node_editor.numeric_text_line import NumericLineEdit
import math

class lineIntContent(Content):
    def initUI(self):
        super().initUI()   
        self.edit = NumericLineEdit(parent=self ,allow_float=True)
        self.edit.setAlignment(Qt.AlignLeft) 
        self.edit.setObjectName(self.node.content_label_objname) 
        self.edit.setReadOnly(True)
        self.edit2 = NumericLineEdit(parent=self ,allow_float=True)
        self.edit2.setAlignment(Qt.AlignLeft) 
        self.edit2.setObjectName(self.node.content_label_objname) 
        self.edit2.setReadOnly(True)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.edit2)

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

@register_node(NODE_MATHEMATICS_LOG) 
class InputINTNode(Node): 
    width = 400
    height = 80 
    op_code = NODE_MATHEMATICS_LOG
    op_title = "Logaritma İşlemi "
    content_label_objname = "line_int_sum"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    def __init__(self, scene,parent=None ): 
        super().__init__(scene)  
        self.addInput("A")   
        self.addInput("Base")   
        self.addOutput("Sonuç")  
        self.create() 
         

    def initInnerClasses(self):
        self.content = lineIntContent(self)
        self.grNode = Graphics(self) 

    def evalImplementation(self, name=None, data=None):
        a = self.get_input("A",True) 
        base = self.get_input("Base",True) 
        if not isinstance(base,int):
            base = 10
        if isinstance(a, (int, float)) :
            self.sendData("Sonuç", math.log(a, base))
            self.content.edit.setText(str(math.log(a, base)))
            self.content.edit2.setText("Base: " +str(base))
         
        else:
            self.sendData("Sonuç", None)  # Hatalı giriş durumunda None gönder
            self.content.edit.setText("Geçersiz Girdi")
            self.content.edit2.setText("Geçersiz Girdi")