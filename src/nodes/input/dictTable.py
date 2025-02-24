import os,json
from qtpy.QtWidgets import QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qtpy.QtCore import Qt
from nodeeditor.utils import dumpException    
from src.node_editor.collector import register_node
from src.node_editor.node import Node
from src.node_editor.content import Content
from src.node_editor.graphics import Graphics 
from src.node_editor.constants import NODE_DICT_CREATOR
from  src.node_editor.numeric_text_line import NumericLineEdit


class DictTableContent(Content):
    add_button_call = None

    def initUI(self):
        super().initUI()

        # Tabloyu oluştur
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([ "Key", "Value"])
        self.layout.addWidget(self.table)

        # Input alanı
        self.key_edit = QLineEdit(self)
        self.key_edit.setPlaceholderText("Key (Anahtar)")
        self.layout.addWidget(self.key_edit)

        self.value_edit = QLineEdit(self)
        self.value_edit.setPlaceholderText("Value (Değer)")
        self.layout.addWidget(self.value_edit)
        

        # Butonlar
        self.addButton = QPushButton("Ekle", self)
        self.addButton.clicked.connect(self.addToTable)
        self.layout.addWidget(self.addButton)

        # Yeni Güncelle butonu
        self.updateButton = QPushButton("Güncelle", self)
        self.updateButton.clicked.connect(self.updateToTable)
        self.layout.addWidget(self.updateButton)

        self.clearButton = QPushButton("Tabloyu Temizle", self)
        self.clearButton.clicked.connect(self.clearTable)
        self.layout.addWidget(self.clearButton)

        # Tablo seçim olayını dinle
        self.table.itemSelectionChanged.connect(self.onRowSelect)

        self.setLayout(self.layout)

    def clearTable(self):
        """Tabloyu temizler"""
        self.table.setRowCount(0) 

    def onRowSelect(self):
        """Seçili satırı input alanlarına yükler"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.key_edit.setText(self.table.item(row, 0).text())
            self.value_edit.setText(self.table.item(row, 1).text())
    def updateToTable(self, input_data=None):
        """Seçili satırı günceller"""
        selected = self.table.selectedItems()
        if not selected:
            print("Lütfen güncellenecek satırı seçin!")
            return

        row = selected[0].row()

        if input_data is None:
            # Manuel güncelleme
            new_key = self.key_edit.text().strip()
            new_value = self.value_edit.text().strip()
            
            if not new_key or not new_value:
                print("Boş değerlerle güncelleme yapılamaz!")
                return
                
            input_data = {new_key: new_value}

        if isinstance(input_data, dict):
            for key, value in input_data.items():
                # Satırı güncelle
                self.table.item(row, 0).setText(str(key))
                self.table.item(row, 1).setText(str(value))
            
            self.node.sendTable()
            self.clearInputs()

    def addToTable(self, input_data=None):
        """Tabloya dict verilerini ekler"""
        if input_data is None or input_data == False:
            key = self.key_edit.text().strip()
            value = self.value_edit.text().strip()
            
            if not key or not value:
                print("Boş key veya value eklenemez.")
                return

            input_data = {key: value}  # Kullanıcıdan gelen girdiyi dict formatına çevir

        if isinstance(input_data, dict):
            for key, value in input_data.items():
                self.insertRow(key, value)
            
            self.node.sendTable()
            
        else:
            print("Yanlış veri tipi! dict formatında olmalı.")

        self.clearInputs()


    def clearInputs(self):
        """Input alanlarını temizler"""
        self.key_edit.clear()
        self.value_edit.clear()

    def insertRow(self, key, value, row=None):
        """Yeni satır ekler veya varolanı günceller"""
        if row is None:  # Yeni satır
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
        else:  # Güncelleme
            row_position = row
            if row_position >= self.table.rowCount():
                return

        self.table.setItem(row_position, 0, QTableWidgetItem(str(key)))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(value)))
         

    def addButtonCallback(self, call=None):
        self.add_button_call = call

    def setTable(self, data):
        """Dışarıdan gelen dict verisini tabloya ekler"""
        if isinstance(data, dict):
            if 'Key' in data and 'Value' in data:
                keys = data['Key']
                values = data['Value']
                if isinstance(keys, list) and isinstance(values, list) and len(keys) == len(values):
                    for key, value in zip(keys, values):
                        self.insertRow(key, value)
                else:
                    print("Hata: 'Key' ve 'Value' listeleri geçersiz veya uyumsuz.")
            else:
                for key, value in data.items():
                    self.insertRow(key, value)
        
    def deportTable(self):
        data = {}
        for col in range(self.table.columnCount()):
            key = self.table.horizontalHeaderItem(col).text()
            values = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, col)
                if item:
                    values.append(item.text())
            data[key] = values
        return data
    def serialize(self):
        """Tabloyu dict formatında kaydeder"""
        res = super().serialize() 
        res['data'] = self.deportTable()
        return res

    def deserialize(self, data, hashmap={}):
        """Kaydedilen veriyi tabloya geri yükler"""
        res = super().deserialize(data, hashmap)
        try:
            table_data = data.get('data', {})
            self.setTable(table_data) 
            return res
        except Exception as e:
            dumpException(e)
        return res


@register_node(NODE_DICT_CREATOR) 
class DictTableNode(Node):
    width = 480
    height = 640
    op_code = NODE_DICT_CREATOR
    op_title = "Dict Tablo Oluşturucu"
    content_label_objname = "dict_table_node"
    category = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    debug = True
    signal = "Temizle"

    def __init__(self, scene, parent=None):
        super().__init__(scene)
        self.addInput("Dict Girişi")
        self.addInput("KEY")
        self.addInput("VALUE")
        self.addInput("ROW")
        self.addInput("ADD SIGNAL")
        self.addInput("UPDATE SIGNAL")
        self.addInput(self.signal)
        self.addOutput("Dict Liste")
        self.addOutput("Dict")
        self.create()

    def initInnerClasses(self):
        self.content = DictTableContent(self)
        self.grNode = Graphics(self)
        self.content.addButtonCallback(self.sendTable)

    def sendTable(self):
        """Tabloyu dict olarak gönderir"""
        data_dict = self.content.deportTable()  # deportTable direkt doğru veriyi alır
        
        # 'Dict Liste' çıktısı (sütun bazlı dict)
        self.sendData("Dict Liste", data_dict)
        
        # 'Dict' çıktısı (satır bazlı tek dict)
        if 'Key' in data_dict and 'Value' in data_dict:
            result = dict(zip(data_dict['Key'], data_dict['Value']))
        else:
            result = {}
        self.sendData("Dict", result)

    def evalImplementation(self, name=None, data=None):
        """
            Düğüme veri geldiğinde tabloyu günceller  
        """
        if self.debug:
            print("name:", name)
            print("data:", type(data), data)

        if name == "KEY" and data is not None:
            self.content.key_edit.setText(str(data)) 
            _val = self.get_input("VALUE")
            if   _val is not None: 
                self.content.value_edit.setText(str(_val))

        if name == "VALUE" and data is not None:
            self.content.value_edit.setText(str(data))
            _key = self.get_input("KEY") 
            if _key is not None  :
                self.content.key_edit.setText(str(_key)) 

        if name == "ROW" and data is not None:
            try:
                # Veriyi string'e çevir
                data_str = str(data)
                valid_chars = "0123456789"
                numeric_data = "".join(filter(lambda x: x in valid_chars, data_str))
                
                if numeric_data:
                    row_index = int(numeric_data)
                    if row_index < self.content.table.rowCount():
                        self.content.table.selectRow(row_index)
                        # Seçili satır varsa input alanlarını doldur
                        selected = self.content.table.selectedItems()
                        if selected:
                            self.content.onRowSelect()
                            _key = self.get_input("KEY")
                            _val = self.get_input("VALUE")
                            if _key is not None and _val is not None:
                                self.content.key_edit.setText(str(_key))
                                self.content.value_edit.setText(str(_val))
            except Exception as e:
                print(f"Row seçim hatası: {str(e)}")


        if name == "ADD SIGNAL" and data is not None:
            _key = self.get_input("KEY")
            _val = self.get_input("VALUE")
            if _key is not None and _val is not None:
                self.content.key_edit.setText(str(_key))
                self.content.value_edit.setText(str(_val))
            self.content.addToTable()

        if name == "UPDATE SIGNAL" and data is not None:
            _row = self.get_input("ROW")
            if _row is not None:
                self.evalImplementation("ROW",_row)
            self.content.updateToTable()

        if name == "Dict Girişi" and data is not None:
            try:
                if isinstance(data ,str):
                    data = dict(json.loads( data.replace("'", '"')))
                if isinstance(data,dict):
                    self.content.clearTable() 
                    self.content.setTable(data)
                    self.sendTable()
            except:
                pass

        if name == self.signal and data is not None:
            self.content.clearTable() 
