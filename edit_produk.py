import sys

from PySide6.QtGui import Qt, QFont, QPixmap
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QMainWindow, QPushButton, QApplication, QFrame,
                               QHBoxLayout, QLabel, QComboBox, QLineEdit, QGridLayout)

from dialog_title_bar import DialogTitleBar

class EditProduk(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        root_layout = QVBoxLayout()
        root_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        title_bar = DialogTitleBar("Edit Produk", self)
        main_layout.addWidget(title_bar)

        main_layout.addSpacing(20)

        header_layout = QHBoxLayout()

        header_layout.addStretch()

        header_icon = QLabel()
        header_icon.setFixedSize(60,60)
        header_icon.setPixmap(QPixmap("data/edit produk.svg"))
        header_icon.setStyleSheet("""
            border : none;
        """)
        header_icon.setScaledContents(True)
        header_layout.addWidget(header_icon)

        header_label = QLabel()
        header_label.setText("Formulir Edit Produk")
        header_label.setStyleSheet("""
                    color: #FFFFFF;
                    font-size: 22px;
                    border: none;
                    font-weight: bold;
                    letter-spacing: 1px;
                """)
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        main_layout.addSpacing(20)

        search_layout = QHBoxLayout()

        frame_search = QFrame()
        frame_search.setFixedSize(900, 95)
        frame_search.setStyleSheet("""
            border : 2px solid #90EE90;
            border-radius : 10px;
        """)

        search_content_layout = QVBoxLayout()

        label_satu = self.create_label_and_icon(
            "data/cari_label.svg",
            "Cari Produk : "
        )
        search_content_layout.addWidget(label_satu)

        search_main_layout = QHBoxLayout()

        combo_box = QComboBox()
        combo_box.setFixedSize(150,45)
        combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
        combo_box.setStyleSheet("""
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
        combo_box.addItems(["Satuan", "Paket"])
        search_main_layout.addWidget(combo_box)

        self.search_line_edit = LineEdit("Cari Produk Dengan SKU...")
        search_main_layout.addWidget(self.search_line_edit)

        search_btn = self._create_button(
            "CARI",
            100,
            "#00aaff",
            "#ffffff"
        )
        search_main_layout.addWidget(search_btn)

        search_content_layout.addLayout(search_main_layout)
        frame_search.setLayout(search_content_layout)
        search_layout.addWidget(frame_search)

        main_layout.addLayout(search_layout)

        main_layout.addSpacing(20)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(20,10,10,0)

        info_label = QLabel("Hasil Data Produk :   ")
        info_label.setStyleSheet("""
            color: #ffffff;
            border: none;
        """)
        info_label.setFont(QFont("Segoe UI", 12))

        info_layout.addWidget(info_label)

        return_label = self.create_label_and_icon(
            "data/warning_.svg",
            "Error - Data tidak ditemukan"
        )
        return_label.hide()

        info_layout.addWidget(return_label)

        info_layout.addStretch()

        main_layout.addLayout(info_layout)


        data_layout = QHBoxLayout()

        frame_data = QFrame()
        frame_data.setFixedSize(999, 200)
        data_conten_layout = QGridLayout()

        self.data_nama = WidgetData(
            "data/produk tangan.svg",
            "Nama Produk : "
        )
        data_conten_layout.addWidget(self.data_nama, 0, 0)

        self.data_stok = WidgetData(
            "data/stok.svg",
            "Stok Saat Ini"
        )
        data_conten_layout.addWidget(self.data_stok, 0, 1)

        self.sku = WidgetData(
            "data/barcode.svg",
            "SKU"
        )
        data_conten_layout.addWidget(self.sku, 0, 2)

        self.data_beli = WidgetData(
            "data/harga beli.svg",
            "Harga Beli : "
        )
        data_conten_layout.addWidget(self.data_beli, 1, 0)

        self.harga_jual = WidgetData(
            "data/hargajual.svg",
            "Harga Jual"
        )
        data_conten_layout.addWidget(self.harga_jual, 1, 1)

        frame_data.setLayout(data_conten_layout)
        data_layout.addWidget(frame_data)
        main_layout.addLayout(data_layout)

        main_layout.addStretch()

        tombol_bawah_widget = QFrame()
        tombol_bawah_widget.setStyleSheet("""
            border-top: none;
        """)
        tombol_bawah_layout = QHBoxLayout()
        tombol_bawah_layout.setContentsMargins(15,15,15,15)

        tombol_bawah_layout.addStretch()

        tombol_ok = self._create_button(
            "SUBMIT",
            120,
            "#FFD700",
            "#E0115F"

        )
        tombol_bawah_layout.addWidget(tombol_ok)
        tombol_bawah_widget.setLayout(tombol_bawah_layout)

        main_layout.addWidget(tombol_bawah_widget)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setMinimumSize(1050, 700)
        self.setStyleSheet("""
            border : 2px solid #90EE90;
            background-color: #000000;
        """)

    @staticmethod
    def _create_button(text, width, color_1, color_2) -> QPushButton:

        button = QPushButton()
        button.setText(text)
        button.setFixedHeight(45)
        button.setFixedWidth(width)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_1};
                color: {color_2};
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: {color_2};
                color: {color_1};
            }}
        """)

        return button

    @staticmethod
    def create_label_and_icon(icon_path, text) -> QFrame:

        frame = QFrame()
        frame.setStyleSheet("""
            border: none;
            background-color: transparent;
        """)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setPixmap(QPixmap(icon_path))
        icon_label.setScaledContents(True)
        content_layout.addWidget(icon_label)

        label = QLabel()
        label.setFont(QFont("Segoe UI", 12))
        label.setText(text)
        label.setStyleSheet("""
            color: #ffffff;
        """)
        content_layout.addWidget(label)

        frame.setLayout(content_layout)
        return frame

class LineEdit(QLineEdit):
    def __init__(self, placeholder_text=""):
        super().__init__()

        self.setFixedHeight(45)
        self.setStyleSheet("""
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
        self.setPlaceholderText(placeholder_text)

    def data(self):
        return self.text().strip()

    def write_text(self, text):
        self.setText(text)

class WidgetData(QWidget):
    def __init__(self, icon_path, text_label):
        super().__init__()

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0,0,0,0)

        label = EditProduk.create_label_and_icon(icon_path, text_label)
        root_layout.addWidget(label)

        self.editline = LineEdit("")
        root_layout.addWidget(self.editline)

        self.setLayout(root_layout)

    def get_data(self):
        return self.editline.data()

    def set_data(self, data_input):
        self.editline.write_text(data_input)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        button = QPushButton("EDIT PRODUK")
        button.setFixedSize(200, 200)
        button.clicked.connect(self.show_dialog)
        main_layout.addWidget(button)

        self.setCentralWidget(button)

    def show_dialog(self):
        dialog = EditProduk(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())