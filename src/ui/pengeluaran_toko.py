from __future__ import annotations

from typing import Optional
from config import asset_uri
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont, QIntValidator, QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDateEdit,
    QComboBox, QLineEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)

from src.database.database import DatabaseManager
from src.utils.fungsi import CustomCalendar
from src.utils.message import CustomMessageBox


class PengeluaranTokoWindow(QWidget):
    CATEGORIES = ["Belanja Stok Produk", "Belanja Operasinal", "Listrik", "Air", "Lainnya"]
    METHODS = ["Cash", "Transfer", "E-Wallet"]
    SORT_OPTIONS = ["Tanggal (Asc)", "Tanggal (Desc)", "Nominal (Asc)", "Nominal (Desc)"]
    DATE_RANGE_OPTIONS = ["Satu Bulan", "Enam Bulan", "Satu Tahun", "Dua Tahun", "Semua"]

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.editing_expense_id: int | None = None

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
        self.card_total_hari_ini = self._create_summary_card("Total Hari Ini", "Rp 0", "#254B4B")
        self.card_total_bulan_ini = self._create_summary_card("Total Bulan Ini", "Rp 0", "#1D3E53")
        self.card_jumlah_transaksi = self._create_summary_card("Jumlah Transaksi", "0", "#432152")
        summary_layout.addWidget(self.card_total_hari_ini)
        summary_layout.addWidget(self.card_total_bulan_ini)
        summary_layout.addWidget(self.card_jumlah_transaksi)
        root_layout.addLayout(summary_layout)

        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background-color: #162023; border: 1px solid #26363A; border-radius: 10px; }")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(14, 14, 14, 14)
        form_layout.setSpacing(10)

        # --- STYLESHEET KHUSUS DATE EDIT & CALENDAR POPUP ---
        date_style = f"""
            QDateEdit {{
                background-color: #11181A;
                color: #E0E0E0;
                border: 1px solid #28373B;
                border-radius: 6px;
                padding: 8px;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #28373B;
            }}
            QDateEdit::down-arrow {{
                image: url({asset_uri("icon_down.svg")});
                width: 12px;
                height: 12px;
            }}
            QCalendarWidget QWidget {{
                background-color: #11181A;
                color: #E0E0E0;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: #1A2C30;
                border-bottom: 1px solid #28373B;
                min-height: 30px;
            }}
            QCalendarWidget QToolButton {{
                color: #E0E0E0;
                background-color: transparent;
                font-weight: bold;
                padding: 4px;
                margin: 2px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: #26363A;
                border-radius: 4px;
            }}
            QCalendarWidget QToolButton::menu-indicator {{
                image: none;
            }}
            QMenu {{
                background-color: #1A2C30;
                color: #E0E0E0;
                border: 1px solid #28373B;
            }}
            QMenu::item {{
                background-color: transparent;
                color: #E0E0E0;
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: #0078D7;
                color: white;
            }}
            QCalendarWidget QTableView {{
                background-color: #11181A;
                color: #E0E0E0;
                selection-background-color: #0078D7;
                selection-color: white;
            }}
            QCalendarWidget QSpinBox {{
                background-color: #11181A;
                color: #E0E0E0;
                border: 1px solid #28373B;
            }}
        """

        # --- STYLESHEET KHUSUS COMBOBOX ---
        combo_style = f"""
            QComboBox {{
                background-color: #11181A;
                color: #E0E0E0;
                padding: 4px 8px;
                border: 1px solid #28373B;
                border-radius: 6px;
                padding: 8px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #28373B;
            }}
            QComboBox::down-arrow {{
                image: url({asset_uri("icon_down.svg")});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1A2C30;
                color: #E0E0E0;
                border: 1px solid #28373B;
                selection-background-color: #0078D7;
            }}
        """

        header_format = QTextCharFormat()
        header_format.setBackground(QColor("#1A2C30"))
        header_format.setForeground(QColor("#A9B7C6"))

        row_1 = QHBoxLayout()
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(date_style)
        cal_widget = CustomCalendar()
        cal_widget.setHeaderTextFormat(header_format)
        self.date_input.setCalendarWidget(cal_widget)

        self.category_input = QComboBox()
        self.category_input.addItems(self.CATEGORIES)
        self.category_input.setStyleSheet(combo_style)
        row_1.addLayout(self._field_layout("📅 Tanggal *", self.date_input))
        row_1.addLayout(self._field_layout("🏷 Kategori *", self.category_input))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Masukkan nominal")
        self.amount_input.setValidator(QIntValidator(1, 1_000_000_000, self))
        self.method_input = QComboBox()
        self.method_input.addItems(self.METHODS)
        self.method_input.setStyleSheet(combo_style)
        row_1.addLayout(self._field_layout("💰 Nominal *", self.amount_input))
        row_1.addLayout(self._field_layout("💳 Metode *", self.method_input))
        form_layout.addLayout(row_1)

        row_2 = QHBoxLayout()
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Catatan (opsional)")
        self.note_input.setMinimumHeight(70)
        self.note_input.setMaximumHeight(75)
        self.note_input.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 150);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(150, 150, 150, 255);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        note_layout = self._field_layout("📝 Catatan", self.note_input)
        row_2.addLayout(note_layout)
        button_lay = QVBoxLayout()
        button_lay.addStretch()
        self.save_button = QPushButton("💾 Simpan")
        self.reset_button = QPushButton("🔄 Reset")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setStyleSheet(self._button_style("#FF8C00", "#E67E22"))
        self.reset_button.setStyleSheet(self._button_style("#FF8C00", "#FF8C00", outline=True, text_color="#FF8C00"))
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
        self.filter_category_input.setStyleSheet(combo_style)
        self.sort_input = QComboBox()
        self.sort_input.addItems(self.SORT_OPTIONS)
        self.sort_input.setStyleSheet(combo_style)
        self.date_range_input = QComboBox()
        self.date_range_input.addItems(self.DATE_RANGE_OPTIONS)
        self.date_range_input.setCurrentText("Satu Tahun")
        self.date_range_input.setStyleSheet(combo_style)
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
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(3, 100)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(5, 200)
        self.table.setRowHeight(0, 50)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #141C1F;
                alternate-background-color: #192427;
                color: #E0E0E0;
                border: none;
            }
            QHeaderView::section {
                background-color: #1A2C30;
                color: #E0E0E0;
                font-weight: bold;
                padding: 8px;
                border: none;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #26363A;
            }
            QTableWidget::item:selected {
                background-color: #26363A;
            }

            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 150);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(150, 150, 150, 255);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        root_layout.addWidget(self.table)

        self.setStyleSheet("""
            /* Main container styles */
            QWidget { background-color: #141C1F; color: #E0E0E0; }
            /* Prevent button styles from being overridden */
            QPushButton { background-color: #FF8C00; color: white; border: none; border-radius: 6px; padding: 0px 0px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background-color: #E67E22; }
            QPushButton:disabled { background-color: #666666; color: #b0b0b0; }
            QLineEdit, QTextEdit {
                background-color: #11181A;
                color: #E0E0E0;
                border: 1px solid #28373B;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #26363A;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #385A64;
                background-color: #11181A;
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
            self.table.setRowHeight(row, 50)
            date_item = self._center_item(item["tanggal"])
            date_item.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, self._center_item(item["kategori"]))
            self.table.setItem(row, 2, self._center_item(self._format_rupiah(item["nominal"])))
            self.table.setItem(row, 3, self._center_item(item["metode"]))
            self.table.setItem(row, 4, QTableWidgetItem(item["catatan"]))
            self.table.setCellWidget(row, 5, self._create_action_widget(item["id"]))

    def _refresh_summary_cards(self):
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
            else:
                date_from = None
                date_to = None
            if date_from:
                filters["date_from"] = date_from.toString("yyyy-MM-dd")
            if date_to:
                filters["date_to"] = date_to.toString("yyyy-MM-dd")

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
            else:
                date_from = None
                date_to = None
            if date_from:
                filters["date_from"] = date_from.toString("yyyy-MM-dd")
            if date_to:
                filters["date_to"] = date_to.toString("yyyy-MM-dd")

        self.filtered_expense_data = self.db.get_pengeluaran(filters)

        if sort_key == "Tanggal (Asc)":
            self.filtered_expense_data.sort(key=lambda x: x["tanggal"])
        elif sort_key == "Tanggal (Desc)":
            self.filtered_expense_data.sort(key=lambda x: x["tanggal"], reverse=True)
        elif sort_key == "Nominal (Asc)":
            self.filtered_expense_data.sort(key=lambda x: x["nominal"])
        elif sort_key == "Nominal (Desc)":
            self.filtered_expense_data.sort(key=lambda x: x["nominal"], reverse=True)

        self._refresh_table()
        self._refresh_summary_cards()

    def _on_save(self):
        if not self._validate_form():
            CustomMessageBox.warning(self, "Form Tidak Valid", "Mohon lengkapi field wajib dengan benar.")
            return

        payload = self._collect_form_data()
        if self.editing_expense_id is not None:
            result = self.db.update_pengeluaran(
                self.editing_expense_id,
                payload["date"],
                payload["category"],
                payload["amount"],
                payload["method"],
                payload["note"]
            )
            if not result["success"]:
                CustomMessageBox.warning(self, "Error", result["message"])
                return
        else:
            result = self.db.insert_pengeluaran(
                payload["date"],
                payload["category"],
                payload["amount"],
                payload["method"],
                payload["note"]
            )
            if not result["success"]:
                CustomMessageBox.warning(self, "Error", result["message"])
                return

        self._apply_search_filter_sort()
        self._clear_form()

    def _on_edit(self, expense_id: int):
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
        confirm = CustomMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Yakin ingin menghapus data pengeluaran ini?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        result = self.db.delete_pengeluaran(expense_id)
        if not result["success"]:
            CustomMessageBox.warning(self, "Error", result["message"])
            return

        if self.editing_expense_id == expense_id:
            self._clear_form()

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
                border-radius: 10px;
                border: none;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        icon_label = QLabel("📈 ")
        icon_label.setStyleSheet("font-size: 16px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #d8d8d8; font-size: 13px; font-weight: 600; border: None")
        title_label.setText("📈 " + title)
        value_label = QLabel(value)
        value_label.setObjectName("summaryValue")
        value_label.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold; border: None")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def _create_action_widget(self, expense_id: int) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent; border: none;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for label, color, hover in [("Edit", "#0078D7", "#0062ad"), ("Hapus", "#d9534f", "#b94441")]:
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #ffffff;
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 50px;
                    min-height: 0px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                    border-color: {hover};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if label == "Edit":
                btn.clicked.connect(lambda _, eid=expense_id: self._on_edit(eid))
            else:
                btn.clicked.connect(lambda _, eid=expense_id: self._on_delete(eid))
            layout.addWidget(btn)

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
    def _button_style(bg: str, hover: str, padding: str = "6px 12px", outline: bool = False, text_color: Optional[str] = None) -> str:
        if outline:
            if text_color is None:
                text_color = bg
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: 2px solid {text_color};
                    border-radius: 6px;
                    padding: {padding};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {text_color};
                    color: #ffffff;
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    color: #666666;
                    border-color: #666666;
                }}
            """
        else:
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