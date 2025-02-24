from qtpy.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from nodeeditor.utils import dumpException 
from src.node_editor.content import Content  
from ..scripts.QBrowserWebView import QBrowser

class QbrowserContent(Content):
    def initUI(self):
        super().initUI()   
        self.browser_layout = QHBoxLayout()
        self.browser = QBrowser(self.node)
        self.browser_layout.addWidget(self.browser.driver)  

        self.bottom_layout = QHBoxLayout()
        
        self.bottom_vertical_layout = QVBoxLayout()

        self.bottom_vertical1_layout = QVBoxLayout() 
        self.bottom_vertical_h1_layout = QHBoxLayout()
        self.current_url_edit = QLineEdit("", self)
        self.current_url_edit.setText(str(self.browser.url)) 
        self.bottom_vertical_h1_layout.addWidget(self.current_url_edit)
        self.bottom_vertical_h2_layout = QHBoxLayout()
        self.browser_url_go_button = QPushButton(">", self) 
        self.bottom_vertical_h1_layout.addWidget(self.browser_url_go_button)
        self.bottom_vertical1_layout.addLayout(self.bottom_vertical_h1_layout,7)
        self.bottom_vertical1_layout.addLayout(self.bottom_vertical_h2_layout,2)
        self.bottom_vertical_layout.addLayout(self.bottom_vertical1_layout)
        self.bottom_layout.addLayout(self.bottom_vertical_layout)


        """self.bottom_vertical_layout.addWidget(QLabel("Layout 1 - Label"))
        self.bottom_vertical_layout.addWidget(QPushButton("Buton 1"))
        self.bottom_vertical_layout.addWidget(QPushButton("Buton 2"))
        """ 
        self.layout.addLayout(self.browser_layout)
        self.layout.addLayout(self.bottom_layout)
        self.setLayout(self.layout)
        
        self.browser_url_go_button.clicked.connect(self.goUrl) 
        self.browser.on_url_changed("",self.setCurrentUrl)  
        self.node.parent.addCloseCallBack(self.browser.closeEvent)

    def goUrl(self): 
        text = str(self.current_url_edit.text())
        self.browser.go(text)

    def setCurrentUrl(self,url):
        self.current_url_edit.setText(str(url)) 

    def serialize(self):
        res = super().serialize()
        try:
            res["current_url"] = self.browser.url
        except Exception as e:
            pass
        #res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if "current_url" in data:
                self.browser.go(data["current_url"])
            
            #value = data['value']
            #self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res
