from PySide6.QtGui import Qt, QFont, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QFormLayout
)

from src.database.database import DatabaseManager
from src.ui.dialog_title_bar import DialogTitleBar
from src.utils.fungsi import ScreenSize
from config import asset_path


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(500, 600)
        self.setModal(True)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(500, 600)
        self.move(x, y)

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(2, 2, 2, 2)

        main_frame = QWidget()
        main_frame.setObjectName("MainFrame")
        main_frame.setStyleSheet("""
            QWidget#MainFrame {
                background-color: #000000;
                border: 2px solid #90EE90;
            }
        """)

        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(20)

        title_bar = DialogTitleBar("Register User Baru", self)
        main_layout.addWidget(title_bar)

        self.logo_label = QLabel()
        pixmap = QPixmap(asset_path("logo_register(150px).png"))

        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.logo_label)

        # Formulir Input
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(30, 20, 30, 0)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setSpacing(15)

        input_style = """
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #90EE90;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }
            QComboBox:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data/panah atas bawah.png);
                width: 25px;
                height: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 2px solid #90EE90;
                selection-background-color: #90EE90;
                selection-color: #000000;
                color: #FFFFFF;
                padding: 5px;
            }
        """
        label_style = "color: #FFFFFF; font-size: 14px; font-weight: bold;"

        self.input_nama = QLineEdit()
        self.input_nama.setStyleSheet(input_style)
        lbl_nama = QLabel("Nama:")
        lbl_nama.setStyleSheet(label_style)

        self.input_key = QLineEdit()
        self.input_key.setStyleSheet(input_style)
        self.input_key.setPlaceholderText("Angka 10 Digit")
        lbl_key = QLabel("Key:")
        lbl_key.setStyleSheet(label_style)

        self.input_key_admin = QLineEdit()
        self.input_key_admin.setStyleSheet(input_style)
        self.input_key_admin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_key_admin.setPlaceholderText("Kunci Admin/Super User")
        lbl_key_admin = QLabel("Key Admin:")
        lbl_key_admin.setStyleSheet(label_style)

        self.combo_role = QComboBox()
        self.combo_role.addItems(["Admin", "Super User"])
        self.combo_role.setStyleSheet(input_style)
        lbl_role = QLabel("Role:")
        lbl_role.setStyleSheet(label_style)

        form_layout.addRow(lbl_nama, self.input_nama)
        form_layout.addRow(lbl_key, self.input_key)
        form_layout.addRow(lbl_key_admin, self.input_key_admin)
        form_layout.addRow(lbl_role, self.combo_role)

        main_layout.addWidget(form_widget)
        main_layout.addStretch()

        # Label Peringatan
        self.label_peringatan = QLabel()
        self.label_peringatan.setFont(QFont("Franklin Gothic", 11, QFont.Weight.Bold))
        self.label_peringatan.setStyleSheet("color: #fbff00; border: none;")
        self.label_peringatan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_peringatan.setWordWrap(True)
        main_layout.addWidget(self.label_peringatan)

        main_layout.addStretch()

        # Tombol
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 0, 30, 20)

        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.setFixedHeight(45)
        self.btn_batal.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #FFFFFF;
                border: 2px solid #ff0000;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5500ff;
                border: 2px solid #ff0000;
            }
        """)
        self.btn_batal.clicked.connect(self.reject)

        self.btn_register = QPushButton("Register")
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setFixedHeight(45)
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: #000000;
                border: 2px solid #00ffff;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #aaffff;
            }
        """)
        self.btn_register.clicked.connect(self.validasi_dan_register)

        button_layout.addWidget(self.btn_batal)
        button_layout.addWidget(self.btn_register)

        main_layout.addLayout(button_layout)
        root_layout.addWidget(main_frame)

    def validasi_dan_register(self):
        nama = self.input_nama.text().strip()
        key = self.input_key.text().strip()
        key_admin = self.input_key_admin.text().strip()
        role_text = self.combo_role.currentText()

        # 1. Cek apakah ada yang kosong
        if not nama or not key or not key_admin or not role_text:
            self.label_peringatan.setText("Semua input wajib diisi!")
            return

        # 2. Inisialisasi Database
        db = DatabaseManager()

        # 3. Verifikasi Key Admin
        status, result = db.verify_login(key_admin)
        if not status or not isinstance(result, dict) or result.get("role") != "Super_user":
            self.label_peringatan.setText("Otorisasi Gagal: Key Admin tidak valid atau bukan Super User")
            return

        # 4. Tentukan Role User Baru
        if role_text == "Admin":
            role_to_insert = "Admin"
        elif role_text == "Super User":
            role_to_insert = "Super_user"
        else:
            role_to_insert = ""

        # 5. Daftarkan User
        try:
            db.register_user(nama, key, role_to_insert)
            self.accept()
        except ValueError as e:
            self.label_peringatan.setText(str(e))
        except Exception as e:
            self.label_peringatan.setText(f"Terjadi kesalahan: {str(e)}")
