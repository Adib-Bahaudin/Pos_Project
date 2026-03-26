from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QGridLayout
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

        self.summary_widget = QWidget()
        summary_layout = QGridLayout(self.summary_widget)
        summary_layout.setContentsMargins(0, 5, 0, 5)
        
        summary_layout.setColumnStretch(0, 1)
        summary_layout.setColumnStretch(1, 1)
        summary_layout.setColumnStretch(2, 1)
        summary_layout.setColumnStretch(3, 1)
        
        self.lbl_diskon_text = QLabel("Diskon : Rp.")
        self.lbl_diskon_value = QLabel("0")
        self.lbl_biaya_text = QLabel("Biaya Lain-Lain : Rp.")
        self.lbl_biaya_value = QLabel("0")
        self.lbl_total_text = QLabel("Total : Rp.")
        self.lbl_total_value = QLabel("0")
        
        self.lbl_diskon_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_diskon_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_biaya_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_biaya_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_total_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_total_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_diskon_text.setFont(QFont("Arial", 11))
        self.lbl_diskon_value.setFont(QFont("Arial", 11))
        self.lbl_biaya_text.setFont(QFont("Arial", 11))
        self.lbl_biaya_value.setFont(QFont("Arial", 11))
        self.lbl_total_text.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.lbl_total_value.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        summary_layout.addWidget(self.lbl_diskon_text, 0, 2)
        summary_layout.addWidget(self.lbl_diskon_value, 0, 3)
        summary_layout.addWidget(self.lbl_biaya_text, 1, 2)
        summary_layout.addWidget(self.lbl_biaya_value, 1, 3)
        summary_layout.addWidget(self.lbl_total_text, 2, 2)
        summary_layout.addWidget(self.lbl_total_value, 2, 3)
        
        layout.addWidget(self.summary_widget)

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
            self.table_items.setItem(i, 1, QTableWidgetItem(f"Rp. {harga:,}"))
            self.table_items.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.table_items.setItem(i, 3, QTableWidgetItem(f"Rp. {subtotal:,}"))

        pembulatan = int(header.get('pembulatan') or 0)
        total = int(header.get('total') or 0)
        diskon_nominal = int(header.get('diskon_nominal') or 0)
        diskon_persen = float(header.get('diskon_persen') or 0)
        
        if diskon_persen > 0:
            self.lbl_diskon_value.setText(f"{diskon_nominal:,} ({diskon_persen:g}%)")
        else:
            self.lbl_diskon_value.setText(f"{diskon_nominal:,}")

        if diskon_nominal == 0:
            self.lbl_diskon_text.hide()
            self.lbl_diskon_value.hide()
        else:
            self.lbl_diskon_text.show()
            self.lbl_diskon_value.show()

        if pembulatan == 0:
            self.lbl_biaya_text.hide()
            self.lbl_biaya_value.hide()
        else:
            self.lbl_biaya_text.show()
            self.lbl_biaya_value.show()
            
        self.lbl_biaya_value.setText(f"{pembulatan:,}")
        self.lbl_total_value.setText(f"{total:,}")
