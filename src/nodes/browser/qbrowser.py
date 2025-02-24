import json,os
from urllib.parse import urlparse 
from src.node_editor.constants import NODE_QBROWSER
from src.node_editor.collector import register_node   
from src.node_editor.node import Node
from src.node_editor.graphics import Graphics  
from .content.QbrowserContent import QbrowserContent
@register_node(NODE_QBROWSER) 
class QbrowserNode(Node): 
    width = 980
    height = 640 
    op_code = NODE_QBROWSER
    op_title = "QTBrowser"
    content_label_objname = "line_text"
    category =  os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    url = "https://www.google.com/"
    proxy = {}
    proxy_status = False
    proxy_is_check = False
    signal = "Sinyal"
    def __init__(self, scene ,parent=None):  
        if parent is not None:
            self.parent = parent
        elif scene.parent_app is not None:
            self.parent = scene.parent_app 

        super().__init__(scene,self.parent)  
        self.addInput("URL" ,color=1)  
        self.addInput("COOKIES",color=2)  
        self.addInput("HEADERS",color=4)  
        self.addInput("INJECTJS",color=3)  
        self.addInput("INAGENT")  
        self.addInput("INHTML",color=6)  
        self.addInput("PROXY",color=7)  

        self.addOutput("CURRENT_URL" ,color=1 )  
        self.addOutput("HTML",color=6 )  
        self.addOutput("COOKIES",color=2 )  
        self.addOutput("RESULTJS",color=3 )  
        self.addOutput("HEADERS" ,color=4)   
        self.addOutput("PAGE_LOAD_STATUS" ,color=5)   
        self.create()  
        self.grNode.add_node_hover_effect_callBack(self.isHoverNode)
        self.content.browser.debug_listener.thread.data_updated.connect(self.sendHeadersResult) 
        self.content.browser.debug_listener.start()
        
    def get_text(self,**kwargs):
        return self.content.edit.text()
    
    def initInnerClasses(self):
        self.content = QbrowserContent(self)
        self.grNode = Graphics(self)
        #self.content.edit.textChanged.connect(self.onInputChanged)
        self.content.browser.go(self.url)
        self.content.browser.driver.show() 
        self.addallcallback()
        

    def isHoverNode(self,_isHover = False): 
        if self.parent is not None:
            if _isHover:
                self.parent.setWeelStatus(False) 
                self.parent.addWheelEventCallBack(self.content.browser.driver.wheelEvent)
            else:
                
                self.parent.setWeelStatus(True) 
                self.parent.addWheelEventCallBack(None)

    def addallcallback(self):
        self.content.browser.set_pagel_load_status_callback(self.sendPageStatus)
        self.content.browser.get_page_html(self.sendHtml) 
        self.content.browser.get_cookies(self.sendCookies) 
        self.content.browser.on_url_changed("",self.sendUrl) 
        self.content.browser.set_pagel_load_status_callback(self.sendPageStatus) 

    def evalImplementation(self,name , data): 
        if self.debug:
            print("browser evalImplementation",name , data)
        self.addallcallback()
        if name == "PROXY" and data is not None:
            self.setProxy(data) 
        if name == "URL" and data is not None:
            proxy_data = self.get_input("PROXY",True)
            if proxy_data is not None:
                self.setProxy(proxy_data) 
            js_data = self.get_input("INJECTJS",True)
            if js_data is not None:
                self.setJsData(js_data)
            agent_data = self.get_input("INAGENT",True)
            if agent_data is not None:
                self.setAgentData(agent_data) 
                
            self.url = data
            self.content.browser.go(data)
        elif name == "COOKIES" and data is not None:
            json_duzeltildi = data.replace("'", '"') 
            val = dict(json.loads(json_duzeltildi, strict=False))
            parsed_url = urlparse(self.url) 
            for key in val.keys():
                self.content.browser.set_cookie(key , val[key], parsed_url.netloc) 
        elif name == "INJECTJS" and data is not None:
            self.setJsData(data)
        elif name == "INHTML" and data is not None:
            self.content.browser.driver.setHtml(data) 
        elif name == "INAGENT" and data is not None:
            self.setAgentData(data)
        
          
    def setJsData(self,data):
        self.content.browser.inject_javascript(True,data,self.sendJsResult)
    def setAgentData(self,data):
        self.content.browser.driver_page.profile().setHttpUserAgent(data)
    def setProxy(self,data):
        data = self.proxyPortStrToInt(data)
        check = ["host","port","username","password","only"]
        if data == self.proxy: 
            return
        if len(data.keys()) == len(check):
            self.content.browser.proxy.remove()
            self.content.browser.proxy.add_proxy(data.get("host"),data.get("port"),data.get("username",None),data.get("password",None),only = data.get("only",[]))
            self.proxy = data

    def proxyPortStrToInt(self,data):
        if isinstance(data , dict):
            data = str(data).replace("'", '"') 
            data = dict(json.loads(data, strict=False))
        if "port" in data: 
            numeric_data = "".join(filter(str.isdigit, str(data["port"])))  
            if not numeric_data:  # Eğer boşsa, varsayılan değer ata
                numeric_data = "80" 
            numeric_data = int(numeric_data)  
            numeric_data = max(1, min(numeric_data, 65535))
            data["port"] = numeric_data
        return data
    
    def sendPageStatus(self,status):
        self.sendData("PAGE_LOAD_STATUS",status) 
        #set_pagel_load_status_callback
    def sendUrl(self,url):
        self.content.setCurrentUrl(str(url)) 
        self.sendData("CURRENT_URL",url) 
        self.sendData("PAGE_LOAD_STATUS",self.content.browser.load_page_status) 

    def sendHtml(self,html):
        self.sendData("HTML",html) 
            
    def sendCookies(self,cookies):
        self.sendData("COOKIES",cookies) 

    def sendJsResult(self,resultJs):
        self.sendData("RESULTJS",resultJs) 
 
    def sendHeadersResult(self,msg):
        print("HEADERS",msg) 
        parsed_url = urlparse(self.content.browser.url)
        domain = parsed_url.netloc
        data = None
        if domain in msg:
            data = msg[domain]
        try:  
            self.sendData("HEADERS",data) 
        except:
            pass
    
    def serialize(self): 
        res = super().serialize()
        res['op_code'] = self.__class__.op_code 
        res['proxy'] = self.proxy
        res['url'] = self.url
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        self.addallcallback()
        if "proxy" in data:
            self.setProxy(data["proxy"])
        if "url" in data:
            self.url = data
            self.content.browser.go(data["url"])
        
        return res