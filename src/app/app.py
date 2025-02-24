import os,cv2
from src.languages import LANGUAGES
from src.window.main_window import MainWindow
class App:
    selected_lang = "tr"
    main_window = None
    fixSize = None , None
    minSize = 720 , 480
    maxiSize = None , None
    start_pos = "center"
    langs = LANGUAGES
    lang = LANGUAGES[selected_lang]
    root = os.path.dirname(os.path.abspath(__file__)) + "/../../"
    whell_callBack = None
    close_callback = []
    is_weel = True
    cam_cv2 = None
    def __init__(self):
        pass
        
    def run(self):
        self.main_window = MainWindow(self)
        self.main_window.show()
        
    def translate(self, key):
        return getattr(self.lang, key)
    
    def addWheelEventCallBack(self,callback): 
        self.whell_callBack = callback

    def wheelEvent(self,event):  
        if callable(self.whell_callBack): 
            self.whell_callBack(event)
    def setWeelStatus(self,status):
        self.is_weel = status

    def getWeelStatus(self ):
        return self.is_weel
    
    def addCloseCallBack(self,call):
        if callable(call):
            self.close_callback.append(call)

    def camStart(self):
        if self.cam_cv2 is None:
            self.cam_cv2 = cv2.VideoCapture(0)
        return self.cam_cv2
    def camStop(self):
        if self.cam_cv2 is not None:
            self.cam_cv2.release() 
            self.cam_cv2 = None
        return self.cam_cv2