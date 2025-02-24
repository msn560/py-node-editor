import os
from .content.QTBROWSER_HeadersContent import QTBROWSER_HeadersContent 
from src.node_editor.constants import NODE_QBROWSER_HEADERS_TABLE
from src.node_editor.collector import register_node   
from src.node_editor.node import Node
from src.node_editor.graphics import Graphics  

@register_node(NODE_QBROWSER_HEADERS_TABLE)
class QTBROWSER_HeadersNode(Node):
    op_code = NODE_QBROWSER_HEADERS_TABLE
    op_title = "QTB Headers"
    content_label_objname = "qt_headers_output_viewer"
    category =  os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    width = 640
    height = 640

    def __init__(self, scene,parent=None):
        super().__init__(scene,parent)
        self.addInput("QT_BROWSER_HEADERS", multi_connect=True)
        self.create( )
        self.grNode.setZValue(-1)  # Arkada görünmesi için

    def initInnerClasses(self):
        self.content = QTBROWSER_HeadersContent(self)
        self.grNode = Graphics(self)
         
 

    def evalImplementation(self, name , data):   
        if name == "QT_BROWSER_HEADERS" and isinstance(data,list):
            self.content.updateTable(data)
         