from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from src.ui.dialog_title_bar import DialogTitleBar


class AuthKeyPopup(QDialog):
    """
    Popup autentikasi sederhana yang meminta key/password sebelum
    mengizinkan aksi tertentu — mirip perintah `su` di Linux.

    Cara pakai:
        popup = AuthKeyPopup(parent, verify_callback=my_verify_fn)
        popup.exec()

    verify_callback(key: str) -> tuple[bool, dict | str]
        Dipanggil saat tombol Konfirmasi ditekan.
        Harus mengembalikan tuple:
          - (True, user_data)  → key valid, popup ditutup (accept)
          - (False, error_msg) → key salah, pesan error ditampilkan
    """

    def __init__(self, parent, verify_callback, title: str = "Autentikasi Diperlukan"):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.verify_callback = verify_callback
        self.verified_data = None  # Menyimpan data user setelah verifikasi berhasil
        self.setObjectName("authKeyPopup")
        self.setMinimumWidth(380)

        # ── Main layout ───────────────────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        self.title_bar = DialogTitleBar(title, self)
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # ── Instruksi ─────────────────────────────────────────────
        instruction_label = QLabel("Masukkan key untuk melanjutkan:")
        instruction_label.setStyleSheet("color: #d8e4ef; background-color: transparent; font-weight: 600;")
        layout.addWidget(instruction_label)

        # ── Input key ─────────────────────────────────────────────
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Masukkan key…")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)

        # ── Status label (untuk pesan error) ──────────────────────
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff5252; background-color: transparent; font-size: 12px;")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        # ── Tombol aksi ──────────────────────────────────────────
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.cancel_button = QPushButton("Batal")
        self.confirm_button = QPushButton("Konfirmasi")
        self.confirm_button.setObjectName("primaryButton")

        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.confirm_button)
        layout.addLayout(button_row)

        # ── Sinyal ───────────────────────────────────────────────
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self._on_confirm)
        self.key_input.returnPressed.connect(self._on_confirm)

        # ── Stylesheet ───────────────────────────────────────────
        self.setStyleSheet("""
            QDialog#authKeyPopup {
                background-color: #0d1117;
                border: 2px solid #f9a825;
            }
            QWidget#contentWidget {
                background-color: transparent;
            }
            QDialog#authKeyPopup QLineEdit {
                background-color: #111827;
                border: 2px solid #263241;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QDialog#authKeyPopup QLineEdit:focus {
                border: 2px solid #f9a825;
            }
            QDialog#authKeyPopup QPushButton {
                min-height: 34px;
                padding: 0px 14px;
                border-radius: 10px;
                background-color: #1a2332;
                color: #8899aa;
                border: 1px solid #263241;
                font-weight: 600;
            }
            QDialog#authKeyPopup QPushButton:hover {
                background-color: #263241;
                color: #d8e4ef;
            }
            QDialog#authKeyPopup QPushButton#primaryButton {
                background-color: #f9a825;
                color: #0d1117;
                border: 1px solid #f9a825;
                font-weight: 700;
            }
            QDialog#authKeyPopup QPushButton#primaryButton:hover {
                background-color: #fbc02d;
                color: #0d1117;
            }
        """)

    def _on_confirm(self):
        key = self.key_input.text().strip()
        if not key:
            self._show_error("Key tidak boleh kosong.")
            return

        success, data = self.verify_callback(key)
        if success:
            self.verified_data = data
            self.accept()
        else:
            self._show_error(data if isinstance(data, str) else "Key salah. Silakan coba lagi.")
            self.key_input.clear()
            self.key_input.setFocus()

    def _show_error(self, message: str):
        self.status_label.setText(message)
        self.status_label.show()
