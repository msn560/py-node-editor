import json
from nodeeditor.utils import dumpException 
from src.node_editor.content import Content  
from qtpy.QtWidgets import (QLineEdit, QPushButton, 
                           QHBoxLayout, QVBoxLayout,
                           QPlainTextEdit, QScrollBar,QTableWidget,QTableWidgetItem)
from qtpy.QtWidgets import  QFileDialog,QTabWidget,QWidget,QSizePolicy

class QTBROWSER_HeadersContent(Content): 
    table_data = {} 
    def initUI(self):
        super().initUI()

        # **Sekme (Tab) Sistemi Ekleniyor**
        self.tab_widget = QTabWidget(self)
        #self.tab_widget.setStyleSheet(  self.table_css)
        # **Request Sekmesi**tab_css
        self.request_tab = QWidget()
        self.request_layout = QVBoxLayout(self.request_tab)
        self.request_table = QTableWidget(self)
        self.request_table.setColumnCount(4)
        self.request_table.setHorizontalHeaderLabels(["URL", "STATUS", "KEY", "VALUE"]) 
        self.request_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.request_layout.addWidget(self.request_table)
        self.request_tab.setLayout(self.request_layout)

        # **Response Sekmesi**
        self.response_tab = QWidget()
        self.response_layout = QVBoxLayout(self.response_tab)
        self.response_table = QTableWidget(self)
        self.response_table.setColumnCount(4)
        self.response_table.setHorizontalHeaderLabels(["URL", "STATUS", "KEY", "VALUE"]) 
        self.response_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.response_layout.addWidget(self.response_table)
        self.response_tab.setLayout(self.response_layout)

        # **Sekmeleri Ekle**
        self.tab_widget.addTab(self.request_tab, "Request Headers")
        self.tab_widget.addTab(self.response_tab, "Response Headers")

        # **Farklı Kaydet Butonu**
        self.save_button = QPushButton("Farklı Kaydet")
        self.save_button.clicked.connect(self.save_data)

        # **Layout Güncelle**
        self.layout.addWidget(self.tab_widget)  # Sekmeleri ana layout'a ekle
        self.layout.addWidget(self.save_button)  # Farklı Kaydet butonu
        
         
    def updateTable(self, dict_data):
        try:
            if not isinstance(dict_data, list):
                return
                
            self.table_data = dict_data  # Veriyi kaydet
            
            # Mevcut verileri temizle
            self.request_table.setRowCount(0)
            self.response_table.setRowCount(0)
            
            for data in dict_data:
                url = data.get("url","N/A")
                status = str(data.get("status","N/A"))
                
                # Request headers
                for key, value in data.get("requestHeaders", {}).items():
                    row = self.request_table.rowCount()
                    self.request_table.insertRow(row)
                    self.request_table.setItem(row, 0, QTableWidgetItem(url))
                    self.request_table.setItem(row, 1, QTableWidgetItem(status))
                    self.request_table.setItem(row, 2, QTableWidgetItem(str(key)))
                    self.request_table.setItem(row, 3, QTableWidgetItem(str(value)))
                
                # Response headers
                for key, value in data.get("response_headers", {}).items():
                    row = self.response_table.rowCount()
                    self.response_table.insertRow(row)
                    self.response_table.setItem(row, 0, QTableWidgetItem(url))
                    self.response_table.setItem(row, 1, QTableWidgetItem(status))
                    self.response_table.setItem(row, 2, QTableWidgetItem(str(key)))
                    self.response_table.setItem(row, 3, QTableWidgetItem(str(value)))

        except Exception as e:
            print("Table update error:", e)
    def save_data(self):
        """ Kullanıcının seçtiği yere JSON olarak veriyi kaydeder. """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(None, "Farklı Kaydet", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if file_path:  # Kullanıcı bir dosya seçtiyse
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(self.table_data, file, ensure_ascii=False, indent=4)
                print(f"Veri başarıyla kaydedildi: {file_path}")
            except Exception as e:
                print(f"Dosya kaydedilirken hata oluştu: {e}")
    def onSendClicked(self):
        text = self.input_edit.text()
        if text:
            self.updateOutput.emit(f">> {text}")
            self.input_edit.clear()

    def updateOutputView(self, text):
        """Çıktı alanına yeni metin ekler"""
        self.output_view.setPlainText(text)
        self.output_view.verticalScrollBar().setValue(
            self.output_view.verticalScrollBar().maximum()
        )

    def serialize(self):
        res = super().serialize()
        res['table_data'] =self.table_data
        return res

    def deserialize(self, data, hashmap={}):
        super().deserialize(data, hashmap)
        try:
            self.updateTable(data.get('table_data', [])) 
        except Exception as e:
            dumpException(e)
        return True
