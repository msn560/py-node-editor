from typing import Optional
from typing import Optional, Union, List
from qtpy.QtGui import QColor,QFont,QFontMetrics
from qtpy.QtCore import   Qt ,QTimer
from qtpy.QtWidgets import QGraphicsEllipseItem 
from qtpy.QtGui import QBrush, QColor, QPen 
from nodeeditor.node_node import Node as OriginalNode
from nodeeditor.node_graphics_socket import SOCKET_COLORS
from nodeeditor.node_edge import Edge
from nodeeditor.node_socket import (
LEFT_TOP ,
LEFT_CENTER,
LEFT_BOTTOM ,
RIGHT_TOP,
RIGHT_CENTER,
RIGHT_BOTTOM
) 

from .graphics import Graphics
from .content import Content
from .socket_name import SocketNameLabel 

class Node(OriginalNode):
    """
    Özel düğüm sınıfı. Tüm özel düğümler bu sınıftan türetilmelidir.
    Özellikler:
    - Giriş/çıkış soketleri yönetimi
    - Veri akışı ve değerlendirme mekanizması
    - Grafiksel öğelerin yönetimi
    """
    # Sınıf seviyesinde özellikler
    icon = ""                   # Düğüm simgesi dosya yolu
    width = 400                 # Varsayılan düğüm genişliği
    height = 150                # Varsayılan düğüm yüksekliği
    op_code = 0                 # Düğüm işlem kodu (benzersiz olmalı)
    op_title = "Undefined"      # Düğüm başlığı (görünen ad)
    content_label = ""          # İçerik etiketi metni
    content_label_objname = "node_bg"  # CSS objesi adı
    category = "Default"        # Kategori (gruplama için)
    GraphicsNode_class = Graphics  # Grafik sınıfı
    NodeContent_class = Content    # İçerik widget sınıfı
    node_inputs = {}            # Giriş soket tanımları
    node_outputs = {}           # Çıkış soket tanımları
    debug = False                # Hata ayıklama modu
    signal = "Signal"           # Öncelikli sinyal adı
    runnedEvalColor_time = 1/2
    def __init__(self, scene, app = None):
        """
        Düğüm başlatıcı
        :param scene: Bağlı olduğu sahne
        :param app: Uygulama referansı
        """
        self.node_inputs = {}            # Giriş soket tanımları
        self.node_outputs = {}           # Çıkış soket tanımları
        self.app = app 
        super().__init__(scene, self.op_title, [], [])
    
    def addInput(self,name,   position = LEFT_TOP,multi_connect = False,color = None  ) -> "Node": 
        """
        Yeni giriş soketi ekler
        :param name: Soket adı (benzersiz)
        :param position: Soket konumu (LEFT_TOP, LEFT_CENTER, vs.)
        :param multi_connect: Çoklu bağlantıya izin ver
        :param color: Soket rengi (None ise otomatik) 
        :return: Node örneği (zincirleme çağrılar için)
        """
        if color is None:
            color = self.autoColorId(len(self.node_inputs.keys()))
        self.node_inputs[name] = { "name":name ,"value":None,"color":color , "position":position,"multi_connect":multi_connect }
        return self
        
    def addOutput(self,name, callback = None, position = RIGHT_TOP , multi_connect = True ,color = None) -> "Node": 
        """
        Yeni çıkış soketi ekler
        :param name: Soket adı (benzersiz)
        :param callback: Değer hesaplama fonksiyonu
        :param position: Soket konumu
        :param multi_connect: Çoklu bağlantıya izin ver
        :param color: Soket rengi (None ise otomatik)
        :return: Node örneği
        """
        if color is None:
            color = self.autoColorId(len(self.node_outputs.keys()))
        self.node_outputs[name] = { "name":name ,"value":None,"color":color ,'callback': callback ,"position":position,"multi_connect":multi_connect}
        return self
    
    def autoColorId(self,id): 
        if id > len(SOCKET_COLORS):
            return self.autoColorId(len(SOCKET_COLORS) - id)
        return id
    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER 
 
 
    def sendData(self, name, value):
        if name in self.node_outputs:
            self.node_outputs[name]['value'] = value
            self.sendEval(name, value)

    def get_input_eval(self, name): 
        if self.debug:
            print(f"DEBUG: Getting input evaluation for '{name}' in node {self.__class__.__name__}")
        
        try:
            input_id = list(self.node_inputs.keys()).index(name)
            outherNodes = self.getInputs(input_id) 
            for ix , outherNode in enumerate(outherNodes): 
                for i,otherOutputs in enumerate(outherNode.outputs): 
                    is_selfNodes = outherNode.getOutputs(i) 
                    for ix , is_selfNode in enumerate(is_selfNodes): 
                        if is_selfNode == self: 
                            output_name = list(outherNode.node_outputs.keys())[i]
                            return outherNode.evaluate(output_name)  
        except Exception as e: 
            print(f"ERROR: node.py-> get_input_eval() => {e}")
            return None
    
    def evaluate(self, outputname ): 
        return self.node_outputs[outputname]["value"]
    
    def get_input(self,name,isUp = False):
        if isUp:
            self.node_inputs[name]["value"] = self.get_input_eval(name)
        return self.node_inputs[name]["value"] 
    
    def createActiveDots(self, color="red", isRemove=True, isCreate=True):
        """Düğümün çalıştığında yeşil oluşturur, kaldırır veya rengini değiştirir."""
        try:
            if not hasattr(self, "activeDots"):
                self.activeDots = []

            # **Noktaları kaldır**
            if isRemove and self.activeDots:
                for dot in self.activeDots:
                    if dot.scene():  # Eğer sahnede varsa
                        self.grNode.scene().removeItem(dot)  # QGraphicsScene üzerinden kaldır
                self.activeDots.clear()

            # **Yeni nokta oluştur**
            if isCreate:
                dot_radius = 5  # Noktanın yarıçapı
                dot = QGraphicsEllipseItem(0, 0, dot_radius * 2, dot_radius * 2)
                dot.setBrush(QBrush(QColor(color)))  # Nokta rengi
                dot.setPen(QPen(Qt.NoPen))  # **Hata düzeltilmiş: QPen(Qt.NoPen) kullanıldı**
                
                # **Pozisyon Ayarlama**
                dot.setPos(self.width - 20, 10)

                # **Noktayı Sahneye Ekleyin**
                self.grNode.scene().addItem(dot)  # Sahneye ekle
                dot.setParentItem(self.grNode)  # Node'a bağla

                # **Listeye ekleyerek takip et**
                self.activeDots.append(dot)
        except Exception as e:
            print(e)
        

    def runnedEvalColor(self, wait=1, background="red"): 
        self.createActiveDots("green")
        QTimer.singleShot(int(wait * 1000), lambda: self.createActiveDots("red"))

    def eval(self,name = None,data=None):   
        try:
            self.runnedEvalColor(wait=self.runnedEvalColor_time)
            if name is not None and data is None:
                self.get_input(name,True) 
            elif name is not None :
                self.node_inputs[name]["value"] = data

            if name is None and data is None:
                for i,key in enumerate(self.node_inputs.keys()):
                    data = self.get_input(key,True)   
                    if data is not None:
                        self.evalImplementation(name = name,data=data)   
            if name is not None and data is not None:
                self.evalImplementation(name = name,data=data)   
        except Exception as e:
            if self.debug:
                print("ERROR:" ,self.__class__.__name__ ," :",e)

    def evalImplementation(self, name=None, data=None): 
        if self.debug:
            print(f"DEBUG: Running custom evaluation logic in node {self.__class__.__name__}")
        # Özel değerlendirme mantığı buraya gelecek
        pass

    def sendEval(self, outputname, data=None):
        """
        Bu fonksiyon, belirli bir output adına bağlı socket'lere form verilerini gönderir.
        Eğer bağlantılı socket'ler arasında 'signal' adlı bir input varsa, 
        bu socket eval fonksiyonu listenin en başına alınır (öncelikli çalıştırılır).
        """
        if self.debug:
            print(f"DEBUG: Sending evaluation from node {self.__class__.__name__} for output '{outputname}'")
        
        try:
            if not outputname in list(self.node_outputs.keys()):
                return
            # Öncelikle output ismine göre port indexini belirliyoruz
            port = list(self.node_outputs.keys()).index(outputname)
            
            if not self.outputs or port >= len(self.outputs):
                if self.debug:
                    print(f"DEBUG: Invalid port for output '{outputname}' in node {self.__class__.__name__}")
                return
            
            other_sockets_names = []
            other_sockets_nodes = []
            
            other_signal_sockets_names = []
            otherr_signal_sockets = []
            
            # Bağlı output'lardan gelen socket'leri toplayalım
            # getOutputs(port) metodu ilgili port için bağlı output'ları döndürür
            for outputs in self.getOutputs(port):
                # Her output'un input socket'leri üzerinde döngü
                for ix, nextInputSocket in enumerate(outputs.inputs): 
                    for edge in nextInputSocket.edges:
                        # edge.getOtherSocket(self) --> self'den farklı diğer socket'i alır
                        other_socket = edge.getOtherSocket(self)
                        self_socket = edge.getOtherSocket(outputs.inputs[ix])

                        # Eğer self_socket'un node'u bizim node'umuzsa
                        if self_socket.node == self:
                            othername = list(other_socket.node.node_inputs.keys())[ix]
                            if other_socket.node in other_sockets_nodes:
                                index = other_sockets_nodes.index(other_socket.node)
                                if other_sockets_names[index] == othername:
                                    break
                            # other_socket'un node_inputs'inde ilgili index'teki key'i alıyoruz
                           
                            if othername == other_socket.node.signal: 
                                if other_socket.node in otherr_signal_sockets:
                                    index = otherr_signal_sockets.index(other_socket.node)
                                    if other_signal_sockets_names[index] == othername:
                                        continue

                                other_socket.node.eval(othername,data)
                                otherr_signal_sockets.append(other_socket.node)
                                other_signal_sockets_names.append(othername)
                                continue
                            if self.debug:
                                print(f"DEBUG: Sending data to input '{othername}' in node {other_socket.node.__class__.__name__}") 
                            other_sockets_names.append(othername)
                            # Diğer node'un eval fonksiyonunu listeye ekle
                            other_sockets_nodes.append(other_socket.node)
             
            
            # Son olarak, toplanan eval fonksiyonlarını sırayla çağırıyoruz
            if self.debug:
                print("other_sockets_names",other_sockets_names)
            for i, name in enumerate(other_sockets_names):
                if callable(other_sockets_nodes[i].eval):
                    other_sockets_nodes[i].eval(name, data)
                    
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Error in sendEval of node {self.__class__.__name__}: {e}")

        
    def id_to_color_id (self,id):
        if id > len(SOCKET_COLORS):
            return self.id_to_color_id( id - len(SOCKET_COLORS))
        return id 
    
    def create(self ):  
        self.initSockets()  
        self.writeSocketNames()   
 
    
    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code 
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id) 
        return res
     
    
    
    def writeSocketsNames(self):
        pass
    
    def initSockets(self, inputs: list=[], outputs: list=[], reset: bool=True):   
        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove grSockets from scene
                for socket in (self.inputs+self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []
        
        # create new sockets
        counter = 0 
        left = [LEFT_TOP,LEFT_CENTER,LEFT_BOTTOM]
        for key, item in self.node_inputs.items():
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=item["position"],
                socket_type=item["color"], multi_edges=item["multi_connect"],
                count_on_this_node_side=len(self.node_inputs.items()), is_input=True
            ) 
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for key, item in self.node_outputs.items():
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=item["position"],
                socket_type=item["color"], multi_edges=item["multi_connect"],
                count_on_this_node_side=len(self.node_inputs.items()), is_input=False
            )  
            counter += 1

            self.outputs.append(socket)


    def writeSocketNames(self):
        max_left = 10
        max_right = 10
        left = [LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM]
        
        # Önce etiket genişliklerini hesapla
        font = QFont()
        font.setPointSize(10)  # SocketNameLabel ile aynı yazı tipi boyutu
        fm = QFontMetrics(font)
        
        # Maksimum genişlikleri hesapla
        for ix in range(2):  # 0: inputs, 1: outputs
            keys = list(self.node_inputs.keys() if ix == 0 else self.node_outputs.keys())
            for name in keys:
                text_width = fm.width(name)
                if ix == 0 and text_width > max_left:
                    max_left = text_width+7
                elif ix == 1 and text_width > max_right:
                    max_right = text_width+7
        
        if len(self.node_inputs.keys())>0:
            self.width +=   max_left + 15
        if len(self.node_outputs.keys())>0:
            self.width +=   max_right + 15  
        self.height += 20
        self.content.lbl.setFixedWidth(self.width)
        self.content.setFixedWidth(self.width)
        self.content.layout.setContentsMargins(max_left + 10, 10, max_right + 10, 10)
        self.grNode.setNodeSize(self.width, self.height)
        self.initSockets()  # Soketleri yeni boyuta göre yeniden oluştur 
        self.createActiveDots()
        # Etiketleri yeni pozisyonlara yerleştir
        sockets = [self.inputs, self.outputs]
        sockets_data = [self.node_inputs, self.node_outputs]
        
        for ix, s in enumerate(sockets):
            for i, socket in enumerate(s):
                name = list(sockets_data[ix].keys())[i]
                x, y = socket.node.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
                color = SOCKET_COLORS[socket.socket_type]
                socket_name_label = SocketNameLabel(str(name), color.name(QColor.HexRgb))
                socket_name_label.label.adjustSize()  # Etiket boyutunu güncelle
                
                y -= 8
                
                if socket.position in left:
                    socket_name_label.label.setAlignment(Qt.AlignLeft)
                    x += 7
                else:
                    socket_name_label.label.setAlignment(Qt.AlignRight)
                    x -= socket_name_label.label.width()  # Sağa hizala
                    x -= 7
                socket_name_label.setPos(x, y)
                socket_name_label.setParentItem(socket.node.grNode)

    def onInputChanged(self, socket=None):
        if self.debug:
            print("%s::__onInputChanged" % self.__class__.__name__)
        self.eval()
         