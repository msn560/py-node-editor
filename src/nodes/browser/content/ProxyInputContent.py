from qtpy.QtWidgets import QLineEdit, QPushButton, QHBoxLayout,QPlainTextEdit,QVBoxLayout
from nodeeditor.utils import dumpException 
from src.node_editor.content import Content
from  src.node_editor.numeric_text_line import NumericLineEdit
from urllib.parse import urlparse

class ProxyInputContent(Content): 

    def initUI(self): 
        super().initUI()   
        needs = ["host", "port", "username", "password", "only","Gönder"]
        self.input_fields = {}  # Elemanları saklamak için dict

        for need in needs:
            h_layout = QHBoxLayout()  # Her öğe için yatay layout

            if need in ["host",   "username","password"]:
                item = QLineEdit(self)
                item.setPlaceholderText(need.capitalize())
            elif need == "port":
                item = NumericLineEdit(self) 
                item.portNumberVal()
            elif need == "only":
                item = QPlainTextEdit(self)
                item.setPlaceholderText(need.capitalize())
            else:  # "only" için buton
                item = QPushButton(need, self)
                item.clicked.connect(self.ProxyFormOnSubmit)

            
            h_layout.addWidget(item)
            self.layout.addLayout(h_layout)
            self.input_fields[need] = item  # Elemanları kaydet

        self.setLayout(self.layout)
 
    def ProxyFormOnSubmit(self ): 
        if callable(self.form_on_submitcallback):
            self.form_on_submitcallback(self.form_data_to_dict())

    def addCallBack(self,AddCallBack):
        if callable(AddCallBack):
            self.form_on_submitcallback  = AddCallBack
    def form_data_to_dict(self):
        """Tüm input değerlerini bir dictionary olarak alır ve yazdırır."""
        proxy_data = {}  # Verileri saklamak için

        for key, widget in self.input_fields.items():
            if isinstance(widget, QLineEdit) :  # QLineEdit için NumericLineEdit
                proxy_data[key] = widget.text()
            elif isinstance(widget, NumericLineEdit):
                proxy_data[key] = int(widget.text())
            elif isinstance(widget, QPlainTextEdit):  # QPlainTextEdit için
                text = widget.toPlainText().strip()   
                if "," in text:  # Eğer virgül içeriyorsa, virgüle göre ayır proxy_data[key]
                    parse = [item.strip() for item in text.split(",")]
                else:  # Aksi halde satır satır al
                    parse = [item.strip() for item in text.split("\n") if item.strip()]
                proxy_data[key] = []
                for checkUrl in parse:
                    if self.getDomain(checkUrl) is not None:
                        proxy_data[key].append(checkUrl) 
        return proxy_data
    
    def getDomain(self, url):
        parsed = urlparse(url.strip())  
        return parsed.netloc if parsed.netloc else None
    
    def serialize(self):
        res = super().serialize() 
        res["proxy"] = self.form_data_to_dict()
        return res
    def dict_data_set_form (self,data:dict):
        try:
            for key in data.keys():
                if not key in self.input_fields.keys():
                    continue
                if isinstance(data[key] , list) and hasattr(self.input_fields[key] , "setPlainText"): 
                    urls = [] 
                    for url in data[key]:
                        if self.getDomain(url) is not None:
                            urls.append(url)
                    self.input_fields[key].setPlainText("\n".join(urls))
                elif hasattr(self.input_fields[key] , "setText"):
                    self.input_fields[key].setText(str(data[key]))
        except Exception as e:
            dumpException(e) 

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            if "proxy" in data:
                if isinstance(data["proxy"] ,dict):
                    self.dict_data_set_form(data["proxy"]) 
        except Exception as e:
            dumpException(e)
        return res
