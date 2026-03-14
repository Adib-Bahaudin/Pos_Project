from PySide6.QtGui import Qt, QFont, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QFrame,
    QApplication, QWidget,
)

from dialog_title_bar import DialogTitleBar
from fungsi import ScreenSize
from database import DatabaseManager


class HapusProdukDialog(QDialog):
    """Dialog hapus produk dengan verifikasi SKU dan konfirmasi eksplisit."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(760, 520)
        self.move(x, y)

        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self._on_handle_shortcut)

        self.db = DatabaseManager()
        self.current_data = None

        root_layout = QVBoxLayout()
        root_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        title_bar = DialogTitleBar("Hapus Produk", self)
        main_layout.addWidget(title_bar)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 8, 20, 0)
        form_layout.setSpacing(12)

        info = QLabel("Pilih jenis produk, cari SKU, lalu ketik HAPUS untuk verifikasi.")
        info.setStyleSheet("color: #ffffff; border: none; font-size: 14px;")
        form_layout.addWidget(info)

        row_search = QHBoxLayout()

        self.combo_jenis = QComboBox()
        self.combo_jenis.addItems(["Satuan", "Paket"])
        self.combo_jenis.setFixedSize(130, 40)
        self.combo_jenis.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_jenis.setStyleSheet(self._input_style())
        row_search.addWidget(self.combo_jenis)

        self.input_sku = QLineEdit()
        self.input_sku.setPlaceholderText("Masukkan SKU produk...")
        self.input_sku.setFixedHeight(40)
        self.input_sku.setStyleSheet(self._input_style())
        row_search.addWidget(self.input_sku)

        self.button_cari = self._create_button("Cari", "#00aaff", 90)
        self.button_cari.clicked.connect(self._on_search)
        row_search.addWidget(self.button_cari)

        form_layout.addLayout(row_search)

        detail_frame = QFrame()
        detail_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #444444;
                border-radius: 10px;
                background-color: #111111;
            }
        """)
        detail_layout = QVBoxLayout()
        detail_layout.setContentsMargins(12, 10, 12, 10)
        detail_layout.setSpacing(6)

        self.label_detail = QLabel("Data produk belum dimuat.")
        self.label_detail.setWordWrap(True)
        self.label_detail.setStyleSheet("color: #ffffff; border: none; font-size: 13px;")
        detail_layout.addWidget(self.label_detail)

        detail_frame.setLayout(detail_layout)
        form_layout.addWidget(detail_frame)

        verify_row = QHBoxLayout()
        verify_label = QLabel("Verifikasi:")
        verify_label.setStyleSheet("color: #ffffff; border: none;")
        verify_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        verify_row.addWidget(verify_label)

        self.input_verifikasi = QLineEdit()
        self.input_verifikasi.setPlaceholderText("Ketik HAPUS")
        self.input_verifikasi.setFixedHeight(40)
        self.input_verifikasi.setStyleSheet(self._input_style())
        verify_row.addWidget(self.input_verifikasi)

        form_layout.addLayout(verify_row)

        self.label_status = QLabel("")
        self.label_status.setStyleSheet("color: #ff9999; border: none;")
        form_layout.addWidget(self.label_status)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        footer = QHBoxLayout()
        footer.setContentsMargins(20, 0, 20, 20)
        footer.addStretch()

        self.button_batal = self._create_button("Batal", "#6c757d", 100)
        self.button_batal.clicked.connect(self.reject)
        footer.addWidget(self.button_batal)

        self.button_hapus = self._create_button("Hapus", "#ff0000", 130)
        self.button_hapus.clicked.connect(self._on_delete)
        self.button_hapus.setEnabled(False)
        footer.addWidget(self.button_hapus)

        main_layout.addLayout(footer)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)

        self.setLayout(root_layout)
        self.setMinimumSize(760, 520)
        self.setStyleSheet("""
            border: 2px solid #ff4d4d;
            background-color: #000000;
        """)

    @staticmethod
    def _input_style() -> str:
        return """
            QComboBox, QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QComboBox:hover, QLineEdit:hover {
                border: 2px solid #ff4d4d;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #ff7373;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #ff4d4d;
            }
        """

    @staticmethod
    def _create_button(text: str, color: str, width: int) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(width, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #ffffff;
                color: {color};
            }}
            QPushButton:disabled {{
                background-color: #4b4b4b;
                color: #a0a0a0;
            }}
        """)
        return button

    def _on_handle_shortcut(self):
        focused = QApplication.focusWidget()
        if focused in (self.input_sku, self.combo_jenis):
            self._on_search()
        elif focused == self.input_verifikasi:
            self._on_delete()

    def _jenis_value(self) -> str:
        return "satuan" if self.combo_jenis.currentIndex() == 0 else "paket"

    def _set_status(self, text: str, error: bool = True):
        color = "#ff9999" if error else "#90EE90"
        self.label_status.setStyleSheet(f"color: {color}; border: none;")
        self.label_status.setText(text)

    def _on_search(self):
        sku = self.input_sku.text().strip()
        if not sku:
            self.current_data = None
            self.button_hapus.setEnabled(False)
            self.label_detail.setText("Data produk belum dimuat.")
            self._set_status("SKU wajib diisi.")
            return

        data = self.db.get_produk_for_delete(self._jenis_value(), sku)
        if not data:
            self.current_data = None
            self.button_hapus.setEnabled(False)
            self.label_detail.setText("Produk tidak ditemukan.")
            self._set_status("Produk dengan SKU tersebut tidak ditemukan.")
            return

        self.current_data = data
        self.button_hapus.setEnabled(True)
        self._set_status("Produk ditemukan. Lanjutkan verifikasi untuk hapus.", error=False)

        if self._jenis_value() == "satuan":
            detail = (
                f"SKU: {data['sku']}\n"
                f"Nama: {data['nama_barang']}\n"
                f"Stok: {data.get('stok', 0)}\n"
                f"Harga Jual: {data.get('harga_jual', 0)}\n"
                f"Harga Beli: {data.get('harga_beli', 0)}"
            )
        else:
            detail = (
                f"SKU: {data['sku']}\n"
                f"Nama Paket: {data['nama_barang']}\n"
                f"Harga Jual: {data.get('harga_jual', 0)}\n"
                f"Detail: {data.get('keterangan', '-')}"
            )

        self.label_detail.setText(detail)

    def _on_delete(self):
        if not self.current_data:
            self._set_status("Cari produk terlebih dahulu.")
            return

        verifikasi = self.input_verifikasi.text().strip().upper()
        if verifikasi != "HAPUS":
            self._set_status("Verifikasi gagal. Ketik tepat: HAPUS")
            return

        result = self.db.delete_produk_bersih(self._jenis_value(), self.current_data["sku"])
        if not result.get("deleted"):
            self._set_status("Gagal menghapus produk. Data mungkin sudah tidak ada.")
            return

        ringkas = (
            f"Produk berhasil dihapus. "
            f"Detail transaksi terhapus: {result['deleted_transaksi_detail']}, "
            f"Produk paket terhapus: {result['deleted_produk_paket']}."
        )
        self._set_status(ringkas, error=False)
        self.accept()
