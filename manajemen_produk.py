from datetime import datetime
from zoneinfo import ZoneInfo

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt, QIcon
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QComboBox, QStackedWidget
)

from barang_baru import TambahBarangBaru
from database import DatabaseManager


class ManajemenProduk(QWidget):
    """Widget utama untuk manajemen produk"""

    # Konstanta
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 35
    SEARCH_FIELD_WIDTH = 500
    SEARCH_BUTTON_WIDTH = 100
    CONTENT_WIDGET_WIDTH = 800
    SELECTOR_HEIGHT = 35
    TABLE_WIDTH = 800
    PAGE_INPUT_WIDTH = 30
    PAGE_INPUT_HEIGHT = 30
    NAV_BUTTON_SIZE = 35
    RESET_BUTTON_WIDTH = 100

    def __init__(self):
        super().__init__()

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Inisialisasi user interface"""
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_widget = QFrame()
        root_widget.setContentsMargins(0, 0, 0, 0)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Header
        header_label = self._create_header_label()
        content_layout.addWidget(header_label)
        content_layout.addSpacing(20)

        # Tombol aksi utama
        action_buttons_widget = self._create_action_buttons()
        content_layout.addWidget(action_buttons_widget)

        # Tombol aksi sekunder
        secondary_buttons_widget = self._create_secondary_buttons()
        content_layout.addWidget(secondary_buttons_widget)

        content_layout.addSpacing(20)

        # Widget pencarian
        search_widget = self._create_search_widget()
        content_layout.addWidget(search_widget)

        content_layout.addStretch()

        # Widget data produk
        data_widget = self._create_data_widget()
        content_layout.addWidget(data_widget)

        root_widget.setLayout(content_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setStyleSheet("border: none")

    @staticmethod
    def _create_header_label() -> QLabel:
        """Membuat label header"""
        label = QLabel()
        label.setText("MANAJEMEN PRODUK")
        label.setFont(QFont("Times New Roman", 30, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _create_action_buttons(self) -> QWidget:
        """Membuat widget dengan tombol aksi utama"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        button_tambah = self._create_action_button("Tambah Produk", "#00ff00")
        button_hapus = self._create_action_button("Hapus Produk", "#ff0000")
        button_return = self._create_action_button("Return Produk", "#00aaff")

        layout.addWidget(button_tambah)
        layout.addWidget(button_hapus)
        layout.addWidget(button_return)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_secondary_buttons(self) -> QWidget:
        """Membuat widget dengan tombol aksi sekunder"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        button_edit = self._create_action_button("Edit Produk", "#ff8000")
        self.button_baru = self._create_action_button("Produk Baru", "#00ff00")

        layout.addWidget(button_edit)
        layout.addWidget(self.button_baru)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_action_button(self, text: str, color: str) -> QPushButton:
        """Membuat tombol aksi dengan warna kustom"""
        button = QPushButton(text)
        button.setFixedSize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                font-family: "Segoe UI";
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover{{
                background-color: #ffffff;
                color: {color};
            }}
        """)
        return button

    def _create_search_widget(self) -> QWidget:
        """Membuat widget pencarian"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()

        # Input pencarian
        search_input = QLineEdit()
        search_input.setStyleSheet("""
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
        search_input.setPlaceholderText("Cari Produk...")
        search_input.setFixedSize(self.SEARCH_FIELD_WIDTH, self.BUTTON_HEIGHT)
        layout.addWidget(search_input)

        # Tombol cari
        search_button = QPushButton("   Cari")
        search_button.setFixedSize(self.SEARCH_BUTTON_WIDTH, self.BUTTON_HEIGHT)
        search_button.setIcon(QIcon("data/search.svg"))
        search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_button.setStyleSheet("""
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
        layout.addWidget(search_button)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_data_widget(self) -> QWidget:
        """Membuat widget data produk dengan selector dan tabel"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Selector produk
        selector_widget = self._create_product_selector()
        layout.addWidget(selector_widget)

        # Stack widget untuk tabel
        self.stack = QStackedWidget()
        self.stack.addWidget(ProdukSatuan())
        self.stack.addWidget(ProdukPaket())
        layout.addWidget(self.stack)

        # Tombol navigasi bawah
        navigation_widget = self._create_bottom_navigation()
        layout.addWidget(navigation_widget)

        widget.setLayout(layout)
        return widget

    def _create_product_selector(self) -> QWidget:
        """Membuat widget selector tipe produk"""
        root_widget = QWidget()
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        content_widget = QWidget()
        content_widget.setFixedSize(self.CONTENT_WIDGET_WIDTH, self.SELECTOR_HEIGHT)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Label
        label = QLabel("Data Produk : ")
        label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff;")
        content_layout.addWidget(label)

        # ComboBox selector
        self.product_selector = QComboBox()
        self.product_selector.addItems(["Satuan", "Paket"])
        self.product_selector.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.product_selector.setFixedSize(100, self.SELECTOR_HEIGHT)
        self.product_selector.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.product_selector.setStyleSheet("""
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
        content_layout.addWidget(self.product_selector)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        root_layout.addWidget(content_widget)

        root_widget.setLayout(root_layout)
        return root_widget

    def _create_bottom_navigation(self) -> QWidget:
        """Membuat widget navigasi halaman di bagian bawah"""
        root_widget = QWidget()
        root_widget.setContentsMargins(0, 0, 0, 0)
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addStretch()

        content_widget = QWidget()
        content_widget.setFixedSize(self.CONTENT_WIDGET_WIDTH, self.BUTTON_HEIGHT)
        content_widget.setContentsMargins(0, 0, 0, 0)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Tombol reset
        button_reset = QPushButton(" Reset")
        button_reset.setIcon(QIcon("data/reset.svg"))
        button_reset.setFixedSize(self.RESET_BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_reset.setIconSize(QSize(20, 20))
        button_reset.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        button_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        button_reset.setStyleSheet("""
            QPushButton{
                background-color: #ff8000;
                color: white;
                border: 2px solid #ff8000;
                border-radius: 10px;
            }
        """)
        content_layout.addWidget(button_reset)

        content_layout.addStretch()

        # Tombol navigasi kiri
        button_left = NavigationButton("data/arah kiri.svg", "data/kiri-hover.svg")
        content_layout.addWidget(button_left)

        # Input halaman
        page_input = QLineEdit()
        page_input.setText("1")
        page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_input.setFixedSize(self.PAGE_INPUT_WIDTH, self.PAGE_INPUT_HEIGHT)
        page_input.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        page_input.setStyleSheet("""
            QLineEdit{
                border: none;
                background-color: #ffffff;
                color: #000000;
                border-radius: 5px;
            }
        """)
        page_input.setMaxLength(2)
        content_layout.addWidget(page_input)

        # Tombol navigasi kanan
        button_right = NavigationButton("data/arah kanan.svg", "data/kanan-hover.svg")
        content_layout.addWidget(button_right)

        content_widget.setLayout(content_layout)
        root_layout.addWidget(content_widget)
        root_layout.addStretch()

        root_widget.setLayout(root_layout)
        return root_widget

    def _setup_connections(self):
        """Setup signal-slot connections"""
        self.product_selector.currentIndexChanged.connect(self._switch_product_view)
        self.button_baru.clicked.connect(self._show_tambah_barang_dialog)

    def _switch_product_view(self, index: int):
        """Switch tampilan tabel berdasarkan pilihan selector"""
        self.stack.setCurrentIndex(index)

    def _show_tambah_barang_dialog(self):
        """Menampilkan dialog tambah barang"""
        dialog = TambahBarangBaru(self)
        result = dialog.exec()

        if result == TambahBarangBaru.DialogCode.Accepted:
            jenis, data = dialog.get_data()

            if jenis == "satuan":
                barang_baru = DatabaseManager()
                barang_baru.insert_barang_baru(
                    sku= data["sku"],
                    nama= data["nama_barang"],
                    harga_jual= data["harga_jual"],
                    harga_beli= data["harga_beli"],
                    stok= data["stok"],
                    tanggal= datetime.now(ZoneInfo("Asia/Jakarta"))
                )
                print("Data Satuan Ditambahkan")

            else:
                print("Data Paket Ditambahkan")
                print(f"nama barang = {data['nama_barang']}")


class BaseProductTable(QWidget):
    """Base class untuk tabel produk dengan fungsi shared"""

    # Konstanta (akan di-override di subclass)
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = []
    HEADERS = []

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi user interface"""
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 5)
        root_layout.addStretch()

        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Buat tabel
        table = self._create_table()
        table_layout.addWidget(table)

        table_widget.setLayout(table_layout)
        root_layout.addWidget(table_widget)
        root_layout.addStretch()

        self.setLayout(root_layout)

    def _create_table(self) -> QTableWidget:
        """Membuat tabel produk"""
        table = QTableWidget()
        table.setRowCount(self.TABLE_ROW_COUNT)
        table.setColumnCount(len(self.COLUMN_WIDTHS))
        table.setFixedWidth(self.TABLE_WIDTH)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Set header
        table.setHorizontalHeaderLabels(self.HEADERS)

        # Set lebar kolom
        for index, width in enumerate(self.COLUMN_WIDTHS):
            table.setColumnWidth(index, width)

        # Konfigurasi header
        header = table.horizontalHeader()
        header.setSectionResizeMode(header.ResizeMode.Interactive)

        # Sembunyikan header vertikal
        table.verticalHeader().setVisible(False)

        # Styling
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

        return table


class ProdukSatuan(BaseProductTable):
    """Widget tabel untuk produk satuan"""

    # Konstanta
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [100, 300, 80, 150, 170]
    HEADERS = ["SKU", "NAMA BARANG", "STOCK", "HARGA JUAL", "TGL MASUK"]


class ProdukPaket(BaseProductTable):
    """Widget tabel untuk produk paket"""

    # Konstanta
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [100, 300, 200, 200]
    HEADERS = ["SKU", "NAMA BARANG", "HARGA JUAL", "KETERANGAN"]


class NavigationButton(QPushButton):
    """Tombol navigasi dengan efek hover"""

    BUTTON_SIZE = 35

    def __init__(self, icon_normal: str, icon_hover: str):
        super().__init__()

        self.icon_normal = QIcon(icon_normal)
        self.icon_hover = QIcon(icon_hover)

        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi tampilan tombol"""
        self.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.setStyleSheet("""
            QPushButton{
                background-color: transparent;
                border: none;
            }
        """)
        self.setIconSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(self.icon_normal)

    def enterEvent(self, event):
        """Handler ketika mouse masuk ke area tombol"""
        self.setIcon(self.icon_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handler ketika mouse keluar dari area tombol"""
        self.setIcon(self.icon_normal)
        super().leaveEvent(event)