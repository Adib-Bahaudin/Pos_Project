from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QAbstractItemView, QHeaderView, QGridLayout,
    QTextEdit
)


class PenjualanWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        container = QFrame()
        container.setStyleSheet("background-color: #050505;")
        root_layout.addWidget(container)

        content_layout = QHBoxLayout(container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        content_layout.addWidget(left_panel, 7)
        content_layout.addWidget(right_panel, 3)

        self.setStyleSheet(self._get_stylesheet())

    def _create_left_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        header = self._create_header_card()
        search_card = self._create_search_card()
        cart_card = self._create_cart_card()

        layout.addWidget(header)
        layout.addWidget(search_card)
        layout.addWidget(cart_card)
        layout.addStretch()
        return widget

    def _create_right_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        payment_card = self._create_payment_summary_card()
        input_card = self._create_payment_input_card()
        quick_action_card = self._create_quick_actions_card()

        layout.addWidget(payment_card)
        layout.addWidget(input_card)
        layout.addWidget(quick_action_card)
        layout.addStretch()

        return widget

    def _create_header_card(self) -> QWidget:
        card = self._build_card()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(10)

        icon = QSvgWidget("data/kasir_100.svg")
        icon.setFixedSize(QSize(50, 50))

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(4)

        title = QLabel("TRANSAKSI PENJUALAN")
        title.setFont(QFont("Times New Roman", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        badge_layout = QHBoxLayout()
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(4)

        badge_nama = QLabel("NAMA KASIR : ADIB")
        badge_nama.setObjectName("smallBadge")

        badge_role = QLabel("SUPER USER")
        badge_role.setObjectName("smallBadge")

        badge_layout.addWidget(badge_nama)
        badge_layout.addWidget(badge_role)
        badge_layout.addStretch()

        header_layout.addWidget(title)
        header_layout.addLayout(badge_layout)

        layout.addWidget(icon)
        layout.addLayout(header_layout)
        return card

    def _create_search_card(self) -> QWidget:
        card = self._build_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(16)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik nama produk / SKU lalu tekan Enter...")
        self.search_input.returnPressed.connect(self._add_product_from_search)
        search_row.addWidget(self.search_input, 1)

        self.product_filter = QComboBox()
        self.product_filter.addItems(["Semua Produk", "Produk Satuan", "Produk Paket"])
        self.product_filter.setFixedWidth(170)
        search_row.addWidget(self.product_filter)

        self.button_add_product = QPushButton("Tambah ke Keranjang")
        self.button_add_product.clicked.connect(self._add_product_from_search)
        self.button_add_product.setObjectName("primaryButton")
        self.button_add_product.setStyleSheet("""
            QPushButton {
                background-color: #00c853;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #00c853;
            }
        """)
        search_row.addWidget(self.button_add_product)

        layout.addLayout(search_row)
        return card

    def _create_cart_card(self) -> QWidget:
        card = self._build_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        self.cart_table = QTableWidget(0, 7)
        self.cart_table.setHorizontalHeaderLabels([
            "SKU", "Produk", "Tipe", "Harga", "Qty", "Subtotal", "Aksi"
        ])
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.cart_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setMinimumHeight(100)
        layout.addWidget(self.cart_table, 1)

        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.cart_info_label = QLabel("Keranjang masih kosong.")
        self.cart_info_label.setStyleSheet("color: #98a3af; font-size: 12px;")
        footer.addWidget(self.cart_info_label)
        footer.addStretch()

        clear_button = QPushButton("Kosongkan Keranjang")
        clear_button.setObjectName("ghostButton")
        clear_button.setStyleSheet("""
            QPushButton { 
                background-color: #17202a;
                color: #dbe8f4;
                border: 2px solid #2a3745;
            }
            QPushButton:hover { 
                background-color: #dbe8f4;
                color: #17202a;
            }
        """)
        clear_button.clicked.connect(self._clear_cart)
        footer.addWidget(clear_button)

        layout.addLayout(footer)
        return card

    def _create_payment_summary_card(self) -> QWidget:
        card = self._build_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.summary_subtotal = self._create_summary_row(layout, "Subtotal", "Rp 0")
        self.summary_discount = self._create_summary_row(layout, "Diskon", "Rp 0")
        self.summary_rounding = self._create_summary_row(layout, "Pembulatan", "Rp 0")

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #2e3945;")
        layout.addWidget(divider)

        total_label = QLabel("Total Tagihan")
        total_label.setStyleSheet("color: #b8c4d0; font-size: 13px; font-weight: 600;")
        layout.addWidget(total_label)

        self.summary_total = QLabel("Rp 0")
        self.summary_total.setStyleSheet(
            "color: #00ff85; font-size: 28px; font-weight: 800;"
        )
        layout.addWidget(self.summary_total)

        return card

    def _create_payment_input_card(self) -> QWidget:
        card = self._build_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(5)

        metode_label = QLabel("Metode Bayar")
        metode_label.setObjectName("formLabel")
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Tunai", "QRIS", "Transfer"])
        self.payment_method.setFixedHeight(33)
        self.payment_method.setStyleSheet("""
            QComboBox {
                padding: 0px 12px;
            }
        """
        )
        form_layout.addWidget(metode_label, 0, 0)
        form_layout.addWidget(self.payment_method, 0, 1)

        bayar_label = QLabel("Nominal Bayar")
        bayar_label.setObjectName("formLabel")

        payment_layout = QHBoxLayout()
        payment_layout.setContentsMargins(0, 0, 0, 0)
        rp = QLabel("Rp. ")
        payment_layout.addWidget(rp)
        self.payment_input = QLineEdit()
        self.payment_input.setFixedHeight(33)
        self.payment_input.setStyleSheet("""
            padding: 0px 12px;
        """
        )
        payment_layout.addWidget(self.payment_input)
        form_layout.addWidget(bayar_label, 1, 0)
        form_layout.addLayout(payment_layout, 1, 1)

        pelanggan_label = QLabel("Nama Customer")
        pelanggan_label.setObjectName("formLabel")
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Opsional, misal: Pelanggan Umum")
        self.customer_input.setFixedHeight(33)
        self.customer_input.setStyleSheet("""
            QLineEdit {
                padding: 0px 12px;
            }
        """
        )
        form_layout.addWidget(pelanggan_label, 2, 0)
        form_layout.addWidget(self.customer_input, 2, 1)

        layout.addLayout(form_layout)

        notes_label = QLabel("Catatan Kasir")
        notes_label.setObjectName("formLabel")
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("tulis informasi disini")
        self.notes_input.setFixedHeight(50)
        layout.addWidget(self.notes_input)

        self.change_label = QLabel("Kembalian: Rp 0")
        self.change_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700;")
        layout.addWidget(self.change_label)

        return card

    def _create_quick_actions_card(self) -> QWidget:
        card = self._build_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        self.button_discount = QPushButton("Diskon")
        self.button_discount.setObjectName("warningButton")
        self.button_discount.setStyleSheet("""
            QPushButton#warningButton {
                background-color: #ffb020;
                color: #1f1300;
            }
            QPushButton#warningButton:hover {
                background-color: #ffd27a;
            }
        """)

        self.button_rounding = QPushButton("Pembulatan")
        self.button_rounding.setObjectName("secondaryButton")
        self.button_rounding.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #00c2ff;
                color: #02131a;
            }
            QPushButton#secondaryButton:hover {
                background-color: #86e8ff;
            }
        """)

        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.setObjectName("ghostDangerButton")
        self.button_cancel.setStyleSheet("""
            QPushButton#ghostDangerButton:hover {
                background-color: #243342;
            }
            QPushButton#ghostDangerButton {
                background-color: #241316;
                color: #ff8f98;
                border: 1px solid #59242a;
            }
        """)
        self.button_cancel.clicked.connect(self._clear_cart)

        self.button_pay = QPushButton("Bayar")
        self.button_pay.setObjectName("successButton")
        self.button_pay.setStyleSheet("""
            QPushButton#successButton:hover {
                background-color: #7dffb1;
            }
            QPushButton#successButton {
                background-color: #00ff85;
                color: #02140a;
            }
        """)

        button_grid = QGridLayout()
        button_grid.setHorizontalSpacing(10)
        button_grid.setVerticalSpacing(10)
        button_grid.addWidget(self.button_discount, 0, 0)
        button_grid.addWidget(self.button_rounding, 0, 1)
        button_grid.addWidget(self.button_cancel, 1, 0)
        button_grid.addWidget(self.button_pay, 1, 1)

        layout.addLayout(button_grid)
        return card

    def _add_product_from_search(self):
        keyword = self.search_input.text().strip().lower()
        if not keyword:
            return

        print(keyword)

    @staticmethod
    def _build_card() -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        return card

    def _clear_cart(self):
        self.cart_table.setRowCount(0)
        self.diskon_nominal = 0
        self.pembulatan_nominal = 0

    @staticmethod
    def _create_summary_row(parent_layout: QVBoxLayout, label_text: str, value_text: str) -> QLabel:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setStyleSheet("color: #b7c2cc; font-size: 13px;")
        value = QLabel(value_text)
        value.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700;")

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(value)
        parent_layout.addWidget(row)
        return value

    @staticmethod
    def _get_stylesheet() -> str:
        return """
                QWidget {
                    background-color: transparent;
                    color: #ffffff;
                    font-family: "Segoe UI";
                }
                QFrame#card {
                    background-color: #0d1117;
                    border: 2px solid #1d2630;
                    border-radius: 18px;
                }
                QLabel#smallBadge {
                    background-color: rgba(0, 255, 133, 0.12);
                    color: #7dfcc4;
                    border: 2px solid rgba(0, 255, 133, 0.4);
                    border-radius: 10px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit, QSpinBox {
                    background-color: #111827;
                    border: 2px solid #263241;
                    border-radius: 12px;
                    color: #ffffff;
                    padding: 10px 12px;
                    font-size: 13px;
                }
                QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QSpinBox:focus {
                    border: 2px solid #00c2ff;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 26px;
                }
                QPushButton {
                    min-height: 44px;
                    border-radius: 12px;
                    border: none;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 0 16px;
                }
                QTableWidget {
                    background-color: #0a0f14;
                    border: 1px solid #202a35;
                    border-radius: 14px;
                    gridline-color: #1d2630;
                    color: #ffffff;
                    padding: 6px;
                    selection-background-color: transparent;
                }
                QHeaderView::section {
                    background-color: #121a24;
                    color: #93a1af;
                    padding: 10px;
                    border: none;
                    border-bottom: 1px solid #263241;
                    font-size: 12px;
                    font-weight: 700;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #18212b;
                }
        """