from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, Qt, QCursor, QIcon
from PySide6.QtWidgets import (QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton)

from database import DatabaseManager

class LoginPage(QWidget):

    def __init__(self, on_login_success):
        super().__init__()

        self.counter = True
        self.on_login_success = on_login_success

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)

        main_frame = QFrame()
        main_frame_layout = QHBoxLayout()
        main_frame_layout.setContentsMargins(0, 0, 0, 0)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)

        content_layout.addSpacing(20)

        label_besar = QLabel(self)
        label_besar.setText("-- SECURE ACCES!! --")
        label_besar.setFont(QFont("Bookman Old Style", 25, QFont.Weight.Bold))
        label_besar.setStyleSheet("color: #00FF7F")
        label_besar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(label_besar)

        content_layout.addSpacing(60)

        label_kecil = QLabel(self)
        label_kecil.setText("Selamat Datang Kembali!")
        label_kecil.setFont(QFont("Corbel", 15, QFont.Weight.Bold))
        label_kecil.setStyleSheet("color: #ffffff")
        label_kecil.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(label_kecil)

        label_kecil_2 = QLabel(self)
        label_kecil_2.setText("Ayo mulai hari ini dengan penuh semangat dan produktifitas maksimal!")
        label_kecil_2.setFont(QFont("Corbel", 15, QFont.Weight.Bold))
        label_kecil_2.setStyleSheet("color: #ffffff")
        label_kecil_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(label_kecil_2)

        content_layout.addSpacing(15)

        login_widget = QWidget()
        login_layout = QHBoxLayout()
        login_layout.setContentsMargins(0,0,0,0)

        frame_login = QFrame()
        frame_login.setStyleSheet("""
            QFrame {
                background-color: #303030;
                border: 2px solid #00ff7f;
                border-radius: 15px;
            }
        """)
        frame_login.setFixedSize(700,190)
        login_content = QVBoxLayout()
        login_content.setContentsMargins(15,0,15,0)
        login_content.setSpacing(0)

        label_login = QLabel()
        label_login.setText("Masukkan Kunci Anda :")
        label_login.setStyleSheet("color: #ffffff; border: None;")
        label_login.setFont(QFont("Arial", 14,))
        label_login.setFixedHeight(30)

        login_content.addWidget(label_login)

        widget_input = QWidget()
        widget_input.setStyleSheet("""
            border-radius: 8px;
            border: 2px solid #00FF7F;
            background-color: #121212;
        """)
        widget_input.setFixedHeight(54)
        layout_input = QHBoxLayout()
        layout_input.setContentsMargins(15,0,15,0)
        layout_input.setSpacing(0)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ketik Kunci Disini . . .")
        self.text_input.setFont(QFont("Arial", 13, ))
        self.text_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.text_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text_input.setFixedSize(600,50)
        self.text_input.setStyleSheet("""
            border: None;
            color: #FFFFFF;
            font-size: 15px;
        """)
        layout_input.addWidget(self.text_input)

        layout_input.addStretch()

        self.togle = QPushButton()
        self.togle.setIcon(QIcon("data/mata tutup.svg"))
        self.togle.setIconSize(QSize(20,20))
        self.togle.setFixedHeight(50)
        self.togle.setStyleSheet("border: none; color: #ffffff")
        self.togle.clicked.connect(self.togle_mata)

        layout_input.addWidget(self.togle)

        widget_input.setLayout(layout_input)
        login_content.addWidget(widget_input)

        self.tombol_login = QPushButton("BUKA AKSES")
        self.tombol_login.setFont(QFont("Franklin Gothic", 15, QFont.Weight.Bold))
        self.tombol_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.tombol_login.setFixedHeight(40)
        self.tombol_login.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background-color: #00ff7f;
            }
            QPushButton:hover {
                background-color: #00ffff;
            }
        """)
        self.tombol_login.clicked.connect(self.login_handle)
        self.tombol_login.setShortcut("Return")

        login_content.addWidget(self.tombol_login)

        tombol_register = QPushButton("KLIK Disini! Untuk Membuat Kunci Akses")
        tombol_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        tombol_register.setFont(QFont("Arial", 10))
        tombol_register.setStyleSheet("""
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
        register_layout.setContentsMargins(0,0,0,0)

        register_layout.addStretch()

        register_layout.addWidget(tombol_register)

        register_layout.addStretch()

        register_widget.setLayout(register_layout)
        login_content.addWidget(register_widget)

        frame_login.setLayout(login_content)
        login_layout.addWidget(frame_login)
        login_widget.setLayout(login_layout)

        content_layout.addWidget(login_widget)

        content_layout.addSpacing(20)

        self.error_info = QLabel()
        self.error_info.setFont(QFont("Franklin Gothic", 12, QFont.Weight.Bold))
        self.error_info.setStyleSheet("color: #fbff00")
        self.error_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(self.error_info)

        content_layout.addStretch()

        footer_widget = QWidget()
        footer_widget.setFixedHeight(70)
        footer_widget.setStyleSheet("""
            border-top: 2px solid #00ffff;
            background-color: #101010;
            color: #ffffff;
        """)

        content_footer = QVBoxLayout()
        content_footer.setSpacing(0)

        footer_1 = QLabel("© Advanced SECURE_ACCESS System by Lucky_Boy")
        footer_1.setStyleSheet("border: none; font-size: 8;")
        footer_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_footer.addWidget(footer_1)

        footer_2 = QLabel("LuckyWHITEHAT Copyright - Licenced for Educational (2025)")
        footer_2.setStyleSheet("border: none; font-size: 8; color: #b4b4b4;")
        footer_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_footer.addWidget(footer_2)

        footer_widget.setLayout(content_footer)
        content_layout.addWidget(footer_widget)

        main_frame.setLayout(content_layout)
        main_frame_layout.addWidget(main_frame)
        self.setLayout(main_frame_layout)

    def togle_mata(self):
        if self.counter:
            self.text_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.togle.setIcon(QIcon("data/mata.svg"))
            self.counter = False
        else:
            self.text_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.togle.setIcon(QIcon("data/mata tutup.svg"))
            self.counter = True

    def login_handle(self):

        auth = DatabaseManager()
        kunci = self.text_input.text().strip()

        if kunci.isdigit():
            success, hasil = auth.verify_login(kunci)
            if success:
                self.error_info.setText('')
                self.on_login_success(hasil)
            else:
                self.error_info.setText(hasil)
        else:
            self.error_info.setText("Kunci Hanya Berupa Angka")