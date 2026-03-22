from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
)
from dialog_title_bar import DialogTitleBar


class DiscountPopup(QDialog):
    def __init__(self, parent, discount_state: dict, apply_callback):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.apply_callback = apply_callback
        self.setObjectName("discountPopup")
        self.setMinimumWidth(360)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        self.title_bar = DialogTitleBar("Atur Diskon Transaksi", self)
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)

        persen_label = QLabel("Diskon (%)")
        persen_label.setStyleSheet("color: #d8e4ef; font-weight: 600;")
        self.percent_input = QLineEdit()
        self.percent_input.setPlaceholderText("Contoh: 10")
        self.percent_input.setValidator(QIntValidator(0, 100, self))

        nominal_label = QLabel("Diskon Nominal")
        nominal_label.setStyleSheet("color: #d8e4ef; font-weight: 600;")
        self.nominal_input = QLineEdit()
        self.nominal_input.setPlaceholderText("Contoh: 25.000")
        self.nominal_input.setValidator(QIntValidator(0, 999999999, self))

        form.addWidget(persen_label, 0, 0)
        form.addWidget(self.percent_input, 0, 1)
        form.addWidget(nominal_label, 1, 0)
        form.addWidget(self.nominal_input, 1, 1)
        layout.addLayout(form)

        self.preview_label = QLabel("Diskon akan diterapkan ke total transaksi.")
        self.preview_label.setStyleSheet("color: #7dfcc4; font-size: 12px;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.reset_button = QPushButton("Reset")
        self.cancel_button = QPushButton("Batal")
        self.apply_button = QPushButton("Terapkan")
        self.apply_button.setObjectName("primaryButton")

        button_row.addWidget(self.reset_button)
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        layout.addLayout(button_row)

        current_mode = discount_state.get("mode")
        current_percent = int(discount_state.get("percent") or 0)
        current_nominal = int(discount_state.get("nominal_input") or 0)

        if current_mode == "percent" and current_percent > 0:
            self.percent_input.setText(str(current_percent))
        elif current_mode == "nominal" and current_nominal > 0:
            self.nominal_input.setText(self._format_nominal_text(current_nominal))

        self.percent_input.textChanged.connect(self._sync_input_state)
        self.percent_input.textChanged.connect(self._update_preview)
        self.nominal_input.textChanged.connect(self._handle_nominal_changed)
        self.reset_button.clicked.connect(self._reset_discount)
        self.cancel_button.clicked.connect(self.close)
        self.apply_button.clicked.connect(self._apply_discount)

        self.setStyleSheet("""
            QDialog#discountPopup {
                background-color: #0d1117;
                border: 2px solid #00ff00;
            }
            QWidget#contentWidget {
                background-color: transparent;
            }
            QDialog#discountPopup QLineEdit {
                background-color: #111827;
                border: 2px solid #263241;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QDialog#discountPopup QLineEdit:disabled {
                color: #6b7b8c;
                background-color: #0b1016;
            }
            QDialog#discountPopup QPushButton {
                min-height: 34px;
                padding: 0px 14px;
                border-radius: 10px;
            }
        """)

        self._sync_input_state()
        self._update_preview()

    @staticmethod
    def _digits_only(text: str) -> str:
        return "".join(char for char in text if char.isdigit())

    @staticmethod
    def _format_nominal_text(value: int) -> str:
        return f"{int(value):,}".replace(",", ".")

    def _handle_nominal_changed(self, text: str):
        digits = self._digits_only(text)
        formatted = self._format_nominal_text(int(digits)) if digits else ""

        if formatted != text:
            cursor_pos_from_right = len(text) - self.nominal_input.cursorPosition()
            self.nominal_input.blockSignals(True)
            self.nominal_input.setText(formatted)
            self.nominal_input.blockSignals(False)
            self.nominal_input.setCursorPosition(max(0, len(formatted) - cursor_pos_from_right))

        self._sync_input_state()
        self._update_preview()

    def _sync_input_state(self):
        percent_filled = bool(self._digits_only(self.percent_input.text()))
        nominal_filled = bool(self._digits_only(self.nominal_input.text()))

        self.percent_input.setEnabled(not nominal_filled)
        self.nominal_input.setEnabled(not percent_filled)

        if not percent_filled and not nominal_filled:
            self.percent_input.setEnabled(True)
            self.nominal_input.setEnabled(True)

    def _update_preview(self):
        percent_value = int(self._digits_only(self.percent_input.text()) or 0)
        nominal_value = int(self._digits_only(self.nominal_input.text()) or 0)

        if percent_value > 0:
            self.preview_label.setText(f"Diskon {percent_value}% akan dihitung dari subtotal transaksi.")
        elif nominal_value > 0:
            self.preview_label.setText(f"Diskon nominal Rp {self._format_nominal_text(nominal_value)} akan dipotong dari subtotal.")
        else:
            self.preview_label.setText("Kosongkan kedua kolom untuk menghapus diskon.")

    def _reset_discount(self):
        self.percent_input.clear()
        self.nominal_input.clear()
        self._apply_discount()

    def _apply_discount(self):
        percent_value = int(self._digits_only(self.percent_input.text()) or 0)
        nominal_value = int(self._digits_only(self.nominal_input.text()) or 0)

        if percent_value > 0:
            payload = {"mode": "percent", "percent": percent_value, "nominal": 0}
        elif nominal_value > 0:
            payload = {"mode": "nominal", "percent": 0, "nominal": nominal_value}
        else:
            payload = {"mode": None, "percent": 0, "nominal": 0}

        self.apply_callback(payload)
        self.close()
