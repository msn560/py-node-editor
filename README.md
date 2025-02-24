# py-node-editor
Bu proje, PyQt tabanlı esnek ve modüler bir node editor uygulamasıdır. Amacı, veri akışı, görsel programlama ve özelleştirilebilir işlem zincirleri oluşturmak isteyen geliştiriciler için başlangıç düzeyinde bir altyapı ve örnek kodlar sağlamaktır. 
Bu proje, PyQt tabanlı esnek ve modüler bir node editor uygulamasıdır. Amacı, veri akışı, görsel programlama ve özelleştirilebilir işlem zincirleri oluşturmak isteyen geliştiriciler için güçlü bir altyapı sağlamaktır.
![image](https://github.com/msn560/py-node-editor/blob/main/document/screenshots/cv2_1.png)
#  Özellikler
Modüler Node Yapısı:
Tüm özel node’lar, temel Node sınıfından türetilerek; giriş/çıkış soketleri, veri akışı, değerlendirme mekanizması ve grafiksel öğeler gibi ortak özellikleri otomatik olarak kullanır.

#  Dinamik Soket Yönetimi:
Her node, belirlenen konumlarda (örneğin LEFT_TOP, RIGHT_CENTER vb.) giriş ve çıkış soketlerine sahiptir. Bu sayede farklı node’lar arasında kolayca veri alışverişi sağlanır.

#  Örnek Node’lar:

  ButtonInput Node:
Kullanıcı arayüzünde metin girişi (QLineEdit) ve buton (QPushButton) ile etkileşimli veri gönderimi sağlar.
  HTTP Server Node:
QThread üzerinde çalışan senkron bir HTTP sunucusudur. Diğer node’lardan (veya ekran görüntüsü gibi harici verilerden) gelen veriyi, uygun header bilgileriyle HTTP isteklerine yanıt olarak döndürür. Bu sayede, örneğin opencv-python ve pyautogui ile yakalanan ekran görüntüleri PNG formatında dışarı aktarılabilir.
Esneklik ve Genişletilebilirlik:
Proje, node’lar arasında veri akışını dict, byte, list, str gibi farklı veri tipleriyle yönetmeye olanak tanır. Ayrıca, farklı işlevler için router node gibi eklentiler oluşturulabilir.

 Kullanım
Node Geliştirme:
Kendi node’larınızı oluşturmak için Node sınıfını temel alarak; soket ekleme, eval (değerlendirme) ve veri gönderme metotlarını özelleştirebilirsiniz.
 
  Prototip ve Geliştirme:
Hızlı prototipleme ve görsel programlama deneyimi için tasarlanmış olan bu yapı, kullanıcı dostu arayüzü ve modüler mimarisi sayesinde genişletilebilir.

```python
import os
from qtpy.QtWidgets import QLineEdit 
from qtpy.QtCore import Qt 
from nodeeditor.utils import dumpException    #debug
from src.node_editor.collector import register_node # otomatik toplayıcı fonksiyon
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics
from src.node_editor.constants import NODE_INPUT  # düğüm için benzersiz tanımlayıcı

class lineTextContent(Content): # düğümün görsel arayüzü
    def initUI(self):
        super().initUI()   
        self.edit = QLineEdit("", self)
        self.edit.setAlignment(Qt.AlignLeft) 
        self.edit.setObjectName(self.node.content_label_objname) 
        self.layout.addWidget(self.edit)

        self.setLayout(self.layout)

    def serialize(self): # düğüm verilerini kson dosyasına işle
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}): # geri yükleme
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(NODE_INPUT) 
class InputNode(Node): # src/node_editor/node.py Node sınıfından türeyen Düğümler
    width = 400
    height = 80 
    op_code = NODE_INPUT   # src/node_editor/constants.py den gelen benzersiz tanımlayıcı
    op_title = "Yazı"
    content_label_objname = "line_text"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__))) # kategorize etmek için bulunulan dosya adını kullan
    def __init__(self, scene,parent=None ): 
        super().__init__(scene)  
        self.addInput("Giriş"  )  #  giriş soketleri
        self.addOutput("Çıkış")  # çıkış soketleri
        self.create() 
         

    def initInnerClasses(self):
        self.content = lineTextContent(self)
        self.grNode = Graphics(self)
        self.content.edit.textChanged.connect(self.onInputTextChanged) 

    def evalImplementation(self, name=None, data=None): # gelen verileri giriş değerine göre işleme 
        self.content.edit.setText(str(data)) 

    def onInputTextChanged(self ):
        text = self.content.edit.text()   
        self.sendData("Çıkış",text) #verileri sonraki bağlı node gönder
 ```
# Bağımlılıklar:

```bash
pip install pyqt5
pip install qtpy 
pip install validators
pip install PyQtWebEngine 
pip install aiohttp 
pip install PySocks
pip install requests[socks]
pip install websocket-client requests
pip install beautifulsoup4 lxml
pip install opencv-python
pip install PyAutoGUI


# Node Editor  https://gitlab.com/pavel.krupala/pyqt-node-editor :
> pip install document/archive/nodeeditor/pyqt-node-editor-master.zip
$ pip install git+https://gitlab.com/pavel.krupala/pyqt-node-editor.git

 ```
 
Kurulum için gereken bağımlılıklar ```document/pip/``` dosyasına göz atın.

## Thanks :
 
 [Pavel Křupala](https://gitlab.com/pavel.krupala/pyqt-node-editor)
 [Node Editor in Python Tutorial Series](https://www.youtube.com/watch?v=xbTLhMJARrk&list=PLZSNHzwDCOggHLThIbCxUhWTgrKVemZkz)
 
  


