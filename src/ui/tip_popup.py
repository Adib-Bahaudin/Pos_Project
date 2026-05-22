from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
)
from src.ui.dialog_title_bar import DialogTitleBar


class TipPopup(QDialog):
    def __init__(self, parent, current_tip: int, change_amount: int, apply_callback):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.apply_callback = apply_callback
        self.change_amount = max(0, change_amount)
        self.setObjectName("tipPopup")
        self.setMinimumWidth(380)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        self.title_bar = DialogTitleBar("Tip / Bonus Kasir", self)
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # --- Input nominal ---
        nominal_label = QLabel("Nominal Tip (Rp)")
        nominal_label.setStyleSheet("color: #d8e4ef; font-weight: 600;")
        layout.addWidget(nominal_label)

        self.nominal_input = QLineEdit()
        self.nominal_input.setPlaceholderText("Contoh: 5.000")
        self.nominal_input.setValidator(QIntValidator(0, 999999999, self))
        if current_tip > 0:
            self.nominal_input.setText(self._format_nominal_text(current_tip))
        layout.addWidget(self.nominal_input)

        layout.addSpacing(5)

        preset_grid = QGridLayout()
        preset_grid.setHorizontalSpacing(8)
        preset_grid.setVerticalSpacing(8)

        presets = [
            ("Rp 5.000", 5000),
            ("Rp 10.000", 10000),
            ("Rp 20.000", 20000),
            ("Rp 50.000", 50000),
        ]

        for i, (label, value) in enumerate(presets):
            btn = QPushButton(label)
            btn.setObjectName("presetButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, v=value: self._set_nominal(v))
            preset_grid.addWidget(btn, 0, i)

        # Tombol khusus: Ambil Kembalian
        self.btn_change = QPushButton(f"Ambil Kembalian ({self._format_nominal_text(self.change_amount)})")
        self.btn_change.setObjectName("presetChangeButton")
        self.btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_change.setEnabled(self.change_amount > 0)
        self.btn_change.clicked.connect(lambda: self._set_nominal(self.change_amount))
        preset_grid.addWidget(self.btn_change, 1, 0, 1, 4)

        layout.addLayout(preset_grid)

        # --- Preview label ---
        self.preview_label = QLabel("Tip akan ditambahkan ke total transaksi.")
        self.preview_label.setStyleSheet("color: #80d4e0; font-size: 12px;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)

        # --- Action buttons ---
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

        # --- Signals ---
        self.nominal_input.textChanged.connect(self._handle_nominal_changed)
        self.reset_button.clicked.connect(self._reset_tip)
        self.cancel_button.clicked.connect(self.close)
        self.apply_button.clicked.connect(self._apply_tip)

        self.setStyleSheet("""
            QDialog#tipPopup {
                background-color: #0d1117;
                border: 2px solid #00897b;
            }
            QWidget#contentWidget {
                background-color: transparent;
            }
            QDialog#tipPopup QLineEdit {
                background-color: #111827;
                border: 2px solid #263241;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QDialog#tipPopup QLineEdit:focus {
                border: 2px solid #00897b;
            }
            QDialog#tipPopup QPushButton {
                min-height: 34px;
                padding: 0px 14px;
                border-radius: 10px;
            }
            QPushButton#presetButton {
                background-color: #113333;
                color: #80d4e0;
                border: 1px solid #1a5050;
                font-weight: 600;
            }
            QPushButton#presetButton:hover {
                background-color: #1a5050;
                color: #b2ebf2;
            }
            QPushButton#presetChangeButton {
                background-color: #1a3a4a;
                color: #80cbc4;
                border: 1px solid #26606a;
                font-weight: 600;
            }
            QPushButton#presetChangeButton:hover {
                background-color: #26606a;
                color: #b2dfdb;
            }
            QPushButton#presetChangeButton:disabled {
                background-color: #0b1016;
                color: #4a5568;
                border: 1px solid #1d2630;
            }
        """)

        self._update_preview()

    @staticmethod
    def _digits_only(text: str) -> str:
        return "".join(char for char in text if char.isdigit())

    @staticmethod
    def _format_nominal_text(value: int) -> str:
        return f"{int(value):,}".replace(",", ".")

    def _set_nominal(self, value: int):
        self.nominal_input.setText(self._format_nominal_text(value))

    def _handle_nominal_changed(self, text: str):
        digits = self._digits_only(text)
        formatted = self._format_nominal_text(int(digits)) if digits else ""

        if formatted != text:
            cursor_pos_from_right = len(text) - self.nominal_input.cursorPosition()
            self.nominal_input.blockSignals(True)
            self.nominal_input.setText(formatted)
            self.nominal_input.blockSignals(False)
            self.nominal_input.setCursorPosition(max(0, len(formatted) - cursor_pos_from_right))

        self._update_preview()

    def _update_preview(self):
        nominal_value = int(self._digits_only(self.nominal_input.text()) or 0)
        if nominal_value > 0:
            self.preview_label.setText(
                f"Tip sebesar Rp {self._format_nominal_text(nominal_value)} akan ditambahkan ke total."
            )
        else:
            self.preview_label.setText("Kosongkan kolom atau tekan Reset untuk menghapus tip.")

    def _reset_tip(self):
        self.nominal_input.clear()
        self._apply_tip()

    def _apply_tip(self):
        nominal_value = int(self._digits_only(self.nominal_input.text()) or 0)
        self.apply_callback(max(0, nominal_value))
        self.close()
