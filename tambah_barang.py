from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QLabel, QFrame)

from dialog_title_bar import DialogTitleBar


class DialogTambahBarang(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_bar = None
        self.harga_jual = None
        self.harga_beli = None
        self.btn_tambahkan = None
        self.btn_batal = None
        self.nama_barang = None
        self.stok = None

        # Hapus title bar bawaan
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.setFixedSize(500, 580)
        self.setModal(True)
        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 3, 0, 0)
        main_layout.setSpacing(0)

        # Custom Title Bar
        self.title_bar = DialogTitleBar("Tambah Barang", self)
        main_layout.addWidget(self.title_bar)

        # Content Layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setObjectName("iconLabel")
        # Uncomment baris di bawah jika sudah ada gambar
        pixmap = QPixmap("data/product_icon.png")
        icon_label.setPixmap(
            pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setScaledContents(True)
        icon_label.setStyleSheet("""
            QLabel#iconLabel {
                background-color: #000000;
                border-radius: 25px;
                border: 3px solid #000000;
            }
        """)

        # Title
        title_label = QLabel("Tambah Data Barang")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        content_layout.addLayout(header_layout)

        # Garis pemisah
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("separator")
        content_layout.addWidget(line)

        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # Nama Barang
        self.nama_barang = self.create_input_field(
            "Nama Barang",
            "Masukkan nama barang...",
            "data/box.png"
        )
        form_layout.addLayout(self.nama_barang['layout'])

        # Harga Jual
        self.harga_jual = self.create_input_field(
            "Harga Jual",
            "Contoh: 50000",
            "data/sell.png"
        )
        form_layout.addLayout(self.harga_jual['layout'])

        # Harga Beli
        self.harga_beli = self.create_input_field(
            "Harga Beli",
            "Contoh: 40000",
            "data/buy.png"
        )
        form_layout.addLayout(self.harga_beli['layout'])

        # Stok
        self.stok = self.create_input_field(
            "Stok",
            "Contoh: 100",
            "data/stok.png"
        )
        form_layout.addLayout(self.stok['layout'])

        content_layout.addLayout(form_layout)
        content_layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Tombol Batal
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setObjectName("btnBatal")
        self.btn_batal.setFixedHeight(45)
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)

        # Tombol Tambahkan
        self.btn_tambahkan = QPushButton("Tambahkan")
        self.btn_tambahkan.setObjectName("btnTambahkan")
        self.btn_tambahkan.setFixedHeight(45)
        self.btn_tambahkan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tambahkan.clicked.connect(self.accept)

        button_layout.addWidget(self.btn_batal)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_tambahkan)

        content_layout.addLayout(button_layout)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    @staticmethod
    def create_input_field(label_text, placeholder, icon_path=None):
        """Membuat field input dengan label dan ikon"""
        field_layout = QVBoxLayout()
        field_layout.setSpacing(8)

        # Container untuk label dan icon
        label_container = QHBoxLayout()
        label_container.setSpacing(8)

        # Icon kecil untuk field (opsional)
        if icon_path:
            field_icon = QLabel()
            field_icon.setFixedSize(20, 20)
            field_icon.setObjectName("fieldIcon")
            # Uncomment jika sudah ada gambar
            pixmap = QPixmap(icon_path)
            field_icon.setPixmap(
                pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            label_container.addWidget(field_icon)

        # Label
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        label_container.addWidget(label)
        label_container.addStretch()

        field_layout.addLayout(label_container)

        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setObjectName("inputField")
        input_field.setFixedHeight(45)

        field_layout.addWidget(input_field)

        return {
            'layout': field_layout,
            'input': input_field,
            'label': label
        }

    def apply_stylesheet(self):
        """Menerapkan stylesheet dengan tema gelap dan aksen hijau"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                border: 2px solid #90EE90;
                border-radius: 10px;
            }

            QLabel#titleLabel {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#fieldLabel {
                color: #90EE90;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            QFrame#separator {
                background-color: #90EE90;
                max-height: 2px;
                margin: 5px 0px;
            }

            QLineEdit#inputField {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #FFFFFF;
                font-size: 14px;
                selection-background-color: #90EE90;
                selection-color: #000000;
            }

            QLineEdit#inputField:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }

            QLineEdit#inputField:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }

            QPushButton#btnBatal {
                background-color: #2a2a2a;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }

            QPushButton#btnBatal:hover {
                background-color: #3a3a3a;
                border: 2px solid #777777;
            }

            QPushButton#btnBatal:pressed {
                background-color: #1a1a1a;
            }

            QPushButton#btnTambahkan {
                background-color: #90EE90;
                color: #000000;
                border: 2px solid #7FFF7F;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }

            QPushButton#btnTambahkan:hover {
                background-color: #7FFF7F;
                border: 2px solid #6FEF6F;
            }

            QPushButton#btnTambahkan:pressed {
                background-color: #6FEF6F;
            }
        """)

    def get_data(self):
        """Mengambil data dari form"""
        return {
            'nama_barang': self.nama_barang['input'].text(),
            'harga_jual': self.harga_jual['input'].text(),
            'harga_beli': self.harga_beli['input'].text(),
            'stok': self.stok['input'].text()
        }