from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt, QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel,
                               QPushButton, QLineEdit, QTableWidget, QComboBox, QStackedWidget)


class ManajemenProduk(QWidget):
    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_widget = QFrame()
        root_widget.setContentsMargins(0, 0, 0, 0)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        kop_label = QLabel()
        kop_label.setText("MANAJEMEN PRODUK")
        kop_label.setFont(QFont("Times New Roman", 30, QFont.Weight.Bold))
        kop_label.setStyleSheet("color: #ffffff;")
        kop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(kop_label)
        content_layout.addSpacing(20)

        # Baris tombol pertama
        tombol_widget = QWidget()
        tombol_layout = QHBoxLayout()
        tombol_layout.setContentsMargins(0, 0, 0, 0)
        tombol_layout.setSpacing(10)
        tombol_layout.addStretch()

        tombol_tambah = self.buat_tombol("Tambah Produk", "#00ff00")
        tombol_hapus = self.buat_tombol("Hapus Produk", "#ff0000")
        tombol_return = self.buat_tombol("Return Produk", "#00aaff")

        tombol_layout.addWidget(tombol_tambah)
        tombol_layout.addWidget(tombol_hapus)
        tombol_layout.addWidget(tombol_return)
        tombol_layout.addStretch()

        tombol_widget.setLayout(tombol_layout)
        content_layout.addWidget(tombol_widget)

        tombol_widget2 = QWidget()
        tombol_layout2 = QHBoxLayout()
        tombol_layout2.setContentsMargins(0, 0, 0, 0)
        tombol_layout2.setSpacing(10)
        tombol_layout2.addStretch()

        tombol_edit = self.buat_tombol("Edit Produk", "#ff8000")
        tombol_baru = self.buat_tombol("Produk Baru", "#00ff00")

        tombol_layout2.addWidget(tombol_edit)
        tombol_layout2.addWidget(tombol_baru)
        tombol_layout2.addStretch()

        tombol_widget2.setLayout(tombol_layout2)
        content_layout.addWidget(tombol_widget2)

        content_layout.addSpacing(20)

        cari_widget = QWidget()
        cari_layout = QHBoxLayout()

        cari_layout.addStretch()

        cari = QLineEdit()
        cari.setStyleSheet("""
            QLineEdit{
                border: 2px solid #ffffff;
                border-radius: 10px;
                background-color: #676767;
                color: #ffffff;
                font-family: "Segoe UI";
                padding-left: 10px;
                font-size: 16px;
            }
            QLineEdit:placeholder {
                color: #d3d3d3;
            }
        """)
        cari.setPlaceholderText("Cari Produk...")
        cari.setFixedSize(500, 35)
        cari_layout.addWidget(cari)

        tombol_cari = QPushButton("   Cari")
        tombol_cari.setFixedSize(100, 35)
        tombol_cari.setIcon(QIcon("data/search.svg"))
        tombol_cari.setCursor(Qt.CursorShape.PointingHandCursor)
        tombol_cari.setStyleSheet("""
            QPushButton{
                background-color: #00aaff;
                color: white;
                border: 2px solid #00aaff;
                border-radius: 10px;
                font-family: "Segoe UI";
                font-size: 16px;
                font-weight: bold;
            }
        """)
        cari_layout.addWidget(tombol_cari)

        cari_layout.addStretch()

        cari_widget.setLayout(cari_layout)
        content_layout.addWidget(cari_widget)

        content_layout.addStretch()

        data_widget = QWidget()
        data_layout = QVBoxLayout()
        data_layout.setContentsMargins(0,0,0,0)
        data_layout.setSpacing(0)

        root_selector = QWidget()
        selector_layout = QHBoxLayout()
        selector_layout.setContentsMargins(0, 0, 0, 0)
        selector_layout.setSpacing(0)

        content_widget_selector = QWidget()
        content_widget_selector.setFixedSize(800, 35)
        content_layout_selector = QHBoxLayout()
        content_layout_selector.setContentsMargins(0, 0, 0, 0)
        content_layout_selector.setSpacing(0)

        label_selector = QLabel("Data Produk : ")
        label_selector.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        label_selector.setStyleSheet("color: #ffffff;")
        content_layout_selector.addWidget(label_selector)

        self.box_selector = QComboBox()
        self.box_selector.addItems(["Satuan", "Paket"])
        self.box_selector.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.box_selector.setFixedSize(100, 35)
        self.box_selector.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.box_selector.setStyleSheet("""
            QComboBox{
                background-color: transparent;
                border: none;
                color: #ffffff;
                padding-left: 5px;
            }
            QComboBox:hover{
                color: #00aaff;
            }
            QComboBox QAbstractItemView{
                color: #ffffff;
            }
        """)
        content_layout_selector.addWidget(self.box_selector)

        content_layout_selector.addStretch()

        content_widget_selector.setLayout(content_layout_selector)
        selector_layout.addWidget(content_widget_selector)

        root_selector.setLayout(selector_layout)
        data_layout.addWidget(root_selector)

        self.stack = QStackedWidget()

        data_layout.addWidget(self.stack)

        # Tambahkan kedua widget ke stack
        self.stack.addWidget(ProdukSatuan())
        self.stack.addWidget(ProdukPaket())

        # Hubungkan signal combobox dengan fungsi ganti_stack
        self.box_selector.currentIndexChanged.connect(self.ganti_stack)

        root_tombol_bawah_widget = QWidget()
        root_tombol_bawah_widget.setContentsMargins(0,0,0,0)
        root_tombol_bawah = QHBoxLayout()
        root_tombol_bawah.setContentsMargins(0,0,0,0)
        root_tombol_bawah.setSpacing(0)

        root_tombol_bawah.addStretch()

        content_tombol_widget = QWidget()
        content_tombol_widget.setFixedSize(800, 35)
        content_tombol_widget.setContentsMargins(0,0,0,0)
        content_tombol_layout = QHBoxLayout()
        content_tombol_layout.setContentsMargins(0,0,0,0)
        content_tombol_layout.setSpacing(0)

        tombol_reset = QPushButton(" Reset")
        tombol_reset.setIcon(QIcon("data/reset.svg"))
        tombol_reset.setFixedSize(100, 35)
        tombol_reset.setIconSize(QSize(20,20))
        tombol_reset.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tombol_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        tombol_reset.setStyleSheet("""
            QPushButton{
                background-color: #ff8000;
                color: white;
                border: 2px solid #ff8000;
                border-radius: 10px;
            }
        """)

        content_tombol_layout.addWidget(tombol_reset)

        content_tombol_layout.addStretch()

        tombol_kiri = ButtonNav("data/arah kiri.svg", "data/kiri-hover.svg")

        content_tombol_layout.addWidget(tombol_kiri)

        label_halaman = QLineEdit()
        label_halaman.setText("1")
        label_halaman.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_halaman.setFixedSize(30, 30)
        label_halaman.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label_halaman.setStyleSheet("""
            QLineEdit{
                border: none;
                background-color: #ffffff;
                color: #000000;
                border-radius: 5px;
            }
        """)
        label_halaman.setMaxLength(2)

        content_tombol_layout.addWidget(label_halaman)

        tombol_kanan = ButtonNav("data/arah kanan.svg", "data/kanan-hover.svg")

        content_tombol_layout.addWidget(tombol_kanan)

        content_tombol_widget.setLayout(content_tombol_layout)
        root_tombol_bawah.addWidget(content_tombol_widget)
        root_tombol_bawah.addStretch()

        root_tombol_bawah_widget.setLayout(root_tombol_bawah)
        data_layout.addWidget(root_tombol_bawah_widget)

        data_widget.setLayout(data_layout)

        content_layout.addWidget(data_widget)

        root_widget.setLayout(content_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setStyleSheet("""
            border: none
        """)

    def ganti_stack(self, index):
        """Fungsi untuk mengganti stack berdasarkan pilihan combobox"""
        self.stack.setCurrentIndex(index)

    @staticmethod
    def buat_tombol(teks, warna):
        tombol = QPushButton(teks)
        tombol.setFixedSize(200, 35)
        tombol.setCursor(Qt.CursorShape.PointingHandCursor)
        tombol.setStyleSheet(f"""
            QPushButton {{
                background-color: {warna};
                color: white;
                border: none;
                border-radius: 10px;
                font-family: "Segoe UI";
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover{{
                background-color: #ffffff;
                color: {warna};
            }}
        """)
        return tombol


class ProdukSatuan(QWidget):
    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 5)

        root_layout.addStretch()

        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)

        table = QTableWidget()
        table.setRowCount(5)
        table.setColumnCount(5)
        table.setFixedWidth(800)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = ["P_ID", "NAMA BARANG", "STOCK", "HARGA JUAL", "TGL MASUK"]
        table.setHorizontalHeaderLabels(header)

        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 150)
        table.setColumnWidth(4, 210)

        header_set = table.horizontalHeader()
        header_set.setSectionResizeMode(header_set.ResizeMode.Interactive)

        table.verticalHeader().setVisible(False)

        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget{
                background-color: #ffffff;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)

        table_layout.addWidget(table)

        table_widget.setLayout(table_layout)

        root_layout.addWidget(table_widget)

        root_layout.addStretch()

        self.setLayout(root_layout)


class ProdukPaket(QWidget):
    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 5)

        root_layout.addStretch()

        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)

        table = QTableWidget()
        table.setRowCount(5)
        table.setColumnCount(4)
        table.setFixedWidth(800)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = ["P_ID", "NAMA BARANG", "HARGA JUAL", "KETERANGAN"]
        table.setHorizontalHeaderLabels(header)

        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 200)
        table.setColumnWidth(3, 240)

        header_set = table.horizontalHeader()
        header_set.setSectionResizeMode(header_set.ResizeMode.Interactive)

        table.verticalHeader().setVisible(False)

        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget{
                background-color: #ffffff;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)

        table_layout.addWidget(table)

        table_widget.setLayout(table_layout)

        root_layout.addWidget(table_widget)

        root_layout.addStretch()

        self.setLayout(root_layout)


class ButtonNav(QPushButton):
    def __init__(self, normal, hover):
        super().__init__()

        self.setFixedSize(35,35)
        self.setStyleSheet("""
            QPushButton{
                background-color: transparent;
                border: none;
            }
        """)
        self.setIconSize(QSize(35, 35))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.normal = QIcon(normal)
        self.hover = QIcon(hover)
        self.setIcon(self.normal)

    def enterEvent(self, event):
        self.setIcon(self.hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.normal)
        super().leaveEvent(event)