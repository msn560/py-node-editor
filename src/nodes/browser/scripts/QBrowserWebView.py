from typing import Optional, List
from PyQt5.QtCore import QSize,QByteArray,QDateTime 
from qtpy.QtCore import Qt,QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor  
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import * 
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from lxml import etree
from PyQt5.QtNetwork import QNetworkCookie  
from  .debug_listener import BrowserDebugListen
from qtpy.QtGui import   QWheelEvent
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtGui import QCloseEvent

class CustomWebView(QWebEngineView):
    def wheelEvent(self, event:QWheelEvent): 
        """Handle mouse wheel events for scrolling or zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Use default zooming when Ctrl is pressed
            super().wheelEvent(event)
        else:
            # Scroll the page with correct direction
            delta = event.angleDelta().y()
            """print(f"Wheel event detected: delta = {delta}")"""
            # Use asynchronous JavaScript execution
            self.page().runJavaScript(f"window.scrollBy(0, {-delta});")

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super(CustomWebEnginePage, self).__init__(profile, parent)  
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)


class ProxyInterceptor(QWebEngineUrlRequestInterceptor):
    block_all  = False
    """Özel Proxy Interceptor (Sadece belirli sitelerde proxy çalıştırmak için)"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.proxies = []

    def setProxies(self, proxies):
        self.proxies = proxies  # Güncellenmiş proxy listesi

    def setBlockAll(self, block: bool):
        """Tüm istekleri engellemek için flag değerini ayarlar."""
        self.block_all = block
    def interceptRequest(self, info):
        """Her isteği kontrol edip, belirli domainler için proxy uygular."""
        url = info.requestUrl().toString()
        if self.parent.browser.node.debug:
            print("interceptRequest > url",url)
        domain = self.getDomain(url)
        if self.parent.browser.node.debug:
            print("interceptRequest > domain",domain)
        if self.block_all: 
            isBlock = False
            for proxy in self.proxies: 
                if len(proxy["only"]) == 0 :
                    isBlock = True
                    break
                if domain in proxy["only"]:
                    isBlock = True
                    break
            if isBlock:
                info.block(True)  # İsteği engelle
        else:
            info.block(False)  # İsteğe izin ver

        matching_proxy = None
        for proxy in self.proxies:
            if len(proxy["only"]) == 0 or domain in proxy["only"]:
                matching_proxy = proxy
                break
        
        if matching_proxy is not None:
            if self.parent.browser.node.debug:
                print("proxy only", matching_proxy["only"])
                print("proxy domain", domain)
                print(f"🔹 Proxy Kullanılıyor: {matching_proxy['host']}:{matching_proxy['port']} → {url}")
            proxy_class = QNetworkProxy(
                matching_proxy.get("type", QNetworkProxy.HttpProxy),
                matching_proxy.get("host", "127.0.0.1"),
                matching_proxy.get("port", 80)
            )
            if matching_proxy.get("username") and matching_proxy.get("password"):
                proxy_class.setUser(matching_proxy.get("username"))
                proxy_class.setPassword(matching_proxy.get("password"))
            QNetworkProxy.setApplicationProxy(proxy_class)
        else: 
            QNetworkProxy.setApplicationProxy(QNetworkProxy())

    def getDomain(self, url):
        parsed = urlparse(url.strip())  
        return parsed.netloc if parsed.netloc else None
    
    def remove_proxy(self):
        self.proxies = []
   
