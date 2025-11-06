import sys
from logging import PlaceHolder

from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QApplication, QHBoxLayout, QLabel, QLineEdit

from dialog_title_bar import DialogTitleBar

class TambahBarangBaru(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(800, 500)
        self.setModal(True)

        root_layout = QVBoxLayout()
        root_widget= QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        title_bar = DialogTitleBar("Tambah Produk Baru", self)
        main_layout.addWidget(title_bar)

        main_layout.addStretch()

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setStyleSheet("""
            background-color: #000000;
        """)

class WidgetKecil(QWidget):
    def __init__(self, ikon_path, label_text, placeholder_text):
        super().__init__()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(10)

        judul_layout = QHBoxLayout()
        judul_layout.setSpacing(10)
        judul_layout.setContentsMargins(0,0,0,0)

        icon = QLabel()
        icon.setPixmap(QPixmap(ikon_path))
        icon.setFixedSize(25,25)
        icon.setScaledContents(True)
        judul_layout.addWidget(icon)

        label = QLabel()
        label.setText(label_text)
        label.setStyleSheet("""
            color: #90EE90;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        judul_layout.addWidget(label)

        content_layout.addLayout(judul_layout)

        self.data = QLineEdit()
        self.data.setFixedHeight(45)
        self.data.setPlaceholderText(placeholder_text)
        self.data.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #FFFFFF;
                font-size: 14px;
                selection-background-color: #90EE90;
                selection-color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }
            QLineEdit:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }
        """)
        content_layout.addWidget(self.data)

        self.setLayout(content_layout)
        self.setContentsMargins(0,0,0,0)

    def get_data(self):
        return self.data.text()

class Widgetutama(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(200,200)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0,0,0,0)

        self.tombol = QPushButton("Tambah Produk Baru")
        self.tombol.setFixedSize(100,50)
        root_layout.addWidget(self.tombol)

        self.setLayout(root_layout)

        self.tombol.clicked.connect(self.clik)

    def clik(self):
        dialog = TambahBarangBaru(self)
        ret = dialog.exec()

        if ret == TambahBarangBaru.DialogCode.Accepted:
            pass

if __name__ == "__main__":
    app = QApplication([])
    window = Widgetutama()
    window.show()
    sys.exit(app.exec())