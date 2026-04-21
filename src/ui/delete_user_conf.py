from PySide6.QtGui import Qt, QFont, QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QApplication, QWidget,
)
from config import asset_path

from src.ui.dialog_title_bar import DialogTitleBar
from src.utils.fungsi import ScreenSize
from src.utils.message import CustomMessageBox

class DeleteUserConfirmDialog(QDialog):
    def __init__(self, user_name: str, parent=None):
        super().__init__(parent)
        self.user_name = str(user_name or "").strip()
        self.required_text = f"HAPUS User {self.user_name}"

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        screen_size = ScreenSize()
        x, y = screen_size.get_centered_position(550, 480)
        self.move(x, y)

        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self._on_handle_shortcut)

        root_layout = QVBoxLayout()
        root_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        title_bar = DialogTitleBar("Verifikasi Hapus User", self)
        main_layout.addWidget(title_bar)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 8, 20, 0)
        form_layout.setSpacing(0)

        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_delete = QLabel()
        icon_delete.setFixedSize(80, 80)
        icon_delete.setPixmap(QPixmap(asset_path("icon_delete_big.png")))
        icon_delete.setScaledContents(True)
        icon_delete.setStyleSheet("border:none;")
        header_layout.addWidget(icon_delete, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel(f"Hapus User")
        title.setStyleSheet("""
        color:#ff4d4d;
        font-size:22px;
        font-weight:bold;
        border:none;
        """)
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Tindakan ini tidak dapat dibatalkan")
        subtitle.setStyleSheet("""
        color:#aaaaaa;
        font-size:12px;
        border:none;
        """)
        header_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout.addLayout(header_layout)
        form_layout.addSpacing(30)

        verify_row = QHBoxLayout()
        verify_label = QLabel("Verifikasi: ")
        verify_label.setStyleSheet("color: #ffffff; border: none;")
        verify_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        verify_row.addWidget(verify_label)

        warning_layout = QHBoxLayout()

        icon_warning = QLabel()
        icon_warning.setFixedSize(24, 24)
        icon_warning.setPixmap(QPixmap(asset_path("warning_.svg")))
        icon_warning.setScaledContents(True)
        icon_warning.setStyleSheet("border:none;")
        warning_layout.addWidget(icon_warning)

        warning_text = QLabel(f"   Ketik {self.required_text} untuk mengkonfirmasi")
        warning_text.setStyleSheet("""
            color:#ff4d4d;
            border:none;
        """)
        warning_layout.addWidget(warning_text)

        form_layout.addLayout(warning_layout)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText(f"Ketik {self.required_text}")
        self.confirm_input.setFixedHeight(40)
        self.confirm_input.setStyleSheet(self._input_style())
        verify_row.addWidget(self.confirm_input)

        form_layout.addLayout(verify_row)

        self.label_status = QLabel("")
        self.label_status.setStyleSheet("color: #ff9999; border: none;")
        form_layout.addWidget(self.label_status, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        footer = QHBoxLayout()
        footer.setContentsMargins(20, 0, 20, 20)
        footer.addStretch()

        self.button_batal = self._create_button("Batal", "#6c757d", 100)
        self.button_batal.clicked.connect(self.reject)
        footer.addWidget(self.button_batal)

        self.button_hapus = self._create_button("Hapus", "#ff0000", 130)
        self.button_hapus.clicked.connect(self._validate_and_accept)
        footer.addWidget(self.button_hapus)

        main_layout.addLayout(footer)

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)

        self.setLayout(root_layout)
        self.setMinimumSize(550, 480)
        self.setStyleSheet("""
            border: 2px solid #ff4d4d;
            background-color: #000000;
        """)

    @staticmethod
    def _input_style() -> str:
        return """
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:hover {
                border: 2px solid #ff4d4d;
            }
            QLineEdit:focus {
                border: 2px solid #ff7373;
            }
        """

    @staticmethod
    def _create_button(text: str, color: str, width: int) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(width, 40)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #ffffff;
                color: {color};
            }}
            QPushButton:disabled {{
                background-color: #4b4b4b;
                color: #a0a0a0;
            }}
        """)
        return button

    def _on_handle_shortcut(self):
        focused = QApplication.focusWidget()
        if focused == self.confirm_input:
            self._validate_and_accept()

    def _validate_and_accept(self):
        if self.confirm_input.text().strip() != self.required_text:
            self.label_status.setText(f"Teks harus: {self.required_text}")
            self.confirm_input.setFocus()
            self.confirm_input.selectAll()
            return
        self.accept()
