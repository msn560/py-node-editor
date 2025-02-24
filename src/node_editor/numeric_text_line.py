from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt

class NumericLineEdit(QLineEdit):
    def __init__(self, parent=None, allow_float=False, allow_negative=False):
        super().__init__(parent)
        self.is_port_numeric = False
        self.allow_float = allow_float
        self.allow_negative = allow_negative

        self.updateValidator()  # Başlangıçta doğrulayıcıyı ayarla

    def updateValidator(self):
        """Giriş doğrulayıcıyı güncelle."""
        min_value = -2147483648  if self.allow_negative else 0  # Negatif sayı izni kontrolü
        max_value = 2147483647
        
        if self.allow_float:
            self.setValidator(QDoubleValidator(min_value, max_value, 10, self))
        else:
            self.setValidator(QIntValidator(min_value, max_value, self))

    def keyPressEvent(self, event):
        """Kullanıcının girdiği karakterleri kontrol et."""
        if event.text().isdigit() or event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            super().keyPressEvent(event)
        elif self.allow_negative and event.text() == "-" and not self.text():
            super().keyPressEvent(event)  # Negatif işaretine izin ver (başlangıçta)
        elif self.allow_float and event.text() == "." and "." not in self.text():
            super().keyPressEvent(event)  # Ondalık sayılar için nokta eklenebilir
        else:
            event.ignore()

    def setAllowFloat(self, allow: bool):
        """Ondalık sayı desteğini aç/kapat."""
        self.allow_float = allow
        self.updateValidator()  # Doğrulayıcıyı güncelle

    def setAllowNegative(self, allow: bool):
        """Negatif sayı desteğini aç/kapat."""
        self.allow_negative = allow
        self.updateValidator()  # Doğrulayıcıyı güncelle

    def portNumberVal(self):
        """Port numarası doğrulama (1-65535 aralığında)."""
        self.setValidator(QIntValidator(1, 65535, self))
        self.setPlaceholderText("Port (1-65535)")
        self.is_port_numeric = True

    def setText(self, data):
        """Gelen veriyi temizleyerek sadece sayısal kısmını alır ve uygular."""
        data = str(data).strip()

        valid_chars = "0123456789"
        if self.allow_negative:
            valid_chars += "-"
        if self.allow_float:
            valid_chars += "."

        numeric_data = "".join(filter(lambda x: x in valid_chars, data))  # Geçerli karakterleri al

        if not numeric_data or numeric_data == "-":
            numeric_data = "0"

        if self.allow_float:
            numeric_data = float(numeric_data)
        else:
            numeric_data = int(numeric_data)

        if self.is_port_numeric:
            numeric_data = max(1, min(numeric_data, 65535))  # 1-65535 sınırı

        super().setText(str(numeric_data))  # Düzeltilmiş değeri göster

    def getInt(self,default = 0 , _min = 0 , _max = 2147483647):
        data = str(super().text()).strip()
        valid_chars = "0123456789"
        if self.allow_negative:
            valid_chars += "-"
        if self.allow_float:
            valid_chars += "."

        numeric_data = "".join(filter(lambda x: x in valid_chars, data))  # Geçerli karakterleri al

        if not numeric_data or numeric_data == "-":
            numeric_data = str(default)

        if self.allow_float:
            numeric_data = float(numeric_data)
        else:
            numeric_data = int(numeric_data) 
        numeric_data = max(_min, min(numeric_data, _max))  # 1-65535 sınırı
        return numeric_data