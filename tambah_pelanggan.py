from PySide6.QtGui import Qt, QPixmap, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QLabel, QGridLayout
)

from barang_baru import WidgetKecil
from dialog_title_bar import DialogTitleBar
from fungsi import ScreenSize


class TambahPelangganDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(600, 550)
        self.setModal(True)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(600, 550)
        self.move(x, y)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(2, 2, 2, 2)

        root_widget = QWidget()
        root_widget.setObjectName("MainFrame")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)

        title_bar = DialogTitleBar("Tambah Pelanggan Baru", self)
        main_layout.addWidget(title_bar)

        header_widget = QWidget()
        header_widget.setStyleSheet("border: none;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 20, 0, 20)

        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setPixmap(QPixmap("data/pelanggan putih.png"))
        icon_label.setScaledContents(True)
        header_layout.addWidget(icon_label)
        header_layout.addSpacing(10)

        label_formulir = QLabel("Formulir Tambah Pelanggan")
        label_formulir.setStyleSheet("""
            color: #FFFFFF;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(label_formulir)
        header_layout.addStretch()
        header_widget.setLayout(header_layout)

        main_layout.addWidget(header_widget, 0, Qt.AlignmentFlag.AlignCenter)

        conten_grid = QGridLayout()
        conten_grid.setContentsMargins(30, 0, 30, 20)
        conten_grid.setSpacing(10)

        self.input_nama = WidgetKecil("data/nama_icon.svg", "Nama Pelanggan (*Wajib)", "Masukkan Nama Pelanggan...")
        conten_grid.addWidget(self.input_nama, 0, 0)

        self.input_nohp = WidgetKecil("data/satuan.png", "Nomor Handphone", "Contoh: 081234567890")
        conten_grid.addWidget(self.input_nohp, 1, 0)

        self.input_alamat = WidgetKecil("data/box.png", "Alamat Pelanggan", "Masukkan Alamat Lengkap...")
        conten_grid.addWidget(self.input_alamat, 2, 0)

        main_layout.addLayout(conten_grid)
        main_layout.addStretch()

        self.label_peringatan = QLabel()
        self.label_peringatan.setFont(QFont("Franklin Gothic", 11, QFont.Weight.Bold))
        self.label_peringatan.setStyleSheet("color: #fbff00; border: none;")
        self.label_peringatan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_peringatan)

        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(60, 0, 60, 20)
        button_layout.addStretch()

        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.setFixedHeight(45)
        self.btn_batal.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #FFFFFF;
                border: 2px solid #ff0000;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5500ff;
                border: 2px solid #ff0000;
            }
        """)
        self.btn_batal.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_batal)

        self.btn_tambahkan = QPushButton("Tambahkan")
        self.btn_tambahkan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tambahkan.setFixedHeight(45)
        self.btn_tambahkan.setStyleSheet("""
            QPushButton {
                background-color: #ffff00;
                color: #000000;
                border: 2px solid #ffff00;
                border-radius: 8px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #aaffff;
                border: 2px solid #ffff00;
            }
        """)
        self.btn_tambahkan.clicked.connect(self.validasi_data)
        button_layout.addWidget(self.btn_tambahkan)

        main_layout.addLayout(button_layout)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)

        self.setStyleSheet("""
            QWidget#MainFrame {
                background-color: #000000;
                border: 2px solid #90EE90;
                border-radius: 10px;
            }
        """)

    def validasi_data(self):
        nama = self.input_nama.get_data()

        if not nama or nama == "":
            self.label_peringatan.setText("Nama Pelanggan wajib diisi!")
            return

        self.accept()

    def get_data(self):
        return {
            "nama": self.input_nama.get_data(),
            "nomer_hp": self.input_nohp.get_data(),
            "alamat": self.input_alamat.get_data(),
        }