# py-node-editor
Bu proje, PyQt tabanlı esnek ve modüler bir node editor uygulamasıdır. Amacı, veri akışı, görsel programlama ve özelleştirilebilir işlem zincirleri oluşturmak isteyen geliştiriciler için başlangıç düzeyinde bir altyapı ve örnek kodlar sağlamaktır. 
Bu proje, PyQt tabanlı esnek ve modüler bir node editor uygulamasıdır. Amacı, veri akışı, görsel programlama ve özelleştirilebilir işlem zincirleri oluşturmak isteyen geliştiriciler için güçlü bir altyapı sağlamaktır.

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

#  Kullanım
Node Geliştirme:
Kendi node’larınızı oluşturmak için Node sınıfını temel alarak; soket ekleme, eval (değerlendirme) ve veri gönderme metotlarını özelleştirebilirsiniz.

#  HTTP API Entegrasyonu:
HTTP Server Node sayesinde, uygulama içerisindeki verileri yerel sunucu üzerinden API olarak sunabilir; örneğin, ekran görüntülerini opencv ve pyautogui ile alıp PNG formatında dışarı aktarabilirsiniz.

 # Prototip ve Geliştirme:
Hızlı prototipleme ve görsel programlama deneyimi için tasarlanmış olan bu yapı, kullanıcı dostu arayüzü ve modüler mimarisi sayesinde genişletilebilir.

 

# Diğer bağımlılıklar:
nodeeditor, ilgili içerik ve grafik sınıfları 
Kurulum için gereken bağımlılıklar ```document/pip/install.txt``` dosyasına göz atın.

## Thanks :
 
 [Pavel Křupala](https://gitlab.com/pavel.krupala/pyqt-node-editor)
 [Node Editor in Python Tutorial Series](https://www.youtube.com/watch?v=xbTLhMJARrk&list=PLZSNHzwDCOggHLThIbCxUhWTgrKVemZkz)
 
  


