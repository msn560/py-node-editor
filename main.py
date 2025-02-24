import   sys  
from qtpy.QtWidgets import QApplication 
from src.app.app import App

QTWEB_DEBUG_PORT = "1250"
QTWEB_DEBUG_PORT_START = True
 


if __name__ == '__main__':
    if QTWEB_DEBUG_PORT_START and "--remote-debugging-port" not in sys.argv:
        sys.argv.append("--remote-debugging-port=" + QTWEB_DEBUG_PORT) 

    qt_app = QApplication(sys.argv)
    _app = App()
    _app.run()
    sys.exit(qt_app.exec_())
    