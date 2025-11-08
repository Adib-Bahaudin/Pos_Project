from PySide6.QtGui import Qt, QPixmap, QIntValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, \
    QGridLayout, QComboBox, QStackedWidget

from database import DatabaseManager
from dialog_title_bar import DialogTitleBar
from fungsi import ScreenSize


class TambahBarangBaru(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(1000, 650)
        self.setModal(True)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(1000, 650)
        self.move(x, y)

        int_validator = QIntValidator(0, 9999999)

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

        self.combo_selector = QComboBox()
        self.combo_selector.addItems(['Satuan', 'Paket'])
        self.combo_selector.setFixedHeight(45)
        self.combo_selector.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_selector.setStyleSheet("""
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

        selector_layout.addWidget(self.combo_selector)
        self.combo_selector.currentIndexChanged.connect(self._on_change)

        selector_widget.setLayout(selector_layout)

        conten_grid.addWidget(selector_widget, 1,1)

        self.harga_jual = WidgetKecil("data/buy.png",
                                      "Harga Jual",
                                      "4000",
                                      int_validator)
        conten_grid.addWidget(self.harga_jual, 2,0)

        self.stack0 = QStackedWidget()
        self.stack0.setStyleSheet("border: none;")

        self.harga_beli = WidgetKecil("data/uang.png",
                                      "harga_beli",
                                      "2000",
                                      int_validator)
        self.stack0.addWidget(self.harga_beli)

        self.nama_barang = WidgetKecil("data/satuan.png",
                                       "Nama Barang Satuan",
                                       "bolpoin")
        self.stack0.addWidget(self.nama_barang)

        conten_grid.addWidget(self.stack0, 2,1)

        self.stok = WidgetKecil("data/stok.png",
                                "Stok",
                                "100",
                                int_validator)

        self.convert = WidgetKecil("data/convert.png",
                                   "Paket Persatuan",
                                   "12",
                                   int_validator)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("border: none;")

        self.stack.addWidget(self.stok)
        self.stack.addWidget(self.convert)

        conten_grid.addWidget(self.stack, 3,0)

        self.sku = WidgetKecil("data/sku.png",
                               "SKU",
                               "ABC123")
        conten_grid.addWidget(self.sku, 3,1)

        main_layout.addLayout(conten_grid)

        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(60,0,60,0)

        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #FFFFFF;
                border: 2px solid #ff0000;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5500ff;
                border: 2px solid #ff0000;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        self.btn_batal.setFixedHeight(45)
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_batal)

        button_layout.addStretch()

        self.btn_tambahkan = QPushButton("Tambahkan")
        self.btn_tambahkan.setStyleSheet("""
            QPushButton {
                background-color: #ffff00;
                color: #000000;
                border: 2px solid #ffff00;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #aaffff;
                border: 2px solid #ffff00;
            }
            QPushButton:pressed {
                background-color: #6FEF6F;
            }
        """)
        self.btn_tambahkan.setFixedHeight(45)
        self.btn_tambahkan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tambahkan.clicked.connect(self.validasi_data)
        button_layout.addWidget(self.btn_tambahkan)

        main_layout.addLayout(button_layout)

        main_layout.addSpacing(30)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #90EE90;
        """)

    def _on_change(self, index: int):
        self.stack.setCurrentIndex(index)
        self.stack0.setCurrentIndex(index)

    def validasi_data(self):
        index = self.combo_selector.currentIndex()
        nama = self.nama.get_data()
        harga_jual = self.harga_jual.get_data()
        harga_beli = self.harga_beli.get_data()
        stok = self.stok.get_data()
        sku = self.sku.get_data()
        nama_barang = self.nama_barang.get_data()
        persatuan = self.convert.get_data()

        if index == 0:
            valid, pesan = self.validate_fields_not_empty(
                nama = nama,
                harga_jual = harga_jual,
                harga_beli = harga_beli,
                stok = stok,
                sku = sku,
            )
            if not valid:
                print(pesan)
            else:
                validasi = DatabaseManager()
                validasi2 = validasi.verify_is_valid("satuan", sku, nama)
                if validasi2['is_valid']:
                    self.accept()
                else:
                    if validasi2['nama_barang'] and validasi2['sku_barang']:
                        print("Nama Barang dan SKU sudah ada")
                    elif validasi2['nama_barang']:
                        print("Nama Barang sudah ada")
                    elif validasi2['sku_barang']:
                        print("SKU sudah ada")
        else:
            valid, pesan = self.validate_fields_not_empty(
                nama = nama,
                harga_jual = harga_jual,
                nama_barang = nama_barang,
                persatuan = persatuan,
                sku = sku,
            )
            if not valid:
                print(pesan)
            else:
                validasi = DatabaseManager()
                validasi2 = validasi.verify_is_valid("paket", sku, nama, nama_barang)
                if validasi2['is_valid']:
                    self.accept()
                else:
                    if validasi2['nama_barang']:
                        print("Nama Barang sudah ada")
                    elif validasi2['sku_barang']:
                        print("SKU sudah ada")
                    elif validasi2['nama_produk']:
                        print("Nama Barang Tidak Ditemukan")

    def get_data(self):
        index = self.combo_selector.currentIndex()
        if index == 0:
            return "satuan", {
                "nama_barang": self.nama.get_data(),
                "harga_jual": self.harga_jual.get_data(),
                "harga_beli": self.harga_beli.get_data(),
                "stok": self.stok.get_data(),
                "sku": self.sku.get_data(),
            }
        else:
            return "paket", {
                "nama_paket": self.nama.get_data(),
                "harga_jual": self.harga_jual.get_data(),
                "nama_barang": self.nama_barang.get_data(),
                "per_satuan": self.convert.get_data(),
                "sku": self.sku.get_data(),
            }

    @staticmethod
    def validate_fields_not_empty(**fields):
        """
        Memeriksa semua field tidak kosong.
        Parameter:
            fields: pasangan nama_field=nilai_field
        Return:
            (bool, message)
        """
        empty_fields = [name for name, value in fields.items() if not value or str(value).strip() == ""]

        if empty_fields:
            message = f"Field berikut tidak boleh kosong: {', '.join(empty_fields)}"
            return False, message
        return True, ""


class WidgetKecil(QWidget):
    def __init__(self, ikon_path, label_text, placeholder_text, validator=None):
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
        if validator is not None:
            self.data.setValidator(validator)
        content_layout.addWidget(self.data)

        self.setLayout(content_layout)
        self.setContentsMargins(0,0,0,0)

    def get_data(self):
        return self.data.text().strip()

