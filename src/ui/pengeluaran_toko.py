from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDateEdit,
    QComboBox, QLineEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)

from src.database.database import DatabaseManager


class PengeluaranTokoWindow(QWidget):
    CATEGORIES = ["Belanja Stok Produk", "Belanja Operasinal", "Listrik", "Air", "Lainnya"]
    METHODS = ["Cash", "Transfer", "E-Wallet"]
    SORT_OPTIONS = ["Tanggal (Asc)", "Tanggal (Desc)", "Nominal (Asc)", "Nominal (Desc)"]
    DATE_RANGE_OPTIONS = ["Satu Bulan", "Enam Bulan", "Satu Tahun", "Dua Tahun", "Semua"]

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.editing_expense_id: int | None = None  # Store the database ID of the expense being edited

        self._build_ui()
        self._connect_signals()
        self._apply_search_filter_sort()
        self._validate_form()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        title = QLabel("Pengeluaran Toko")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; background-color: transparent")
        root_layout.addWidget(title)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        self.card_total_hari_ini = self._create_summary_card("Total Hari Ini", "Rp 0", "#2f4f4f")
        self.card_total_bulan_ini = self._create_summary_card("Total Bulan Ini", "Rp 0", "#203a43")
        self.card_jumlah_transaksi = self._create_summary_card("Jumlah Transaksi", "0", "#3b2f58")
        summary_layout.addWidget(self.card_total_hari_ini)
        summary_layout.addWidget(self.card_total_bulan_ini)
        summary_layout.addWidget(self.card_jumlah_transaksi)
        root_layout.addLayout(summary_layout)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background-color: #171717; border: 1px solid #3c3c3c; border-radius: 8px; }")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(14, 14, 14, 14)
        form_layout.setSpacing(10)

        row_1 = QHBoxLayout()
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.category_input = QComboBox()
        self.category_input.addItems(self.CATEGORIES)
        row_1.addLayout(self._field_layout("Tanggal *", self.date_input))
        row_1.addLayout(self._field_layout("Kategori *", self.category_input))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Masukkan nominal")
        self.amount_input.setValidator(QIntValidator(1, 1_000_000_000, self))
        self.method_input = QComboBox()
        self.method_input.addItems(self.METHODS)
        row_1.addLayout(self._field_layout("Nominal *", self.amount_input))
        row_1.addLayout(self._field_layout("Metode *", self.method_input))
        form_layout.addLayout(row_1)

        row_2 = QHBoxLayout()
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Catatan (opsional)")
        self.note_input.setMinimumHeight(70)
        self.note_input.setMaximumHeight(75)
        note_layout = self._field_layout("Catatan", self.note_input)
        row_2.addLayout(note_layout)
        button_lay = QVBoxLayout()
        button_lay.addStretch()
        self.save_button = QPushButton("Simpan")
        self.reset_button = QPushButton("Reset")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setStyleSheet(self._button_style("#00a86b", "#00895a"))
        self.reset_button.setStyleSheet(self._button_style("#ff8c00", "#d97700"))
        button_lay.addWidget(self.reset_button)
        button_lay.addWidget(self.save_button)
        row_2.addLayout(button_lay)
        form_layout.addLayout(row_2)

        self.form_error_label = QLabel("")
        self.form_error_label.setStyleSheet("color: #ff6b6b; font-size: 11px; border: None")
        form_layout.addWidget(self.form_error_label)

        root_layout.addWidget(form_frame)

        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kategori/catatan...")
        self.filter_category_input = QComboBox()
        self.filter_category_input.addItems(["Semua", *self.CATEGORIES])
        self.sort_input = QComboBox()
        self.sort_input.addItems(self.SORT_OPTIONS)
        self.date_range_input = QComboBox()
        self.date_range_input.addItems(self.DATE_RANGE_OPTIONS)
        self.date_range_input.setCurrentText("Satu Tahun")
        filter_layout.addWidget(self.date_range_input, 1)
        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(self.filter_category_input, 1)
        filter_layout.addWidget(self.sort_input, 1)
        root_layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Kategori", "Nominal", "Metode", "Catatan", "Aksi"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                alternate-background-color: #545454;
                color: white;
                border: 1px solid #3c3c3c;
            }
            QHeaderView::section {
                background-color: #a6a6a6;
                color: black;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        root_layout.addWidget(self.table)

        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #101010;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #ffffff;
            }
        """)

    def _connect_signals(self):
        self.amount_input.textChanged.connect(self._validate_form)
        self.category_input.currentIndexChanged.connect(self._validate_form)
        self.method_input.currentIndexChanged.connect(self._validate_form)
        self.date_input.dateChanged.connect(self._validate_form)
        self.search_input.textChanged.connect(self._apply_search_filter_sort)
        self.filter_category_input.currentIndexChanged.connect(self._apply_search_filter_sort)
        self.sort_input.currentIndexChanged.connect(self._apply_search_filter_sort)
        self.date_range_input.currentIndexChanged.connect(self._apply_search_filter_sort)
        self.save_button.clicked.connect(self._on_save)
        self.reset_button.clicked.connect(self._clear_form)

    def _validate_form(self) -> bool:
        amount_text = self.amount_input.text().strip()
        if not self.category_input.currentText().strip():
            self.form_error_label.setText("Kategori wajib diisi.")
            self.save_button.setEnabled(False)
            return False
        if not self.method_input.currentText().strip():
            self.form_error_label.setText("Metode wajib diisi.")
            self.save_button.setEnabled(False)
            return False
        if not amount_text:
            self.form_error_label.setText("Nominal wajib diisi.")
            self.save_button.setEnabled(False)
            return False
        if not amount_text.isdigit() or int(amount_text) <= 0:
            self.form_error_label.setText("Nominal harus berupa angka lebih dari 0.")
            self.save_button.setEnabled(False)
            return False

        self.form_error_label.setText("")
        self.save_button.setEnabled(True)
        return True

    def _collect_form_data(self) -> dict:
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "category": self.category_input.currentText().strip(),
            "amount": int(self.amount_input.text().strip()),
            "method": self.method_input.currentText().strip(),
            "note": self.note_input.toPlainText().strip(),
        }

    def _clear_form(self):
        self.date_input.setDate(QDate.currentDate())
        self.category_input.setCurrentIndex(0)
        self.amount_input.clear()
        self.method_input.setCurrentIndex(0)
        self.note_input.clear()
        self.editing_expense_id = None
        self.save_button.setText("Simpan")
        self.form_error_label.setText("")
        self._validate_form()

    def _refresh_table(self):
        self.table.setRowCount(len(self.filtered_expense_data))
        for row, item in enumerate(self.filtered_expense_data):
            # Store the expense ID in the first column's UserRole for later retrieval in edit/delete
            date_item = self._center_item(item["tanggal"])
            date_item.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, self._center_item(item["kategori"]))
            self.table.setItem(row, 2, self._center_item(self._format_rupiah(item["nominal"])))
            self.table.setItem(row, 3, self._center_item(item["metode"]))
            self.table.setItem(row, 4, QTableWidgetItem(item["catatan"]))
            # Pass the expense ID to the action widget (so edit/delete know which expense to operate on)
            self.table.setCellWidget(row, 5, self._create_action_widget(item["id"]))

    def _refresh_summary_cards(self):
        # Build the same filters as in _apply_search_filter_sort to get statistics for the current view
        keyword = self.search_input.text().strip()
        selected_category = self.filter_category_input.currentText()
        date_range_key = self.date_range_input.currentText()

        filters = {}
        if keyword:
            filters["search_keyword"] = keyword
        if selected_category != "Semua":
            filters["kategori"] = selected_category
        if date_range_key != "Semua":
            today = QDate.currentDate()
            if date_range_key == "Satu Bulan":
                date_from = today.addMonths(-1)
                date_to = today
            elif date_range_key == "Enam Bulan":
                date_from = today.addMonths(-6)
                date_to = today
            elif date_range_key == "Satu Tahun":
                date_from = today.addYears(-1)
                date_to = today
            elif date_range_key == "Dua Tahun":
                date_from = today.addYears(-2)
                date_to = today
            else:  # Semua
                date_from = None
                date_to = None
            if date_from:
                filters["date_from"] = date_from.toString("yyyy-MM-dd")
            if date_to:
                filters["date_to"] = date_to.toString("yyyy-MM-dd")

        # Get statistics from the database
        stats = self.db.get_pengeluaran_statistics(filters)
        total_today = stats["total_today"]
        total_month = stats["total_month"]
        total_transactions = stats["total_count"]

        self._set_card_value(self.card_total_hari_ini, self._format_rupiah(total_today))
        self._set_card_value(self.card_total_bulan_ini, self._format_rupiah(total_month))
        self._set_card_value(self.card_jumlah_transaksi, str(total_transactions))

    def _apply_search_filter_sort(self):
        keyword = self.search_input.text().strip()
        selected_category = self.filter_category_input.currentText()
        sort_key = self.sort_input.currentText()
        date_range_key = self.date_range_input.currentText()

        # Build filters for the database query
        filters = {}
        if keyword:
            filters["search_keyword"] = keyword
        if selected_category != "Semua":
            filters["kategori"] = selected_category
        if date_range_key != "Semua":
            # We'll handle date range in the database method by adding date_from and date_to filters.
            today = QDate.currentDate()
            if date_range_key == "Satu Bulan":
                date_from = today.addMonths(-1)
                date_to = today
            elif date_range_key == "Enam Bulan":
                date_from = today.addMonths(-6)
                date_to = today
            elif date_range_key == "Satu Tahun":
                date_from = today.addYears(-1)
                date_to = today
            elif date_range_key == "Dua Tahun":
                date_from = today.addYears(-2)
                date_to = today
            else:  # Semua
                date_from = None
                date_to = None
            if date_from:
                filters["date_from"] = date_from.toString("yyyy-MM-dd")
            if date_to:
                filters["date_to"] = date_to.toString("yyyy-MM-dd")

        # Fetch data from the database
        self.filtered_expense_data = self.db.get_pengeluaran(filters)

        # Apply sorting (the database method returns data sorted by tanggal DESC, id DESC by default)
        # We'll re-sort based on the UI sort option
        if sort_key == "Tanggal (Asc)":
            self.filtered_expense_data.sort(key=lambda x: x["tanggal"])
        elif sort_key == "Tanggal (Desc)":
            self.filtered_expense_data.sort(key=lambda x: x["tanggal"], reverse=True)
        elif sort_key == "Nominal (Asc)":
            self.filtered_expense_data.sort(key=lambda x: x["nominal"])
        elif sort_key == "Nominal (Desc)":
            self.filtered_expense_data.sort(key=lambda x: x["nominal"], reverse=True)
        # Note: the default order from the database is tanggal DESC, id DESC, which matches "Tanggal (Desc)"

        self._refresh_table()
        self._refresh_summary_cards()

    def _on_save(self):
        if not self._validate_form():
            QMessageBox.warning(self, "Form Tidak Valid", "Mohon lengkapi field wajib dengan benar.")
            return

        payload = self._collect_form_data()
        if self.editing_expense_id is not None:
            # Update existing expense
            result = self.db.update_pengeluaran(
                self.editing_expense_id,
                payload["date"],
                payload["category"],
                payload["amount"],
                payload["method"],
                payload["note"]
            )
            if not result["success"]:
                QMessageBox.warning(self, "Error", result["message"])
                return
        else:
            # Insert new expense
            result = self.db.insert_pengeluaran(
                payload["date"],
                payload["category"],
                payload["amount"],
                payload["method"],
                payload["note"]
            )
            if not result["success"]:
                QMessageBox.warning(self, "Error", result["message"])
                return

        self._apply_search_filter_sort()
        self._clear_form()

    def _on_edit(self, expense_id: int):
        # Fetch the expense from the database using the id filter
        filters = {"id": expense_id}
        expenses = self.db.get_pengeluaran(filters)
        if not expenses:
            return
        selected = expenses[0]
        self.editing_expense_id = expense_id
        self.date_input.setDate(QDate.fromString(selected["tanggal"], "yyyy-MM-dd"))
        self.category_input.setCurrentText(selected["kategori"])
        self.amount_input.setText(str(selected["nominal"]))
        self.method_input.setCurrentText(selected["metode"])
        self.note_input.setPlainText(selected["catatan"])
        self.save_button.setText("Simpan Perubahan")
        self._validate_form()

    def _on_delete(self, expense_id: int):
        confirm = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Yakin ingin menghapus data pengeluaran ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Delete from the database
        result = self.db.delete_pengeluaran(expense_id)
        if not result["success"]:
            QMessageBox.warning(self, "Error", result["message"])
            return

        # If we were editing this expense, clear the form
        if self.editing_expense_id == expense_id:
            self._clear_form()

        # Refresh the table and summary cards
        self._apply_search_filter_sort()

    @staticmethod
    def _field_layout(label_text: str, widget: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(0)
        label = QLabel(f"  {label_text}")
        label.setFixedHeight(25)
        label.setStyleSheet("color: #d7d7d7; font-weight: bold; border: None")
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def _create_summary_card(self, title: str, value: str, bg_color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #d8d8d8; font-size: 12px; border: None")
        value_label = QLabel(value)
        value_label.setObjectName("summaryValue")
        value_label.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; border: None")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def _create_action_widget(self, expense_id: int) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)
        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Hapus")
        edit_button.setStyleSheet(self._button_style("#0078D7", "#0062ad", padding="4px 10px"))
        delete_button.setStyleSheet(self._button_style("#d9534f", "#b94441", padding="4px 10px"))
        edit_button.clicked.connect(lambda _, eid=expense_id: self._on_edit(eid))
        delete_button.clicked.connect(lambda _, eid=expense_id: self._on_delete(eid))
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        return widget

    @staticmethod
    def _center_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    @staticmethod
    def _set_card_value(card: QFrame, value: str):
        label = card.findChild(QLabel, "summaryValue")
        if label:
            label.setText(value)

    @staticmethod
    def _format_rupiah(value: int) -> str:
        return f"Rp {value:,}".replace(",", ".")

    @staticmethod
    def _button_style(bg: str, hover: str, padding: str = "6px 12px") -> str:
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: {padding};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: #666666;
                color: #b0b0b0;
            }}
        """