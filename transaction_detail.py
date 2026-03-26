from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QGridLayout, QComboBox
)
from PySide6.QtPrintSupport import QPrinterInfo

from dialog_title_bar import DialogTitleBar
from fungsi import CurrencyDelegate
from nota_printer import NotaPrinter


class PrinterSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setObjectName("printerSelectionDialog")
        self.setMinimumWidth(360)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        
        self.title_bar = DialogTitleBar("Pilih Printer", self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        
        lbl_printer = QLabel("Pilih Printer:")
        lbl_printer.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(lbl_printer)
        
        self.combo_printer = QComboBox()
        self.combo_printer.setStyleSheet("""
            QComboBox {
                background-color: #111827;
                border: 2px solid #263241;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #111827;
                color: white;
                selection-background-color: #0d6efd;
            }
        """)
        
        default_printer = QPrinterInfo.defaultPrinterName()
        available_printers = QPrinterInfo.availablePrinterNames()
        
        if default_printer:
            self.combo_printer.addItem(default_printer)
            
        for p in available_printers:
            if p != default_printer:
                self.combo_printer.addItem(p)
                
        layout.addWidget(self.combo_printer)
        
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        
        self.cancel_button = QPushButton("Batal")
        self.cancel_button.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 4px;")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Lanjutkan")
        self.apply_button.setStyleSheet("background-color: #0d6efd; color: white; padding: 8px; border-radius: 4px;")
        self.apply_button.clicked.connect(self.accept)
        
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        layout.addLayout(button_row)
        
        self.setStyleSheet("""
            QDialog#printerSelectionDialog {
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
        
    def get_selected_printer(self):
        return self.combo_printer.currentText()


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
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.setAlternatingRowColors(True)
        self.table_items.setShowGrid(False)
        self.table_items.setColumnCount(5)
        self.table_items.setHorizontalHeaderLabels(["No", "Barang", "Harga", "Qty", "Subtotal"])
        
        header = self.table_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_items.setStyleSheet("""
            QTableWidget { 
                background-color: #2d2d2d; 
                alternate-background-color: #545454; 
                color: white; 
                border: 1px solid #444; 
                outline: none; 
            }
            QHeaderView::section:horizontal {
                background-color: #a6a6a6;
                color: black; 
                font-weight: bold;
                border: none; 
                padding: 6px; 
            }
        """)
        self.table_items.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_items.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table_items.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        currency_delegate = CurrencyDelegate(horizontal_padding=25, parent=self.table_items)
        self.table_items.setItemDelegateForColumn(2, currency_delegate)
        self.table_items.setItemDelegateForColumn(4, currency_delegate)

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
        
        btn_print = QPushButton("Cetak Nota")
        btn_print.setStyleSheet("background-color: #0d6efd; color: white; padding: 8px; border-radius: 4px;")
        btn_print.clicked.connect(self._print_nota)
        
        btn_close = QPushButton("Tutup")
        btn_close.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_print)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _load_data(self):
        self.transaction_data = self.db.get_transaction_detail_with_items(self.transaction_id)
        data = self.transaction_data
        if not data:
            self.lbl_info.setText("Data tidak ditemukan.")
            return

        header = data['header']
        items = data['items']
        laba = header.get('laba')

        info_text = "<table cellspacing='0' cellpadding='2'>"
        info_text += f"<tr><td><b>ID Transaksi</b></td><td><b>:</b></td><td>{header.get('id', '')}</td></tr>"
        info_text += f"<tr><td><b>Waktu</b></td><td><b>:</b></td><td>{header.get('tanggal', '')}</td></tr>"
        info_text += f"<tr><td><b>Kasir</b></td><td><b>:</b></td><td>{header.get('nama_kasir', '')}</td></tr>"
        info_text += f"<tr><td><b>Customer</b></td><td><b>:</b></td><td>{header.get('nama_customer', '')}</td></tr>"
        info_text += f"<tr><td><b>Metode Bayar</b></td><td><b>:</b></td><td>{header.get('metode_bayar', '')}</td></tr>"
        
        if header.get('catatan'):
            info_text += f"<tr><td><b>Catatan</b></td><td><b>:</b></td><td>{header.get('catatan', '')}</td></tr>"
            
        info_text += "</table>"

        self.lbl_info.setText(info_text)

        self.table_items.setRowCount(len(items))
        for i, item in enumerate(items):
            nama = item.get("nama_barang", "")
            harga = int(item.get("harga", 0))
            qty = int(item.get("jumlah", 0))
            subtotal = harga * qty
            
            item_no = QTableWidgetItem(str(i + 1))
            item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_qty = QTableWidgetItem(str(qty))
            item_qty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table_items.setItem(i, 0, item_no)
            self.table_items.setItem(i, 1, QTableWidgetItem(nama))
            self.table_items.setItem(i, 2, QTableWidgetItem(f"Rp. {harga:,}"))
            self.table_items.setItem(i, 3, item_qty)
            self.table_items.setItem(i, 4, QTableWidgetItem(f"Rp. {subtotal:,}"))

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

    def _print_nota(self):
        if hasattr(self, 'transaction_data') and self.transaction_data:
            dialog = PrinterSelectionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_printer = dialog.get_selected_printer()
                printer = NotaPrinter(printer_name=selected_printer)
                printer.print_receipt(self.transaction_data)
