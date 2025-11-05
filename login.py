from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt, QCursor, QIcon
from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)

from database import DatabaseManager


class LoginPage(QWidget):
    """Halaman login dengan input kunci akses"""

    def __init__(self, on_login_success):
        super().__init__()

        self.is_password_visible = False
        self.on_login_success = on_login_success

        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi tampilan halaman login"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)

        # Frame utama
        main_frame = QFrame()
        main_frame_layout = QHBoxLayout()
        main_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Layout konten utama
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        content_layout.addSpacing(20)
        header_label = self._create_header_label()
        content_layout.addWidget(header_label)
        content_layout.addSpacing(60)

        # Welcome message
        welcome_label = self._create_welcome_label()
        content_layout.addWidget(welcome_label)

        subtitle_label = self._create_subtitle_label()
        content_layout.addWidget(subtitle_label)
        content_layout.addSpacing(15)

        # Login form
        login_widget = self._create_login_form()
        content_layout.addWidget(login_widget)
        content_layout.addSpacing(20)

        # Error info
        self.error_info = self._create_error_label()
        content_layout.addWidget(self.error_info)

        content_layout.addStretch()

        # Footer
        footer_widget = self._create_footer()
        content_layout.addWidget(footer_widget)

        main_frame.setLayout(content_layout)
        main_frame_layout.addWidget(main_frame)
        self.setLayout(main_frame_layout)

    def _create_header_label(self) -> QLabel:
        """Membuat label header"""
        label = QLabel(self)
        label.setText("-- SECURE ACCES!! --")
        label.setFont(QFont("Bookman Old Style", 25, QFont.Weight.Bold))
        label.setStyleSheet("color: #00FF7F")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _create_welcome_label(self) -> QLabel:
        """Membuat label sambutan"""
        label = QLabel(self)
        label.setText("Selamat Datang Kembali!")
        label.setFont(QFont("Corbel", 15, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _create_subtitle_label(self) -> QLabel:
        """Membuat label subtitle"""
        label = QLabel(self)
        label.setText("Ayo mulai hari ini dengan penuh semangat dan produktifitas maksimal!")
        label.setFont(QFont("Corbel", 15, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    @staticmethod
    def _create_error_label() -> QLabel:
        """Membuat label untuk menampilkan error"""
        label = QLabel()
        label.setFont(QFont("Franklin Gothic", 12, QFont.Weight.Bold))
        label.setStyleSheet("color: #fbff00")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _create_login_form(self) -> QWidget:
        """Membuat form login"""
        login_widget = QWidget()
        login_layout = QHBoxLayout()
        login_layout.setContentsMargins(0, 0, 0, 0)

        # Frame login
        frame_login = QFrame()
        frame_login.setStyleSheet("""
            QFrame {
                background-color: #303030;
                border: 2px solid #00ff7f;
                border-radius: 15px;
            }
        """)
        frame_login.setFixedSize(700, 190)

        login_content = QVBoxLayout()
        login_content.setContentsMargins(15, 0, 15, 0)
        login_content.setSpacing(0)

        # Label instruksi
        instruction_label = self._create_instruction_label()
        login_content.addWidget(instruction_label)

        # Input widget
        input_widget = self._create_input_widget()
        login_content.addWidget(input_widget)

        # Tombol login
        self.login_button = self._create_login_button()
        login_content.addWidget(self.login_button)

        # Tombol register
        register_widget = self._create_register_widget()
        login_content.addWidget(register_widget)

        frame_login.setLayout(login_content)
        login_layout.addWidget(frame_login)
        login_widget.setLayout(login_layout)

        return login_widget

    @staticmethod
    def _create_instruction_label() -> QLabel:
        """Membuat label instruksi input"""
        label = QLabel()
        label.setText("Masukkan Kunci Anda :")
        label.setStyleSheet("color: #ffffff; border: None;")
        label.setFont(QFont("Arial", 14))
        label.setFixedHeight(30)
        return label

    def _create_input_widget(self) -> QWidget:
        """Membuat widget input kunci dengan tombol toggle visibility"""
        input_widget = QWidget()
        input_widget.setStyleSheet("""
            border-radius: 8px;
            border: 2px solid #00FF7F;
            background-color: #121212;
        """)
        input_widget.setFixedHeight(54)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 0, 15, 0)
        input_layout.setSpacing(0)

        # Input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ketik Kunci Disini . . .")
        self.text_input.setFont(QFont("Arial", 13))
        self.text_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.text_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text_input.setFixedSize(600, 50)
        self.text_input.setStyleSheet("""
            border: None;
            color: #FFFFFF;
            font-size: 15px;
        """)
        input_layout.addWidget(self.text_input)

        input_layout.addStretch()

        # Toggle visibility button
        self.toggle_visibility_button = QPushButton()
        self.toggle_visibility_button.setIcon(QIcon("data/mata tutup.svg"))
        self.toggle_visibility_button.setIconSize(QSize(20, 20))
        self.toggle_visibility_button.setFixedHeight(50)
        self.toggle_visibility_button.setStyleSheet("border: none; color: #ffffff")
        self.toggle_visibility_button.clicked.connect(self._toggle_password_visibility)

        input_layout.addWidget(self.toggle_visibility_button)

        input_widget.setLayout(input_layout)
        return input_widget

    def _create_login_button(self) -> QPushButton:
        """Membuat tombol login"""
        button = QPushButton("BUKA AKSES")
        button.setFont(QFont("Franklin Gothic", 15, QFont.Weight.Bold))
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setFixedHeight(40)
        button.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background-color: #00ff7f;
            }
            QPushButton:hover {
                background-color: #00ffff;
            }
        """)
        button.clicked.connect(self._handle_login)
        button.setShortcut("Return")
        return button

    @staticmethod
    def _create_register_widget() -> QWidget:
        """Membuat widget dengan tombol register"""
        register_button = QPushButton("KLIK Disini! Untuk Membuat Kunci Akses")
        register_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        register_button.setFont(QFont("Arial", 10))
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff
            }
            QPushButton:hover {
                color: #00ffff;
            }
        """)

        register_widget = QWidget()
        register_widget.setFixedHeight(16)
        register_widget.setStyleSheet("""
            background-color: transparent;
            color: #ffffff 
        """)

        register_layout = QHBoxLayout()
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.addStretch()
        register_layout.addWidget(register_button)
        register_layout.addStretch()

        register_widget.setLayout(register_layout)
        return register_widget

    @staticmethod
    def _create_footer() -> QWidget:
        """Membuat footer dengan informasi copyright"""
        footer_widget = QWidget()
        footer_widget.setFixedHeight(70)
        footer_widget.setStyleSheet("""
            border-top: 2px solid #00ffff;
            background-color: #101010;
            color: #ffffff;
        """)

        content_footer = QVBoxLayout()
        content_footer.setSpacing(0)

        footer_line_1 = QLabel("© Advanced SECURE_ACCESS System by Lucky_Boy")
        footer_line_1.setStyleSheet("border: none; font-size: 8;")
        footer_line_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_footer.addWidget(footer_line_1)

        footer_line_2 = QLabel("LuckyWHITEHAT Copyright - Licenced for Educational (2025)")
        footer_line_2.setStyleSheet("border: none; font-size: 8; color: #b4b4b4;")
        footer_line_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_footer.addWidget(footer_line_2)

        footer_widget.setLayout(content_footer)
        return footer_widget

    def _toggle_password_visibility(self):
        """Toggle visibility password antara tersembunyi dan terlihat"""
        if self.is_password_visible:
            self.text_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_button.setIcon(QIcon("data/mata tutup.svg"))
            self.is_password_visible = False
        else:
            self.text_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_button.setIcon(QIcon("data/mata.svg"))
            self.is_password_visible = True

    def _handle_login(self):
        """Handler untuk proses login"""
        database_manager = DatabaseManager()
        key = self.text_input.text().strip()

        if key.isdigit():
            is_success, result = database_manager.verify_login(key)
            if is_success:
                self.error_info.setText('')
                self.on_login_success(result)
            else:
                self.error_info.setText(result)
        else:
            self.error_info.setText("Kunci Hanya Berupa Angka")