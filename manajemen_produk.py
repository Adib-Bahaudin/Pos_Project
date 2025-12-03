import math
from datetime import datetime, date
from zoneinfo import ZoneInfo

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt, QIcon, QIntValidator, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QComboBox, QStackedWidget, QTableWidgetItem, QApplication
)

from barang_baru import TambahBarangBaru
from edit_produk import EditProduk
from database import DatabaseManager


class ManajemenProduk(QWidget):
    """Widget utama untuk manajemen produk"""

    # Konstanta
    pages = 0
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

        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.handle_shortcut)

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
        self.table_data()

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

        self.button_edit = self._create_action_button("Edit Produk", "#ff8000")
        self.button_baru = self._create_action_button("Produk Baru", "#00ff00")

        layout.addWidget(self.button_edit)
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
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("""
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
            QLineEdit[active ="true"] {
                border: 2px solid #00aaff;
            }
        """)
        self.search_input.setPlaceholderText("Cari Produk atau SKU ...")
        self.search_input.setFixedSize(self.SEARCH_FIELD_WIDTH, self.BUTTON_HEIGHT)
        self.search_input.setProperty("active", False)
        layout.addWidget(self.search_input)

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
            QPushButton:hover {
                background-color: #0055ff;
                color: #ffffff;
                border: 2px solid #0055ff;
            }
        """)
        search_button.clicked.connect(self.search_page)
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
        self.table_satuan = ProdukSatuanTable()
        self.stack.addWidget(self.table_satuan)
        self.table_paket = ProdukPaketTable()
        self.stack.addWidget(self.table_paket)
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
        button_reset.clicked.connect(self.reset_click)
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
        button_left.clicked.connect(self.prev_page)
        content_layout.addWidget(button_left)

        # Input halaman
        self.page_input = QLineEdit()
        self.page_input.setText("1")
        self.page_input.setValidator(QIntValidator(0, 99))
        self.page_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_input.setFixedSize(self.PAGE_INPUT_WIDTH, self.PAGE_INPUT_HEIGHT)
        self.page_input.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.page_input.setStyleSheet("""
            QLineEdit{
                border: none;
                background-color: #ffffff;
                color: #000000;
                border-radius: 5px;
            }
        """)
        self.page_input.setMaxLength(2)
        content_layout.addWidget(self.page_input)

        # Tombol navigasi kanan
        button_right = NavigationButton("data/arah kanan.svg", "data/kanan-hover.svg")
        button_right.clicked.connect(self.next_page)
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
        self.button_edit.clicked.connect(self._show_edit_dialog)

    def reset_click(self):
        self.search_input.setText("")
        self.search_page()
        self.table_satuan.reset_width()
        self.table_paket.reset_width()

    def _switch_product_view(self, index: int):
        """Switch tampilan tabel berdasarkan pilihan selector"""
        self.stack.setCurrentIndex(index)
        self.table_data()

    def _show_tambah_barang_dialog(self):
        """Menampilkan dialog tambah barang"""
        dialog = TambahBarangBaru(self)
        result = dialog.exec()

        if result == TambahBarangBaru.DialogCode.Accepted:
            jenis, data = dialog.get_data()

            if jenis == "satuan":
                barang_baru = DatabaseManager()
                barang_baru.insert_barang_baru_satuan(
                    sku= data["sku"],
                    nama= data["nama_barang"],
                    harga_jual= data["harga_jual"],
                    harga_beli= data["harga_beli"],
                    stok= data["stok"],
                    tanggal= datetime.now(ZoneInfo("Asia/Jakarta"))
                )
                self.table_data()
            else:
                barang_baru = DatabaseManager()
                barang_baru.insert_barang_baru_paket(
                    nama= data["nama_paket"],
                    harga_jual= data["harga_jual"],
                    nama_barang= data["nama_barang"],
                    sku= data["sku"],
                    coversion= data["per_satuan"],
                )
                self.table_data()

    def _show_edit_dialog(self):
        dialog = EditProduk(self)
        dialog.exec()

    def handle_shortcut(self):
        focused = QApplication.focusWidget()

        if focused == self.search_input:
            self.search_page()
        elif focused == self.page_input:
            self.custom_page()

    def table_data(self, offset=0):
        current = bool(self.search_input.property("active"))
        text = self.search_input.text().strip()
        database = DatabaseManager()
        produk = self.product_selector.currentIndex()
        if current == False or (text == "" and current == True):
            if current:
                self.search_input.setProperty("active", not current)
                self.search_input.style().unpolish(self.search_input)
                self.search_input.style().polish(self.search_input)

            if produk == 0:
                data = database.get_produk_satuan(5, offset)
                self.table_satuan.set_data(data)
            else:
                data = database.get_produk_paket(5, offset)
                self.table_paket.set_data(data)
        elif text != "" and current == True:
            if produk == 0:
                data = database.get_search_produk(produk, text, 5, offset)
                self.table_satuan.set_data(data)
            else:
                data = database.get_search_produk(produk, text, 5, offset)
                self.table_paket.set_data(data)

        if offset == 0:
            self.page_input.setText("1")
        else:
            text = int(offset / 5) + 1
            self.page_input.setText(str(text))

    def search_page(self):
        current = bool(self.search_input.property("active"))
        text = self.search_input.text().strip()
        if (text != "" and current == False) or (text != "" and current == True):
            if not current:
                self.search_input.setProperty("active", not current)
            self.search_input.style().unpolish(self.search_input)
            self.search_input.style().polish(self.search_input)
            self.table_data()
        elif text == "" and current == True:
            self.search_input.setProperty("active", not current)
            self.search_input.style().unpolish(self.search_input)
            self.search_input.style().polish(self.search_input)
            self.table_data()

    def custom_page(self):
        text = self.search_input.text().strip()
        current = bool(self.search_input.property("active"))
        index = self.product_selector.currentIndex()
        database = DatabaseManager()

        if current == False or (text == "" and current == True):
            self.pages = math.ceil(database.get_rows_produk(index)/5)
        else:
            self.pages = math.ceil(database.get_search_row(index,text)/5)

        page = int(self.page_input.text().strip())
        if page >= self.pages:
            self.page_input.setText(str(self.pages))
            self.table_data((self.pages - 1) * 5)
        elif page <= 0:
            self.table_data()
        else:
            self.table_data((page - 1) * 5)

    def next_page(self):
        page = int(self.page_input.text().strip())
        database = DatabaseManager()
        text = self.search_input.text().strip()
        current = bool(self.search_input.property("active"))
        index = self.product_selector.currentIndex()

        if current == False or (text == "" and current == True):
            self.pages = math.ceil(database.get_rows_produk(index) / 5)
        else:
            self.pages = math.ceil(database.get_search_row(index,text)/5)

        if page < self.pages:
            page = page + 1
            self.table_data((page - 1) * 5)
        else:
            pass

    def prev_page(self):
        page = int(self.page_input.text().strip())
        if page > 1:
            page -= 1
            self.table_data((page - 1) * 5)
        else:
            pass


_ID_MONTHS = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def format_tanggal(value, in_fmt="%Y-%m-%d"):
    """
    Terima string ISO (contoh: '2025-11-07 19:32:27.262473+07:00'),
    atau 'YYYY-MM-DD', atau datetime/date.
    Kembalikan '7 November 2025' (tanpa ubah zona waktu).
    """
    if not value:
        return ""
    try:
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                dt = datetime.strptime(value, in_fmt)
        elif isinstance(value, datetime):
            dt = value
        elif isinstance(value, date):
            dt = datetime(value.year, value.month, value.day)
        else:
            return str(value)

        d = dt.date()
        return f"{d.day} {_ID_MONTHS[d.month]} {d.year}"
    except (ValueError, TypeError):
        return str(value)


class BaseProductTable(QWidget):
    """Base class untuk tabel produk dengan fungsi shared"""

    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = []
    HEADERS = []
    TABLE_NAME = ""
    FIELDS = []
    FORMATTERS = {}

    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.per_page = self.TABLE_ROW_COUNT
        self._all_rows = []
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
        self.table = self._create_table()
        table_layout.addWidget(self.table)

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

    def reset_width(self):
        """reset lebar kolom sesuai konfigurasi awal"""
        for index, width in enumerate(self.COLUMN_WIDTHS):
            self.table.setColumnWidth(index, width)

    def set_data(self, rows: list[dict]):
        """Set Seluruh Data tabel"""
        self._all_rows = rows or []
        self.current_page = 1
        self._render_current_page()

    def _render_current_page(self):
        self.table.clearContents()

        for r, row in enumerate(self._all_rows):
            for c, key in enumerate(self.FIELDS):
                val = row.get(key)
                if key in self.FORMATTERS:
                    val = self.FORMATTERS[key](val)
                item = QTableWidgetItem("" if val is None else str(val))
                if key == "nama_barang":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r, c, item)


class ProdukSatuanTable(BaseProductTable):
    """Widget tabel untuk produk satuan"""

    TABLE_NAME = "produksatuan"
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [100, 300, 80, 150, 170]
    HEADERS = ["SKU", "NAMA BARANG", "STOCK", "HARGA JUAL", "TGL MASUK"]
    FIELDS = ["sku", "nama_barang", "stock", "harga_jual", "tgl_masuk"]
    FORMATTERS = {
        "tgl_masuk": format_tanggal,
    }


class ProdukPaketTable(BaseProductTable):
    """Widget tabel untuk produk paket"""

    TABLE_NAME = "produkpaket"
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [100, 300, 200, 200]
    HEADERS = ["SKU", "NAMA BARANG", "HARGA JUAL", "KETERANGAN"]
    FIELDS = ["sku", "nama_barang", "harga_jual", "keterangan"]


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
