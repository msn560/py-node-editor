import os
from qtpy.QtWidgets import QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qtpy.QtCore import Qt
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_LIST_CREATOR
from  src.node_editor.numeric_text_line import NumericLineEdit


class ListCreatorContent(Content):
    add_button_call = None

    def initUI(self):
        super().initUI()   

        # Tabloyu oluştur
        self.table = QTableWidget(self)
        self.table.setColumnCount(1)  # 1 sütun
        self.table.setHorizontalHeaderLabels(['Veri'])  # Başlık ekle
        self.layout.addWidget(self.table)

        # Input için QLineEdit oluştur
        self.edit = QLineEdit(self)
        self.layout.addWidget(self.edit)

        # Buton ekle
        self.addButton = QPushButton("Ekle", self)
        self.addButton.clicked.connect(self.addToTable)
        self.layout.addWidget(self.addButton)

        # Temizle butonunu ekle
        self.clearButton = QPushButton("Tabloyu Temizle", self)
        self.clearButton.clicked.connect(self.clearTable)  # Temizleme fonksiyonuna bağla
        self.layout.addWidget(self.clearButton)

        self.setLayout(self.layout)

    def clearTable(self):
        """Tabloyu temizle"""
        self.table.setRowCount(0)  # Satırları sıfırla (tabloyu temizle)

    def addToTable(self, input_value=None):
        """Tabloya input ekle"""
        if input_value is None or input_value == False:
            input_value = self.edit.text()  # QLineEdit'den veriyi al

        # Eğer bir liste verilmişse, her elemanı tabloya ekle
        if isinstance(input_value, list):
            for input in input_value:
                self.addToTable(input)
            return

        # Burada değerlerin tipini kontrol ediyoruz
        if isinstance(input_value, (int, float, str)):
            input_value = str(input_value).strip()  # Değeri string'e çevir ve boşlukları temizle

            if input_value != "":  # Eğer boş değilse
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(input_value))  # Yeni veriyi tabloya ekle
                self.edit.clear()  # Giriş alanını temizle

                # Eğer bir callback fonksiyonu varsa, çağır
                if callable(self.add_button_call):
                    self.add_button_call(input_value)
            else:
                print("Boş değer eklenemez.")

    def addButtonCallback(self, call=None):
        self.add_button_call = call

    def setTable(self, data):
        if not isinstance(data, list):
            return
        for i, val in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(val)))  # Veriyi string olarak tabloya ekle

    def serialize(self):
        res = super().serialize()
        # Tabloyu bir şekilde serialize edebiliriz, örneğin tabloyu string'e çevirebiliriz
        data = []
        for row in range(self.table.rowCount()):
            data.append(self.table.item(row, 0).text())
        res['data'] = data
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            data = data['data']
            for item in data:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(item))
            return res
        except Exception as e:
            dumpException(e)
        return res


@register_node(NODE_LIST_CREATOR) 
class ListCreatorNode(Node):
    width = 400
    height = 300 
    op_code = NODE_LIST_CREATOR
    op_title = "Liste Oluşturucu"
    content_label_objname = "list_creator_node"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    debug = True
    signal = "Temizle"

    def __init__(self, scene, parent=None): 
        super().__init__(scene)  
        self.addInput("Veri Girişi")  
        self.addInput(self.signal)  
        self.addOutput("Liste")  
        self.create() 

    def initInnerClasses(self):
        self.content = ListCreatorContent(self)
        self.grNode = Graphics(self) 
        self.content.addButtonCallback(self.sendTable)

    def sendTable(self, data):
        # Burada listeyi gönderiyoruz
        data = []
        for row in range(self.content.table.rowCount()):
            data.append(self.content.table.item(row, 0).text())
        self.sendData("Liste", data)

    def evalImplementation(self, name=None, data=None):
        if self.debug:
            print("name", name)
            print("data", type(data), data)

        if name == "Veri Girişi" and data is not None:
            self.content.addToTable(data) 
            self.sendTable(data)

        if name == self.signal and data is not None: 
            self.content.clearTable() 
            self.sendData("Liste", []) 
        pass
