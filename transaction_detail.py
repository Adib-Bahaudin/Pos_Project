from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget
)

from dialog_title_bar import DialogTitleBar


class TransactionDetailModal(QDialog):
    def __init__(self, db_manager, transaction_id, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.transaction_id = transaction_id
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setObjectName("transactionDetailModal")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        
        self.title_bar = DialogTitleBar(f"Detail Transaksi #{transaction_id}", self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)
        
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(18, 18, 18, 18)
        self.content_layout.setSpacing(12)
        
        self.setStyleSheet("""
            QDialog#transactionDetailModal {
                background-color: #1e1e1e;
                border: 2px solid #00ff00;
            }
            QWidget#contentWidget {
                background-color: transparent;
            }
            QLabel {
                color: white;
            }
        """)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = self.content_layout
        
        self.lbl_info = QLabel("Loading...")
        self.lbl_info.setFont(QFont("Arial", 11))
        layout.addWidget(self.lbl_info)
        
        self.table_items = QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(["Barang", "Harga", "Qty", "Subtotal"])
        self.table_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_items.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: white; border: 1px solid #444; }
            QHeaderView::section { background-color: #1e1e1e; color: white; padding: 4px; }
        """)
        self.table_items.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_items)

        self.lbl_laba = QLabel("")
        self.lbl_laba.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.lbl_laba)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Tutup")
        btn_close.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _load_data(self):
        data = self.db.get_transaction_detail_with_items(self.transaction_id)
        if not data:
            self.lbl_info.setText("Data tidak ditemukan.")
            return

        header = data['header']
        items = data['items']
        laba = header.get('laba')

        info_text = f"<b>ID Transaksi:</b> {header.get('id', '')} <br/>"
        info_text += f"<b>Waktu:</b> {header.get('tanggal', '')} <br/>"
        info_text += f"<b>Kasir:</b> {header.get('nama_kasir', '')} <br/>"
        info_text += f"<b>Customer:</b> {header.get('nama_customer', '')} <br/>"
        info_text += f"<b>Metode Bayar:</b> {header.get('metode_bayar', '')} <br/>"
        info_text += f"<b>Total:</b> Rp {int(header.get('total', 0)):,} <br/>"
        
        if header.get('catatan'):
            info_text += f"<b>Catatan:</b> {header.get('catatan', '')}"

        self.lbl_info.setText(info_text)

        self.table_items.setRowCount(len(items))
        for i, item in enumerate(items):
            nama = item.get("nama_barang", "")
            harga = int(item.get("harga", 0))
            qty = int(item.get("jumlah", 0))
            subtotal = harga * qty
            
            self.table_items.setItem(i, 0, QTableWidgetItem(nama))
            self.table_items.setItem(i, 1, QTableWidgetItem(f"Rp {harga:,}"))
            self.table_items.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.table_items.setItem(i, 3, QTableWidgetItem(f"Rp {subtotal:,}"))

        if laba:
            laba_bersih = int(laba.get('laba_bersih', 0))
            self.lbl_laba.setText(f"Laba Bersih Transaksi: Rp {laba_bersih:,}")
        else:
            self.lbl_laba.setText("Laba: Tidak tersedia")