class BrowserProxyManager:
    def __init__(self,browser ):
        self.browser = browser
        self.driver = browser.driver
        self.driver_profile =  browser.driver_profile
        self.proxy = []
        self.interceptor = ProxyInterceptor(self)
        self.driver_profile.setUrlRequestInterceptor(self.interceptor)
    """
     
    0    DefaultProxy 
    1    Socks5Proxy  
    2    NoProxy  
    3    HttpProxy  
    4    HttpCachingProxy 
    5    FtpCachingProxy 

    """  
    def add_proxy(self, host: str = "127.0.0.1", port: int = 8080, username: Optional[str] = None, password: Optional[str] = None, 
                  proxy_type: int = QNetworkProxy.HttpProxy, only: List[str] = []):
        """Belirtilen proxy'yi listeye ekler"""
        new_only = [self.browser.getDomain(o) for o in only if self.browser.getDomain(o)]
        self.proxy.append({
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "type": proxy_type,
            "only": new_only
        })
        self.interceptor.setProxies(self.proxy)  

    def remove (self):
        self.proxy = []
        self.interceptor.remove_proxy()
  
class QBrowser(): 
    html_content =""
    url = "https://www.youtube.com/"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    cache_callback = None
    cache_cookie_callback = None
    current_url_callback = None
    headers_callback =None
    cookie_caches = {}
    inject_js_data  = {}
    proxy  = list()
    is_apply_proxy = False
    load_page_status = False
    load_page_status_callback = None
    
    def __init__(self, parent=None): 
        self.node = parent
        self.driver = CustomWebView() 
        self.driver_profile = QWebEngineProfile.defaultProfile()
        self.driver_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.driver_profile.setCachePath("")  # Önbelleği devre dışı bırak
        self.driver_profile.setPersistentStoragePath("")  # Depolama alanını sıfırla
        # Güvenlik ayarlarını devre dışı bırak
        self.driver_profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.driver_profile.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.driver_profile.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        self.driver_profile.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)  
        """
        self.interceptor = MyInterceptor(headers_callback=self.get_page_headers)
        self.driver_profile.setUrlRequestInterceptor(self.interceptor)""" 
        self.driver_cookie_store = self.driver_profile.cookieStore()
        self.driver_cookie_store.cookieAdded.connect(self.handle_cookies)  
        self.proxy = BrowserProxyManager(self)
        self.driver_page = CustomWebEnginePage(self.driver_profile, self.driver)
        self.driver.setPage(self.driver_page)
        self.driver_page.profile().setHttpUserAgent(self.user_agent)
        self.driver.setContextMenuPolicy(Qt.NoContextMenu) 
        self.driver.loadStarted.connect(self.on_load_started)
        self.driver.loadFinished.connect(self.on_load_finished) 
        self.driver.setStyleSheet("QWebEngineView { border-radius: 10px; }")
        self.driver.hide() 
        self.driver.urlChanged.connect(self.on_url_changed)

        self.debug_listener = BrowserDebugListen(self)
        self.debug_listener.thread.data_updated.connect(self.debug_listener_handle)
     

    def debug_listener_handle (self,data):
        self.get_page_headers(data)

    def go(self, url:str): 
        domain = self.getDomain(url) 
        if domain is None:
            return 
        self.url = url  
        self.driver.setUrl(QUrl(url))

    def setBlockAll(self, block: bool):
        self.proxy.interceptor.setBlockAll(block)
    
    def isBlock(self, block: bool):
        return  self.proxy.interceptor.block_all
    
    def getDomain(self,url):
        parsed = urlparse(url.strip())  
        if not parsed.scheme:  # Eğer "http" veya "https" yoksa otomatik ekle
            url = "https://" + url
            parsed = urlparse(url)  # Tekrar parse et 
        if not parsed.netloc:  # Eğer hala geçersizse, işlemi iptal et
            print("Geçersiz URL:", url)
            return None
        return parsed.netloc
    
    def on_load_started(self):
        self.load_page_status = False
        pass

    def on_load_finished(self, success):
        self.driver.show()
        self.load_page_status = success
        if callable(self.load_page_status_callback):
            self.load_page_status_callback(success)
        if success:
            self.get_page_html()
            self.get_cookies() 
         
    def set_pagel_load_status_callback (self,callback = None):
        self.load_page_status_callback = callback

    def set_headers(self,headers):
        self.interceptor.set_headers_dict = headers
    
    def update_headers(self,headers):
        if self.interceptor.set_headers_dict is None:
            self.interceptor.set_headers_dict = {}
        self.interceptor.set_headers_dict.update(headers)
        
    
    def on_url_changed(self, url,callBack = None):
        
        if callBack is not None:
            self.current_url_callback = callBack 
            if url =="":
                return
        if hasattr(url,"toString"):
            self.url = url.toString()
        else:
            self.url = str(url) 
        if callable(self.current_url_callback ):
            self.current_url_callback(self.url)
        js = f"""
            window.addEventListener("load", function() {{
                console.log("Sayfa ve tüm kaynaklar tamamen yüklendi!");
                window.pyqt6Callback();  // Burada Python fonksiyonuna callback yapıyoruz
            }});
            """ 
        self.driver.page().runJavaScript(js, self.waitForPageLoad)


    def headersAddCallBack(self,callBack = None):
        if callable(callBack):
            self.headers_callback = callBack 
    

    def get_page_headers(self,data = {}):
         if callable(self.headers_callback):
             self.headers_callback(data)

    def get_page_html(self,callBack = None):
        if callBack is None:
            if self.cache_callback is not None:
                callBack = self.cache_callback
            else:
                callBack = self.handle_html 
        else:
            self.cache_callback = callBack 

        self.driver.page().toHtml(callBack)
        self.driver.page().toHtml(self.handle_html)

    def handle_html(self, html): 
        self.html_content = html  

    def get_cookies(self, callBack=None): 
        if callable(callBack):
            self.cache_cookie_callback = callBack 


    def handle_cookies(self, cookies):
        """Çerezler yüklendikten sonra işleme yapılır."""
        try:
            cookie_dict = {}
            name = cookies.name().data().decode()
            val = cookies.value().data().decode()
            cookie_dict[name] = val 

            parsed_url = urlparse(self.url)
            if parsed_url.netloc not in self.cookie_caches:
                self.cookie_caches[parsed_url.netloc] = dict()

            self.cookie_caches[parsed_url.netloc].update(cookie_dict)

            # Eğer callback varsa, gönder
            if callable(self.cache_cookie_callback):
                self.cache_cookie_callback(self.cookie_caches[parsed_url.netloc]) 
        except Exception as e:
            print("cokkie error",e)

    def set_cookie(self, name, value, domain):
        """Çerez ekleme fonksiyonu"""
        cookie = QNetworkCookie()
        cookie.setName(name.encode())
        cookie.setValue(value.encode())
        cookie.setDomain(domain)
        cookie.setExpirationDate(QDateTime.currentDateTime().addDays(7))
        cookie.setSecure(True)
        cookie.setHttpOnly(True)
        self.driver_cookie_store.setCookie(cookie)

    def waitForPageLoad(self, status = False):
        self.inject_javascript(True)

    def inject_javascript(self ,run = False, script = None,result_call= None): 
        if script is not None:
            self.inject_js_data["script"] = script
        if callable(result_call):
            self.inject_js_data["result_call"] = result_call

        if run:
            if not "script" in self.inject_js_data:
                return None
            if not "result_call" in self.inject_js_data:
                return None
            try: 
                self.driver.page().runJavaScript(self.inject_js_data["script"],self.inject_js_data["result_call"]) 
            except Exception as e:
                self.inject_js_data["result_call"]("ERROR:{}".format(e))
                pass
    def closeEvent(self,event): 
        self.driver_profile.deleteLater()
        self.driver.close()
 

def is_html(content):
    """String'in HTML olup olmadığını kontrol eder."""
    if not isinstance(content, str) or not content.strip():
        return False  # Boş veya string değilse HTML değildir.

    soup = BeautifulSoup(content, "html.parser")
    return bool(soup.find())  # İçinde en az bir HTML etiketi varsa True döner.
