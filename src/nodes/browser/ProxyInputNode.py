import os
from src.node_editor.constants import NODE_QT_PROXY_INPUT
from src.node_editor.collector import register_node 
from src.node_editor.node import Node
from src.node_editor.graphics import Graphics
import json
from .content.ProxyInputContent import ProxyInputContent

@register_node(NODE_QT_PROXY_INPUT)
class ProxyInputNode(Node):
    op_code = NODE_QT_PROXY_INPUT
    op_title = "QTB Proxy Girişi"
    content_label_objname = "qtb_proxy_input"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    
    width = 350
    height = 480
    signal = "Sinyal"
    def __init__(self, scene,parent=None):
        super().__init__(scene)
        self.addInput("Değiştir")
        self.addInput(self.signal)
        self.addOutput("Çıktı")
        self.create( )  
        

    def initInnerClasses(self):
        self.content = ProxyInputContent(self)
        self.grNode = Graphics(self)  
        self.content.addCallBack(self.sendDataOnClick)

    def sendDataOnClick(self,data): 
        print("sendDataOnClick data",data) 
        self.sendData("Çıktı",data) 

    def evalImplementation(self, name , data):
        print("proxy eval", type(data),name,data)
        if name == "Değiştir":
            if isinstance(data ,dict):
                self.content.dict_data_set_form(data)
            elif isinstance(data ,str):
                try:
                    data = dict(json.loads( data.replace("'", '"')))
                    self.content.dict_data_set_form(data)
                except:
                    pass
        elif name ==  self.signal and data is not None:
            self.sendEval("Çıktı", self.content.form_data_to_dict()) 
        pass

    def getInputData(self): 
        pass

    def onInputChanged(self, socket=None):
        """Input değiştiğinde otomatik gönderim (opsiyonel)"""
        #self.sendDataOnClick()  # Otomatik gönderim için aktif edilebilir