import os
from qtpy.QtWidgets import QLineEdit 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_MATHEMATICS_TRIGONOMETRY 
from  src.node_editor.numeric_text_line import NumericLineEdit
import math
class lineIntContent(Content):
    def initUI(self):
        super().initUI()   
        self.edit = NumericLineEdit(parent=self ,allow_float=True )
        self.edit.setAlignment(Qt.AlignLeft) 
        self.edit.setObjectName(self.node.content_label_objname) 
        self.edit.setReadOnly(True)
        self.edit1 = NumericLineEdit(parent=self ,allow_float=True )
        self.edit1.setAlignment(Qt.AlignLeft) 
        self.edit1.setObjectName(self.node.content_label_objname) 
        self.edit1.setReadOnly(True)
        
        self.edit2 = NumericLineEdit(parent=self ,allow_float=True )
        self.edit2.setAlignment(Qt.AlignLeft) 
        self.edit2.setObjectName(self.node.content_label_objname) 
        self.edit2.setReadOnly(True)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.edit1)
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

@register_node(NODE_MATHEMATICS_TRIGONOMETRY) 
class InputINTNode(Node): 
    width = 400
    height = 80 
    op_code = NODE_MATHEMATICS_TRIGONOMETRY  
    op_title = "Trigonometri"
    content_label_objname = "line_int_trigonometry"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    def __init__(self, scene,parent=None ): 
        super().__init__(scene)  
        self.addInput("A")   
        self.addOutput("Sin")  
        self.addOutput("Cos")  
        self.addOutput("Tan")  
        self.create() 
         

    def initInnerClasses(self):
        self.content = lineIntContent(self)
        self.grNode = Graphics(self) 

    def evalImplementation(self, name=None, data=None):
        a = self.get_input("A",True) 
        if isinstance(a, (int, float)) :
            sin = math.sin(math.radians(a))
            cos =  math.cos(math.radians(a))
            tan = math.tan(math.radians(a))
            self.sendData("Sin",sin)
            self.sendData("Cos",cos)
            self.sendData("Tan",tan)
            self.content.edit.setText( str(sin ))
            self.content.edit1.setText( str( cos))
            self.content.edit2.setText( str(tan ))
        else:
            self.sendData("Sin", None)  # Hatalı giriş durumunda None gönder
            self.sendData("Cos", None)  # Hatalı giriş durumunda None gönder
            self.sendData("Tan", None)  # Hatalı giriş durumunda None gönder
            self.content.edit.setText("Geçersiz Girdi")
            self.content.edit1.setText("Geçersiz Girdi")
            self.content.edit2.setText("Geçersiz Girdi")