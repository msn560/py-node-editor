CV2_CSS = """
QPushButton  {
    background: #3498db;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background: #2980b9;
}

QPushButton:pressed {
    background: #1c6da8;
}
 QLineEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                font: 14px 'Segoe UI';
                border: 2px solid #4C566A;
                border-radius: 5px;
                padding: 5px;
                selection-background-color: #88C0D0;
            }
            QLineEdit:focus {
                border: 2px solid #81A1C1;
                background-color: #3B4252;
            }
             QLabel#status_label {
                font: bold 14px;
                padding: 5px;
                border-radius: 3px;
            }
            .active { color: #27ae60; background: #e8f6f3; }
            .inactive { color: #c0392b; background: #f9ebea; }
            
QSlider::groove:horizontal {
    background: #4C566A;
    height: 6px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #81A1C1;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #D8DEE9;
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QLineEdit {
    background-color: #2E3440;
    color: #D8DEE9;
    font: 14px 'Segoe UI';
    border: 2px solid #4C566A;
    border-radius: 5px;
    padding: 5px;
    selection-background-color: #88C0D0;
    min-width: 80px;
}

QLabel {
    color: #D8DEE9;
    font: 12px 'Segoe UI';
}
QSlider::groove:horizontal {
    background: #4C566A;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #D8DEE9;
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QLabel#warning_label {
    color: #bf616a;
    font: bold 12px;
}

QCheckBox {
    color: #88C0D0;
    spacing: 5px;
}
"""