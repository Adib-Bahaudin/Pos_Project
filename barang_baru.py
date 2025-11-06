import sys

from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QApplication, QHBoxLayout, QLabel, QLineEdit, \
    QGridLayout, QComboBox, QStackedWidget

from dialog_title_bar import DialogTitleBar

class TambahBarangBaru(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(1000, 700)
        self.setModal(True)

        root_layout = QVBoxLayout()
        root_widget= QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        title_bar = DialogTitleBar("Tambah Produk Baru", self)
        main_layout.addWidget(title_bar)

        conten_grid = QGridLayout()
        conten_grid.setContentsMargins(30,20,30,20)
        conten_grid.setSpacing(0)
        conten_grid.setColumnMinimumWidth(0,500)
        conten_grid.setColumnMinimumWidth(1, 500)

        header_widget = QWidget()
        header_widget.setStyleSheet("border: none;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0,0,0,20)

        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setObjectName("iconLabel")
        pixmap = QPixmap("data/Keranjang.png")
        icon_label.setPixmap(pixmap)
        icon_label.setScaledContents(True)
        header_layout.addWidget(icon_label)

        header_layout.addSpacing(10)

        label_formulir = QLabel()
        label_formulir.setText("Formulir Tambah Produk")
        label_formulir.setStyleSheet("""
            color: #FFFFFF;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(label_formulir)

        header_widget.setLayout(header_layout)
        conten_grid.addWidget(header_widget, 0,0,1,0,
                              Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.nama = WidgetKecil("data/box.png",
                                "Nama Produk Baru",
                                "Nama Produk ..."
                                )
        conten_grid.addWidget(self.nama, 1, 0)

        selector_widget = QWidget()
        selector_widget.setFixedWidth(435)
        selector_widget.setStyleSheet("border: none;")
        selector_layout = QVBoxLayout()
        selector_layout.setContentsMargins(25,0,0,0)

        label_layout = QHBoxLayout()

        icon = QLabel()
        icon.setPixmap(QPixmap("data/ikon jenis.png"))
        icon.setFixedSize(25, 25)
        icon.setScaledContents(True)
        label_layout.addWidget(icon)

        label_selector = QLabel()
        label_selector.setText("Jenis Produk : ")
        label_selector.setStyleSheet("""
            color: #90EE90;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        label_layout.addWidget(label_selector)

        selector_layout.addLayout(label_layout)

        combo_selector = QComboBox()
        combo_selector.addItems(['Satuan', 'Paket'])
        combo_selector.setFixedHeight(45)
        combo_selector.setCursor(Qt.CursorShape.PointingHandCursor)
        combo_selector.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }
            QComboBox:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox::down-arrow {
                image: url(data/panah atas bawah.png);
                width: 25px;
                height: 25px;
            }

            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 2px solid #90EE90;
                selection-background-color: #90EE90;
                selection-color: #000000;
                color: #FFFFFF;
                padding: 5px;
            }
        """)

        selector_layout.addWidget(combo_selector)

        selector_widget.setLayout(selector_layout)

        conten_grid.addWidget(selector_widget, 1,1)

        self.harga_jual = WidgetKecil("data/buy.png",
                                      "Harga Jual",
                                      "4000")
        conten_grid.addWidget(self.harga_jual, 2,0)

        self.harga_beli = WidgetKecil("data/uang.png",
                                      "harga_beli",
                                      "2000")
        conten_grid.addWidget(self.harga_beli, 2,1)

        self.stok = WidgetKecil("data/stok.png",
                                "Stok",
                                "100")

        self.convert = WidgetKecil("data/convert.png",
                                   "Paket Persatuan",
                                   "12")

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("border: none;")

        self.stack.addWidget(self.stok)
        self.stack.addWidget(self.convert)

        conten_grid.addWidget(self.stack)

        main_layout.addLayout(conten_grid)

        main_layout.addStretch()

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #90EE90;
        """)

class WidgetKecil(QWidget):
    def __init__(self, ikon_path, label_text, placeholder_text):
        super().__init__()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(25,10,25,0)
        content_layout.setSpacing(10)

        judul_layout = QHBoxLayout()
        judul_layout.setSpacing(10)
        judul_layout.setContentsMargins(0,0,0,0)

        icon = QLabel()
        icon.setPixmap(QPixmap(ikon_path))
        icon.setStyleSheet("border: none;")
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
            border: none;
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