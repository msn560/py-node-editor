
from qtpy.QtWidgets import QLabel,QVBoxLayout  
from nodeeditor.node_content_widget import QDMNodeContentWidget 

class Content(QDMNodeContentWidget): 
    def initUI(self):
        self.layout = QVBoxLayout() 
        self.lbl = QLabel(self.node.content_label, self)
        self.lbl.setObjectName(self.node.content_label_objname)  
        self.lbl.setFixedWidth(self.node.width) 
        self.lbl.setFixedHeight(self.node.height )  
        self.width = self.node.width
        self.height = self.node.height 
        self.setFixedSize(self.width,self.height)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)  
         
