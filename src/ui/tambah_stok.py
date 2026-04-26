"""
Tambah Stok Produk Dialog
=========================
Dialog untuk menambahkan stok produk yang sudah ada di database.
Menampilkan tabel produk dengan kolom QSpinBox untuk input jumlah
unit yang akan ditambahkan, serta ringkasan total di bagian bawah.

Catatan: File ini hanya menangani frontend/UI.
         Operasi backend (database) belum diimplementasikan.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QSpinBox,
    QSpacerItem, QSizePolicy, QAbstractItemView,
)

from src.ui.dialog_title_bar import DialogTitleBar
from src.utils.fungsi import ScreenSize


class TambahStokDialog(QDialog):
    """Dialog antarmuka untuk menambah stok produk yang sudah ada."""

    # ── Konstanta ──────────────────────────────────────────────
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 560
    ACCENT_COLOR = "#00cc66"
    ACCENT_HOVER = "#00ff7f"
    BG_COLOR = "#000000"
    SURFACE_COLOR = "#111111"
    BORDER_COLOR = "#2a2a2a"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#aaaaaa"
    DANGER_COLOR = "#ff4d4d"
    DANGER_HOVER = "#ff6666"
    NEUTRAL_COLOR = "#555555"
    NEUTRAL_HOVER = "#777777"

    COLUMN_HEADERS = [
        "NO.", "SKU", "Nama Produk",
        "Stok Saat Ini", "Tambah Unit", "Stok Akhir", "Aksi",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.jumlah_baris = 0

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        screen = ScreenSize()
        x, y = screen.get_centered_position(
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        )
        self.move(x, y)

        self._setup_ui()

        self._load_dummy_data()

    # ══════════════════════════════════════════════════════════
    #  SETUP UI UTAMA
    # ══════════════════════════════════════════════════════════

    def _setup_ui(self):
        """Menyusun seluruh komponen UI dialog."""
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)

        root_widget = QWidget()
        root_widget.setObjectName("TambahStokFrame")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        title_bar = DialogTitleBar("Tambah Stok Produk", self)
        main_layout.addWidget(title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(14)

        self._build_search_section(content_layout)
        self._build_table_section(content_layout)
        self._build_bottom_section(content_layout)

        main_layout.addLayout(content_layout)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)

        self.setStyleSheet(f"""
            QWidget#TambahStokFrame {{
                background-color: {self.BG_COLOR};
                border: 2px solid {self.ACCENT_COLOR};
            }}
        """)

    # ══════════════════════════════════════════════════════════
    #  SECTION 1 – PENCARIAN
    # ══════════════════════════════════════════════════════════

    def _build_search_section(self, parent_layout: QVBoxLayout):
        """Membuat baris pencarian: label + input + tombol Cari."""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        label_cari = QLabel("Cari Produk:")
        label_cari.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        label_cari.setStyleSheet(f"color: {self.TEXT_PRIMARY}; border: none;")
        search_layout.addWidget(label_cari)

        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk atau SKU...")
        self.input_cari.setFixedHeight(36)
        self.input_cari.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.SURFACE_COLOR};
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 8px;
                padding: 6px 12px;
                color: {self.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:hover {{
                border: 2px solid {self.ACCENT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_HOVER};
            }}
        """)
        search_layout.addWidget(self.input_cari)

        self.btn_cari = QPushButton("  Cari")
        self.btn_cari.setFixedSize(90, 36)
        self.btn_cari.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cari.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_cari.setIcon(
            self.style().standardIcon(
                self.style().StandardPixmap.SP_FileDialogContentsView
            )
        )
        self.btn_cari.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.ACCENT_COLOR};
                color: #000000;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.ACCENT_HOVER};
            }}
        """)
        self.btn_cari.clicked.connect(self._on_search)
        search_layout.addWidget(self.btn_cari)

        parent_layout.addLayout(search_layout)

    # ══════════════════════════════════════════════════════════
    #  SECTION 2 – TABEL PRODUK
    # ══════════════════════════════════════════════════════════

    def _build_table_section(self, parent_layout: QVBoxLayout):
        """Membuat QTableWidget dengan 8 kolom sesuai spesifikasi."""
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMN_HEADERS))
        self.table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.table.setRowCount(0)

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(3, 95)   
        self.table.setColumnWidth(4, 100)   
        self.table.setColumnWidth(5, 95)   
        self.table.setColumnWidth(6, 70)   

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.SURFACE_COLOR};
                border: 2px solid {self.TEXT_PRIMARY};
                border-radius: 0px;
                color: {self.TEXT_PRIMARY};
                gridline-color: {self.BORDER_COLOR};
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px 8px;
                border-bottom: 1px solid {self.BORDER_COLOR};
            }}
            QTableWidget::item:selected {{
                background-color: #1a3d2a;
                color: {self.TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: #1a1a1a;
                color: {self.ACCENT_COLOR};
                font-weight: bold;
                font-size: 11px;
                padding: 6px 4px;
                border: none;
                border-bottom: 2px solid {self.ACCENT_COLOR};
            }}
        """)

        parent_layout.addWidget(self.table)

    # ══════════════════════════════════════════════════════════
    #  SECTION 3 – BOTTOM (RINGKASAN & TOMBOL)
    # ══════════════════════════════════════════════════════════

    def _build_bottom_section(self, parent_layout: QVBoxLayout):
        """Membuat baris bawah: ringkasan teks + 3 tombol aksi."""
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        self.label_ringkasan = QLabel(
            "Total Item Baru: 0 Produk.  Total Unit Ditambah: 0"
        )
        self.label_ringkasan.setFont(QFont("Segoe UI", 10))
        self.label_ringkasan.setStyleSheet(
            f"color: {self.TEXT_SECONDARY}; border: none;"
        )
        bottom_layout.addWidget(self.label_ringkasan)

        bottom_layout.addSpacerItem(
            QSpacerItem(
                40, 20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum,
            )
        )

        self.btn_hapus_semua = self._create_bottom_button(
            "Hapus Semua",
            self.NEUTRAL_COLOR,
            self.NEUTRAL_HOVER,
            text_color=self.TEXT_PRIMARY,
        )
        self.btn_hapus_semua.clicked.connect(self._on_hapus_semua)
        bottom_layout.addWidget(self.btn_hapus_semua)

        self.btn_batal = self._create_bottom_button(
            "Batal",
            "#333333",
            "#444444",
            text_color=self.TEXT_PRIMARY,
        )
        self.btn_batal.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_batal)

        self.btn_simpan = self._create_bottom_button(
            "Simpan Stok",
            self.ACCENT_COLOR,
            self.ACCENT_HOVER,
            text_color="#000000",
        )
        self.btn_simpan.clicked.connect(self._on_simpan)
        bottom_layout.addWidget(self.btn_simpan)

        parent_layout.addLayout(bottom_layout)

    # ══════════════════════════════════════════════════════════
    #  HELPER – MEMBUAT TOMBOL
    # ══════════════════════════════════════════════════════════

    @staticmethod
    def _create_bottom_button(
        text: str,
        bg_color: str,
        hover_color: str,
        text_color: str = "#ffffff",
    ) -> QPushButton:
        """Membuat QPushButton dengan styling konsisten untuk footer."""
        btn = QPushButton(text)
        btn.setFixedSize(120, 36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        return btn

    # ══════════════════════════════════════════════════════════
    #  DATA DUMMY (REPRESENTASI BACKEND)
    # ══════════════════════════════════════════════════════════

    def _get_dummy_products(self) -> list[dict]:
        """
        Mengembalikan data dummy produk.
        Nantinya fungsi ini akan diganti dengan query ke database.
        """
        return [
            {
                "id": 1,
                "sku": "SKU-001",
                "nama": "Pulpen Pilot G2",
                "deskripsi": "Pulpen gel 0.5mm warna hitam",
                "stok": 24,
            },
            {
                "id": 2,
                "sku": "SKU-002",
                "nama": "Buku Tulis A5",
                "deskripsi": "Buku tulis 80 halaman bergaris",
                "stok": 50,
            },
        ]

    def _load_dummy_data(self):
        """Memuat data dummy ke dalam tabel."""
        products = self._get_dummy_products()
        for product in products:
            self._add_product_row(product)
        self._update_ringkasan()

    # ══════════════════════════════════════════════════════════
    #  INJEKSI WIDGET KE DALAM TABEL
    # ══════════════════════════════════════════════════════════

    def _add_product_row(self, product: dict):
        """
        Menambahkan satu baris produk ke tabel.

        PENTING – Injeksi Widget:
        ─────────────────────────
        • Kolom 5 ("Tambah Unit"): menggunakan QSpinBox via setCellWidget().
          SpinBox dikonfigurasi min=0, max=9999, default=0.
          Setiap perubahan nilai akan memperbarui kolom "Stok Akhir"
          dan label ringkasan secara otomatis.

        • Kolom 7 ("Aksi"): menggunakan QPushButton "Hapus" via setCellWidget().
          Klik tombol ini akan menghapus baris terkait dari tabel.
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        stok_saat_ini = product.get("stok", 0)

        self.jumlah_baris += 1

        # ── Kolom 0: ID Produk ──
        item_id = QTableWidgetItem(str(self.jumlah_baris))
        item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_id.setForeground(QColor(self.TEXT_SECONDARY))
        self.table.setItem(row, 0, item_id)

        # ── Kolom 1: SKU ──
        item_sku = QTableWidgetItem(product["sku"])
        item_sku.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item_sku)

        # ── Kolom 2: Nama Produk ──
        item_nama = QTableWidgetItem(product["nama"])
        item_nama.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.table.setItem(row, 2, item_nama)

        # ── Kolom 4: Stok Saat Ini ──
        item_stok = QTableWidgetItem(str(stok_saat_ini))
        item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, item_stok)

        # ── Kolom 5: Tambah Unit (INJEKSI QSpinBox) ──────────────
        # QSpinBox diinjeksikan langsung ke dalam sel tabel
        # menggunakan setCellWidget(). Sinyal valueChanged dihubungkan
        # ke _on_spinbox_changed agar kolom "Stok Akhir" dan ringkasan
        # selalu ter-update secara real-time.
        spin_box = QSpinBox()
        spin_box.setMinimum(0)
        spin_box.setMaximum(9999)
        spin_box.setValue(0)
        spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin_box.setStyleSheet(f"""
            QSpinBox {{
                background-color: #1a1a1a;
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 4px;
                color: {self.TEXT_PRIMARY};
                font-size: 12px;
                padding: 2px;
            }}
            QSpinBox:focus {{
                border: 2px solid {self.ACCENT_COLOR};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: none;
                background-color: #222222;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {self.ACCENT_COLOR};
            }}
        """)
        # Simpan referensi stok awal pada spin_box agar bisa dihitung ulang
        spin_box.setProperty("stok_awal", stok_saat_ini)
        spin_box.setProperty("baris", row)
        spin_box.valueChanged.connect(
            lambda val, r=row: self._on_spinbox_changed(r, val)
        )
        self.table.setCellWidget(row, 4, spin_box)

        # ── Kolom 6: Stok Akhir ──
        item_stok_akhir = QTableWidgetItem(str(stok_saat_ini))
        item_stok_akhir.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_stok_akhir.setForeground(QColor(self.ACCENT_COLOR))
        self.table.setItem(row, 5, item_stok_akhir)

        # ── Kolom 7: Aksi (INJEKSI QPushButton "Hapus") ──────────
        # QPushButton bertuliskan "Hapus" diinjeksikan ke sel tabel
        # menggunakan setCellWidget(). Ikon tempat sampah diambil
        # dari QStyle standar (SP_TrashIcon / SP_DialogDiscardButton).
        # Klik tombol ini akan memanggil _on_hapus_baris() untuk
        # menghapus baris yang bersangkutan dari tabel.
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hapus.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_hapus.setIcon(
            self.style().standardIcon(
                self.style().StandardPixmap.SP_DialogDiscardButton
            )
        )
        btn_hapus.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.DANGER_COLOR};
                border: 1px solid {self.DANGER_COLOR};
                border-radius: 4px;
                padding: 3px 6px;
            }}
            QPushButton:hover {{
                background-color: {self.DANGER_COLOR};
                color: #ffffff;
            }}
        """)
        btn_hapus.clicked.connect(lambda _, r=row: self._on_hapus_baris(r))
        self.table.setCellWidget(row, 6, btn_hapus)

    # ══════════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ══════════════════════════════════════════════════════════

    def _on_spinbox_changed(self, row: int, value: int):
        """
        Dipanggil setiap kali QSpinBox pada baris tertentu berubah.
        Memperbarui kolom "Stok Akhir" = Stok Saat Ini + Tambah Unit,
        lalu memperbarui label ringkasan.
        """
        spin_box = self.table.cellWidget(row, 4)
        if spin_box is None:
            return

        stok_awal = spin_box.property("stok_awal") or 0
        stok_akhir = stok_awal + value

        item_akhir = self.table.item(row, 5)
        if item_akhir:
            item_akhir.setText(str(stok_akhir))

        self._update_ringkasan()

    def _on_hapus_baris(self, row: int):
        """Menghapus baris tertentu dari tabel, lalu memperbarui ringkasan."""
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)
            self.jumlah_baris -= 1

            # Perbarui lambda binding pada baris-baris setelahnya
            # agar indeks baris tetap konsisten setelah penghapusan.
            self._rebind_row_signals()
            self._update_ringkasan()

    def _rebind_row_signals(self):
        """
        Memperbarui koneksi sinyal QSpinBox dan QPushButton
        setelah sebuah baris dihapus, karena indeks baris bergeser.
        """
        for row in range(self.table.rowCount()):
            # Rebind QSpinBox
            spin_box = self.table.cellWidget(row, 4)
            if spin_box and isinstance(spin_box, QSpinBox):
                try:
                    spin_box.valueChanged.disconnect()
                except RuntimeError:
                    pass
                spin_box.setProperty("baris", row)
                spin_box.valueChanged.connect(
                    lambda val, r=row: self._on_spinbox_changed(r, val)
                )

            # Rebind QPushButton "Hapus"
            btn_hapus = self.table.cellWidget(row, 6)
            if btn_hapus and isinstance(btn_hapus, QPushButton):
                try:
                    btn_hapus.clicked.disconnect()
                except RuntimeError:
                    pass
                btn_hapus.clicked.connect(
                    lambda _, r=row: self._on_hapus_baris(r)
                )

    def _on_hapus_semua(self):
        """Menghapus seluruh baris dari tabel."""
        self.jumlah_baris = 0
        self.table.setRowCount(0)
        self._update_ringkasan()

    def _on_search(self):
        """
        Handler tombol Cari (dummy).
        Saat ini hanya memfilter data dummy berdasarkan teks input.
        Nantinya akan diganti dengan query ke database.
        """
        keyword = self.input_cari.text().strip().lower()
        all_products = self._get_dummy_products()

        if keyword:
            filtered = [
                p for p in all_products
                if keyword in p["nama"].lower()
                or keyword in p["sku"].lower()
            ]
        else:
            filtered = all_products

        # Bersihkan tabel dan isi ulang dengan hasil filter
        self.table.setRowCount(0)
        for product in filtered:
            self._add_product_row(product)
        self._update_ringkasan()

    def _on_simpan(self):
        """
        Handler tombol Simpan Stok (dummy).
        Saat ini hanya menutup dialog dengan status Accepted.
        Nantinya akan menyimpan data stok ke database.
        """
        self.accept()

    # ══════════════════════════════════════════════════════════
    #  UPDATE RINGKASAN
    # ══════════════════════════════════════════════════════════

    def _update_ringkasan(self):
        """
        Menghitung ulang ringkasan:
        - Total Item Baru = jumlah baris dengan Tambah Unit > 0
        - Total Unit Ditambah = sum semua nilai Tambah Unit
        """
        total_item = 0
        total_unit = 0

        for row in range(self.table.rowCount()):
            spin_box = self.table.cellWidget(row, 4)
            if spin_box and isinstance(spin_box, QSpinBox):
                val = spin_box.value()
                if val > 0:
                    total_item += 1
                total_unit += val

        self.label_ringkasan.setText(
            f"Total Item Baru: {total_item} Produk.  "
            f"Total Unit Ditambah: {total_unit}"
        )
