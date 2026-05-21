"""
Tambah Stok Produk Dialog
=========================
Dialog untuk menambahkan stok produk yang sudah ada di database.
Menampilkan tabel produk dengan kolom QSpinBox untuk input jumlah
unit yang akan ditambahkan, serta ringkasan total di bagian bawah.
"""

from PySide6.QtCore import Qt, QStringListModel, QTimer
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QSpinBox,
    QSpacerItem, QSizePolicy, QAbstractItemView,
    QCompleter,
)

from src.database.database import DatabaseManager
from src.ui.dialog_title_bar import DialogTitleBar
from src.utils.fungsi import ScreenSize
from src.utils.message import CustomMessageBox
from src.utils.logger import get_logger, log_error
from config import asset_path


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
    SEARCH_LIMIT = 12

    COLUMN_HEADERS = [
        "NO.", "SKU", "Nama Produk",
        "Stok Saat Ini", "Harga Unit", "Tambah Unit", "Subtotal", "Aksi",
    ]

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.logger = get_logger("TambahStok")
        self.logger.info("Inisialisasi dialog TambahStok")
        self.jumlah_baris = 0
        self.search_lookup = {}
        self.dataproduk = None

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
        self.logger.debug(f"Posisi dialog: x={x}, y={y}, ukuran={self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

        self._setup_ui()
        self._setup_search_completer()
        self.db_manager = db_manager or DatabaseManager()
        self._pending_search_add_signature = None

        self.input_cari.setFocus()
        self.logger.info("Dialog TambahStok berhasil diinisialisasi")

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
        self.input_cari.textChanged.connect(self._handle_search_text_changed)
        search_layout.addWidget(self.input_cari)

        self.btn_cari = QPushButton("  Cari")
        self.btn_cari.setFixedSize(90, 36)
        self.btn_cari.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cari.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_cari.setIcon(QIcon(asset_path("search.svg")))
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

        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 85)
        self.table.setColumnWidth(6, 90)
        self.table.setColumnWidth(7, 80)

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
            "Total Item: 0 Produk, Total Harga: 0 Rupiah"
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
        self.btn_simpan.clicked.connect(self.accept)
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
        self.table.setRowHeight(row, 50)

        stok_saat_ini = product.get("stok", 0)
        harga_beli = product.get("harga_beli", 0) or 0

        self.logger.info(
            f"Menambahkan produk ke tabel baris {row}: "
            f"SKU={product.get('sku')}, Nama={product.get('nama_barang')}, "
            f"Stok={stok_saat_ini}, HargaBeli={harga_beli}"
        )

        self.jumlah_baris += 1

        item_id = QTableWidgetItem(str(self.jumlah_baris))
        item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_id.setForeground(QColor(self.TEXT_SECONDARY))
        self.table.setItem(row, 0, item_id)

        item_sku = QTableWidgetItem(product["sku"])
        item_sku.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item_sku)

        item_nama = QTableWidgetItem(product["nama_barang"])
        item_nama.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.table.setItem(row, 2, item_nama)

        item_stok = QTableWidgetItem(str(stok_saat_ini))
        item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, item_stok)

        item_harga_unit = QTableWidgetItem(f"{int(harga_beli):,}".replace(",", "."))
        item_harga_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, item_harga_unit)

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
        spin_box.setProperty("stok_awal", stok_saat_ini)
        spin_box.setProperty("harga_unit", int(harga_beli))
        spin_box.setProperty("baris", row)
        spin_box.valueChanged.connect(
            lambda val, r=row: self._on_spinbox_changed(r, val)
        )
        self.table.setCellWidget(row, 5, spin_box)

        item_subtotal = QTableWidgetItem("0")
        item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_subtotal.setForeground(QColor(self.ACCENT_COLOR))
        self.table.setItem(row, 6, item_subtotal)

        btn_hapus = QPushButton("  Hapus")
        btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hapus.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_hapus.setIcon(QIcon(asset_path("tong_sampah_putih.svg")))
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
        self.table.setCellWidget(row, 7, btn_hapus)

    # ══════════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ══════════════════════════════════════════════════════════

    def _on_spinbox_changed(self, row: int, value: int):
        """
        Dipanggil setiap kali QSpinBox pada baris tertentu berubah.
        Memperbarui kolom "Subtotal" = Tambah Unit × Harga Unit,
        lalu memperbarui label ringkasan.
        """
        spin_box = self.table.cellWidget(row, 5)
        if spin_box is None:
            self.logger.warning(f"SpinBox tidak ditemukan pada baris {row}")
            return

        harga_unit = spin_box.property("harga_unit") or 0
        subtotal = value * harga_unit

        sku_item = self.table.item(row, 1)
        sku_text = sku_item.text() if sku_item else "?"
        self.logger.debug(
            f"SpinBox berubah baris {row} (SKU={sku_text}): "
            f"qty={value}, harga_unit={harga_unit}, subtotal={subtotal}"
        )

        item_subtotal = self.table.item(row, 6)
        if item_subtotal:
            item_subtotal.setText(f"{subtotal:,}".replace(",", "."))

        self._update_ringkasan()

    def _on_hapus_baris(self, row: int):
        """Menghapus baris tertentu dari tabel, lalu memperbarui ringkasan."""
        if 0 <= row < self.table.rowCount():
            sku_item = self.table.item(row, 1)
            sku_text = sku_item.text() if sku_item else "?"
            self.logger.info(f"Menghapus baris {row} (SKU={sku_text}) dari tabel, sisa baris: {self.table.rowCount() - 1}")

            self.table.removeRow(row)
            self.jumlah_baris -= 1

            self._rebind_row_signals()
            self._update_ringkasan()
        else:
            self.logger.warning(f"Gagal hapus baris {row}: indeks di luar jangkauan (total baris: {self.table.rowCount()})")

    def _rebind_row_signals(self):
        """
        Memperbarui koneksi sinyal QSpinBox dan QPushButton
        setelah sebuah baris dihapus, karena indeks baris bergeser.
        """
        total = self.table.rowCount()
        self.logger.debug(f"Rebind sinyal untuk {total} baris setelah penghapusan")

        for row in range(total):
            spin_box = self.table.cellWidget(row, 5)
            if spin_box and isinstance(spin_box, QSpinBox):
                try:
                    spin_box.valueChanged.disconnect()
                except RuntimeError:
                    pass
                spin_box.setProperty("baris", row)
                spin_box.valueChanged.connect(
                    lambda val, r=row: self._on_spinbox_changed(r, val)
                )

            btn_hapus = self.table.cellWidget(row, 7)
            if btn_hapus and isinstance(btn_hapus, QPushButton):
                try:
                    btn_hapus.clicked.disconnect()
                except RuntimeError:
                    pass
                btn_hapus.clicked.connect(
                    lambda _, r=row: self._on_hapus_baris(r)
                )

            nomer = QTableWidgetItem(str(row + 1))
            nomer.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            nomer.setForeground(QColor(self.TEXT_SECONDARY))    
            self.table.setItem(row, 0, nomer)

    def _on_hapus_semua(self):
        """Menghapus seluruh baris dari tabel."""
        jumlah_dihapus = self.table.rowCount()
        self.logger.info(f"Menghapus semua baris dari tabel ({jumlah_dihapus} baris)")
        self.jumlah_baris = 0
        self.table.setRowCount(0)
        self._update_ringkasan()

    def _on_search(self):
        """
        Handler tombol Cari.
        """
        self.input_cari.clear()
        self.input_cari.setFocus()
        self._update_ringkasan()

    def accept(self):
        """
        Handler tombol Simpan akan menyimpan 
        data stok terbaru ke database.
        """
        self.logger.info(f"Tombol Simpan ditekan, memproses {self.table.rowCount()} baris")

        import re
        text = self.label_ringkasan.text()
        match = re.search(r"Total Item:\s*(\d+)", text)

        if match:
            nilai_item = int(match.group(1))
            if nilai_item <= 0:
                self.logger.warning("Simpan dibatalkan: tidak ada item dengan qty > 0")
                CustomMessageBox.warning(self, "Barang Kosong!", 
                    "Tambahkan Produk dan Item Sebelum Melakukan Aksi"
                )
                return
        
        kunci = ["nama", "sku", "jumlah"]
        self.tambah_barang = {k: [] for k in kunci}
        berhasil_count = 0
        gagal_count = 0

        for row in range(self.table.rowCount()):
            spin_box = self.table.cellWidget(row, 5)
            sku = self.table.item(row, 1)
            nama = self.table.item(row, 2)
            stok_saat_ini = self.table.item(row, 3)

            try:
                if sku is not None and stok_saat_ini is not None:
                    sku = sku.text()
                    stok_val = spin_box.value() if spin_box else 0
                    stok_awal = int(stok_saat_ini.text()) if stok_saat_ini else 0
                    stok = str(stok_awal + stok_val)
                    self.logger.debug(
                        f"Baris {row}: SKU={sku}, stok_awal={stok_awal}, "
                        f"tambah={stok_val}, stok_akhir={stok}"
                    )
            except Exception as e:
                log_error(e, f"Baris {row}: gagal membaca nilai SKU/stok", self.logger)

            if spin_box and isinstance(spin_box, QSpinBox):
                val = spin_box.value()
                if val > 0:
                    self.logger.info(f"Update stok ke DB: SKU={sku}, stok_baru={stok}")
                    self.db_manager.update_produk("", sku, stok, True)
                    try:
                        if nama is not None:
                            nama = nama.text()
                            data = [nama, sku, val]

                            for k, v in zip(kunci, data):
                                self.tambah_barang[k].append(v)

                            berhasil_count += 1
                    except Exception as e:
                        gagal_count += 1
                        log_error(e, f"Gagal mengambil data nama produk baris {row}", self.logger)
                else:
                    gagal_count += 1
                    self.logger.warning(f"Produk SKU={sku} dilewati: qty=0")
                    CustomMessageBox.warning(
                        self, 
                        "Gagal Update Stok!", 
                        f"Tidak menambahkan stok pada produk dengan SKU: {sku}. \n"
                        "Dikarenakan anda menambahkan 0 item untuk produk tersebut."
                    )

        self.logger.info(
            f"Proses simpan selesai: {berhasil_count} produk berhasil, "
            f"{gagal_count} produk dilewati/gagal"
        )
        self.dataproduk = self.label_ringkasan.text()
        super().accept()

    def get_value(self):
        return self.dataproduk, self.tambah_barang
    # ══════════════════════════════════════════════════════════
    #  UPDATE RINGKASAN
    # ══════════════════════════════════════════════════════════

    @staticmethod
    def _format_rupiah(value: int) -> str:
        """Format angka dengan pemisah ribuan menggunakan titik."""
        return f"{value:,}".replace(",", ".")

    def _update_ringkasan(self):
        """
        Menghitung ulang ringkasan:
        - Total Item = jumlah baris dengan Tambah Unit > 0
        - Total Harga = sum semua subtotal (Tambah Unit × Harga Unit)
        """
        total_item = 0
        total_harga = 0

        for row in range(self.table.rowCount()):
            spin_box = self.table.cellWidget(row, 5)
            if spin_box and isinstance(spin_box, QSpinBox):
                val = spin_box.value()
                if val > 0:
                    total_item += 1
                harga_unit = spin_box.property("harga_unit") or 0
                total_harga += val * harga_unit

        self.logger.debug(
            f"Ringkasan diperbarui: total_item={total_item}, "
            f"total_harga={total_harga}, total_baris={self.table.rowCount()}"
        )

        self.label_ringkasan.setText(
            f"Total Item: {total_item} Produk, "
            f"Total Harga: {self._format_rupiah(total_harga)} Rupiah"
        )

    # ══════════════════════════════════════════════════════════
    #  HANDEL AUTO SUGGESTION
    # ══════════════════════════════════════════════════════════

    def _handle_search_text_changed(self, text: str):
        if text in self.search_lookup:
            return

        if not text:
            self.logger.debug("Input pencarian dikosongkan, mereset suggestion")
            self.search_model.setStringList([])
            self.search_lookup.clear()

            if (p := self.search_completer.popup()):
                p.hide()
            return

        self._refresh_search_suggestions(text)

    def _setup_search_completer(self):
        self.search_model = QStringListModel(self)
        self.search_completer = QCompleter(self.search_model, self)
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.search_completer.activated.connect(self._handle_completer_activated)
        self.input_cari.setCompleter(self.search_completer)

    def _refresh_search_suggestions(self, keyword: str = ""):
        keyword = keyword.strip()
        self.logger.debug(f"Mencari produk dengan keyword: '{keyword}', limit={self.SEARCH_LIMIT}")

        self.search_suggestions = self.db_manager.search_products(
            keyword=keyword,
            limit=self.SEARCH_LIMIT,
            filter_index=1
        )

        self.logger.debug(f"Hasil pencarian: {len(self.search_suggestions)} produk ditemukan")

        self.search_lookup = {
            self._build_suggestion_text(item): item
            for item in self.search_suggestions
        }
        self.search_model.setStringList(list(self.search_lookup.keys()))

        if keyword and self.search_suggestions:
            self.search_completer.complete()

    def _handle_completer_activated(self, selected_text: str):
        product = self.search_lookup.get(selected_text)
        if not product:
            self.logger.warning(f"Produk tidak ditemukan di lookup untuk: '{selected_text}'")
            return

        self.logger.info(
            f"Produk dipilih dari suggestion: SKU={product.get('sku')}, "
            f"Nama={product.get('nama_barang')}"
        )
        self._add_product_to_cart_once_per_event_cycle(product)
        QTimer.singleShot(0, self.input_cari.clear)

    @staticmethod
    def _build_suggestion_text(item: dict) -> str:
        return f"• {item['sku']} • {item['nama_barang']}"

    def _add_product_to_cart_once_per_event_cycle(self, product: dict):
        signature = self._get_product_signature(product)
        if signature == self._pending_search_add_signature:
            self.logger.debug(
                f"Double-add dicegah untuk produk SKU={product.get('sku')} "
                f"(signature sudah pending)"
            )
            return

        nama_produk = product.get("nama_barang", "")
        if self._is_product_in_table(nama_produk):
            self.logger.info(
                f"Produk '{nama_produk}' (SKU={product.get('sku')}) "
                f"sudah ada di tabel, tidak ditambahkan ulang"
            )
            return

        self._pending_search_add_signature = signature
        QTimer.singleShot(0, self._clear_pending_search_add_signature)
        self._add_product_row(product)

    def _is_product_in_table(self, nama_produk: str) -> bool:
        """
        Mengecek apakah produk dengan nama tertentu sudah ada di tabel
        berdasarkan kolom 2 (Nama Produk).

        Args:
            nama_produk: Nama produk yang akan dicek.

        Returns:
            True jika produk sudah ada di tabel, False jika belum.
        """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            if item and item.text() == nama_produk:
                return True
        return False

    def _get_product_signature(self, product: dict):
        """
        Signature untuk mencegah double-add pada siklus event Qt yang sama
        (mis. activated completer + returnPressed dipanggil berurutan).
        """
        product_id = product.get("id")
        sku = product.get("sku")
        tipe = product.get("tipe")

        if product_id is None and sku is None and tipe is None:
            return ("__object__", str(id(product)))

        return (
            str(product_id or ""),
            str(sku or ""),
            str(tipe or "").casefold(),
        )

    def _clear_pending_search_add_signature(self):
        self._pending_search_add_signature = None