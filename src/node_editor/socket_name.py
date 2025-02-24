from qtpy.QtWidgets import  QLabel, QGraphicsProxyWidget, QGraphicsItem
from qtpy.QtGui import QFont  
from qtpy.QtCore import QRectF, Qt

class SocketNameLabel(QGraphicsItem):
    
    def __init__(self, text="", color="white",width=200, height=50, parent=None):
        super().__init__(parent)
        # QLabel oluştur ve stilini ayarla
        self.label = QLabel(text) 
        self.label.setContentsMargins(10,0, 10, 0)  # (Sol, Üst, Sağ, Alt)

        "background-color: rgb(128, 0, 128);"
        self.label.setStyleSheet(""" 
            color: """+ color +""";
            border: none; 
            background: transparent;
        """)
        self.label.setFont(QFont("Arial", 7)) 
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.label)
        
    def boundingRect(self):
        return QRectF(0, 0, self.label.width(), self.label.height())
    
    def paint(self, painter, option, widget=None):
        # QGraphicsProxyWidget kendisi çizim yapıyor; burada ekstra bir çizim yapmaya gerek yok.
        pass