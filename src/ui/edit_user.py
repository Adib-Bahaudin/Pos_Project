from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QPushButton,
    QDialog, QLineEdit
)

from src.database.database import DatabaseManager
from config import asset_path, asset_uri
from src.utils.message import CustomMessageBox
from src.ui.dialog_title_bar import DialogTitleBar
from src.utils.fungsi import ScreenSize

class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        self.db = DatabaseManager()
        self.id_user = user_data.get('id') if user_data else None
        
        self.nama_input, self.kunci_input, self.role_input = QLineEdit(), QLineEdit(), QComboBox()
        self.otorisasi_input = QLineEdit()
        self.kunci_input.setPlaceholderText("Kosongkan jika tidak diubah" if user_data else "Harus 10 digit angka")
        self.kunci_input.setMaxLength(10)
        self.role_input.addItems(["Admin", "Super_user"])
        self.otorisasi_input.setPlaceholderText("Masukkan kunci Super_user")
        self.otorisasi_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.otorisasi_input.setMaxLength(10)

        input_style = """
            QLineEdit, QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:hover, QComboBox:hover {
                border: 2px solid #00aaff;
                background-color: #252525;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #48c2ff;
                background-color: #2a2a2a;
            }
            QComboBox::drop-down {
                border: none;
                width: 26px;
            }
            QComboBox::down-arrow {
                image: url(%s);
                width: 18px;
                height: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 2px solid #00aaff;
                selection-background-color: #90EE90;
                selection-color: #000000;
                color: #FFFFFF;
                padding: 5px;
            }
        """ % asset_uri("panah atas bawah.png")
        self.nama_input.setStyleSheet(input_style)
        self.kunci_input.setStyleSheet(input_style)
        self.role_input.setStyleSheet(input_style)
        self.otorisasi_input.setStyleSheet(input_style)

        if user_data:
            self.nama_input.setText(user_data.get('nama', ''))
            if (idx := self.role_input.findText(user_data.get('role', 'Admin'))) >= 0: self.role_input.setCurrentIndex(idx)
            
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        root_widget = QWidget()
        root_widget.setObjectName("UserFormRoot")
        main_layout = QVBoxLayout(root_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(DialogTitleBar("Edit User", self))

        content = QWidget()
        content.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 18, 20, 20)
        content_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_icon = QLabel()
        header_icon.setFixedSize(56, 56)
        header_icon.setScaledContents(True)
        header_icon.setPixmap(QPixmap(asset_path("manajemen putih.png")))
        header_title = QLabel("Formulir Edit User")
        header_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; border: none;")
        header_layout.addStretch()
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        content_layout.addSpacing(20)

        def add_field(label_text: str, widget: QWidget):
            row = QVBoxLayout()
            row.setSpacing(5)
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 13px; font-weight: 600; border: none; color: #ffffff;")
            row.addWidget(label)
            row.addWidget(widget)
            content_layout.addLayout(row)

        add_field(" 🔖 Nama User", self.nama_input)
        add_field(" ⚓️ Kunci Akses", self.kunci_input)
        add_field(" 🕹️ Role", self.role_input)
        add_field(" 👁️‍🗨️ Kunci Otorisasi Admin", self.otorisasi_input)

        content_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        submit_btn = QPushButton("SUBMIT")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setFixedSize(130, 44)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aaff;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008ed6;
            }
        """)
        submit_btn.clicked.connect(self.accept)
        button_layout.addWidget(submit_btn)

        cancel_btn = QPushButton("BATAL")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFixedSize(130, 44)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b4b4b;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        content_layout.addLayout(button_layout)

        main_layout.addWidget(content)
        root_layout.addWidget(root_widget)
        self.setFixedSize(500, 620)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(500, 620)
        self.move(x, y)

        root_widget.setStyleSheet("""
            QWidget#UserFormRoot {
                border: 2px solid #00aaff;
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)

    def accept(self):
        otorisasi_key = self.otorisasi_input.text().strip()
        if not otorisasi_key:
            CustomMessageBox.critical(self, "Otorisasi Gagal", "Kunci Otorisasi Admin wajib diisi.")
            return

        is_valid, result = self.db.verify_login(otorisasi_key)
        if not is_valid:
            message = result if isinstance(result, str) else "Terjadi kesalahan saat memverifikasi otorisasi."
            CustomMessageBox.critical(self, "Otorisasi Gagal", message)
            return

        if not isinstance(result, dict) or result.get("role") != "Super_user":
            CustomMessageBox.critical(self, "Otorisasi Gagal", "Hanya Super_user yang dapat mengelola user.")
            return

        super().accept()
        
    def get_data(self):
        return {"id": self.id_user, "nama": self.nama_input.text().strip(), "kunci": self.kunci_input.text().strip(), "role": self.role_input.currentText()}
