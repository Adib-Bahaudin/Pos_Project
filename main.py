import sys

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap, QFont, Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QApplication, QPushButton,
    QMainWindow, QVBoxLayout, QFrame, QStackedWidget
)

from dashboard import Dashboard
from fungsi import ScreenSize
from login import LoginPage
from database import DatabaseManager


class TitleBar(QWidget):
    """Custom title bar dengan fungsi drag, minimize, dan close"""

    def __init__(self, parent: 'MainWindow'):
        super().__init__()

        self.drag_position = QPoint()
        self.parent_window: MainWindow = parent

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Inisialisasi tampilan title bar"""
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border-bottom: 2px solid #ffffff;
            }
        """)

        # Frame utama
        frame_main = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)

        # Layout horizontal untuk konten title bar
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 0, 0)
        main_layout.setSpacing(3)

        # Icon aplikasi
        icon_label = self._create_icon_label()
        main_layout.addWidget(icon_label)

        # Label judul aplikasi
        title_label = self._create_title_label()
        main_layout.addWidget(title_label)

        main_layout.addStretch()

        # Tombol minimize
        self.tombol_minimize = self._create_minimize_button()
        main_layout.addWidget(self.tombol_minimize)
        main_layout.addSpacing(10)

        # Tombol close
        self.tombol_close = self._create_close_button()
        main_layout.addWidget(self.tombol_close)
        main_layout.addSpacing(15)

        frame_main.setLayout(main_layout)
        frame_layout.addWidget(frame_main)
        self.setLayout(frame_layout)

    def _create_icon_label(self) -> QLabel:
        """Membuat label icon aplikasi"""
        icon_label = QLabel(self)
        icon_label.setFixedSize(30, 30)
        icon = QPixmap("data/Black White Geometric Letter B Modern Logo.svg")
        icon_label.setPixmap(icon)
        icon_label.setScaledContents(True)
        return icon_label

    def _create_title_label(self) -> QLabel:
        """Membuat label judul aplikasi"""
        title_label = QLabel(self)
        title_label.setStyleSheet("color: #FFFFFF;")
        title_label.setText("arokah Copy & Printing")

        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(25)
        font.setBold(True)
        font.setItalic(True)
        title_label.setFont(font)

        return title_label

    def _create_minimize_button(self) -> QPushButton:
        """Membuat tombol minimize"""
        button = QPushButton(self)
        button.setFixedSize(20, 20)
        button.setText("_")
        button.setFont(QFont("Terminal", 12, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 7px;
                background-color: #ffff00;
                padding-bottom: 4px;
            }
            QPushButton:hover {
                background-color: #aaffff;
            }
        """)
        return button

    def _create_close_button(self) -> QPushButton:
        """Membuat tombol close"""
        button = QPushButton(self)
        button.setFixedSize(25, 25)
        button.setText("X")
        button.setFont(QFont("Terminal", 12, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 7px;
                background-color: #ff0000;
            }
            QPushButton:hover {
                background-color: #5500ff;
            }
        """)
        return button

    def _connect_signals(self):
        """Menghubungkan signal ke slot"""
        self.tombol_minimize.clicked.connect(self._on_minimize)
        self.tombol_close.clicked.connect(self._on_close)

    def _on_minimize(self):
        """Handler untuk tombol minimize"""
        if self.parent_window:
            self.parent_window.showMinimized()

    def _on_close(self):
        """Handler untuk tombol close"""
        if self.parent_window:
            self.parent_window.close_session()
            self.parent_window.close()

    def mousePressEvent(self, event):
        """Handler ketika mouse ditekan (untuk drag window)"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handler ketika mouse bergerak (untuk drag window)"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class MainWindow(QMainWindow):
    """Window utama aplikasi"""

    def __init__(self):
        super().__init__()

        self.dashboard_widget = None
        self.login = False
        self.data_login = {"id": None, "username": None, "role": None}

        self._setup_window()
        self._setup_ui()
        self._check_existing_session()

    def _setup_window(self):
        """Konfigurasi window utama"""
        self.setWindowTitle("coba")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        screen_size = ScreenSize()
        size = screen_size.get_app_size()
        self.setFixedSize(size)

        x, y = screen_size.get_centered_position()
        self.move(x, y)

    def _setup_ui(self):
        """Inisialisasi tampilan UI"""
        screen_size = ScreenSize()
        stack_size = screen_size.get_app_dimensions()

        # Widget utama
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: green")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        title_bar = TitleBar(self)
        main_layout.addWidget(title_bar)

        # Stacked widget untuk halaman-halaman
        self.stack = QStackedWidget()

        main_wrapper = QFrame()
        main_wrapper.setFrameShape(QFrame.Shape.NoFrame)
        main_wrapper_layout = QVBoxLayout(main_wrapper)
        main_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        main_wrapper_layout.addWidget(self.stack)
        main_wrapper.setFixedSize(stack_size[0], stack_size[1] - 50)

        main_layout.addWidget(main_wrapper)

        # Halaman login
        login_page = LoginPage(self.on_login_success)
        self.stack.addWidget(login_page)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _check_existing_session(self):
        """Mengecek apakah ada session login yang masih aktif"""
        database_manager = DatabaseManager()
        is_logged_in, session_data = database_manager.verify_session()

        if is_logged_in:
            self.on_login_success(session_data)
        else:
            if session_data == "token tidak sudah expaired":
                pesan = LoginPage()
                pesan.session_info(session_data)
            elif session_data == "token tidak valid":
                pesan = LoginPage()
                pesan.session_info(session_data)

    def on_login_success(self, data):
        """Handler ketika login berhasil"""

        self.login = True
        self.data_login = {
            "id": data['user_id'],
            "username": data['username'],
            "role": data['role']
        }

        # Hapus semua widget dari stack
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

        # Tambahkan dashboard
        dashboard = Dashboard(data)
        self.stack.addWidget(dashboard)
        self.stack.setCurrentWidget(dashboard)

    def close_session(self):
        """Menutup session login saat aplikasi ditutup"""
        if self.login:
            database_manager = DatabaseManager()
            user_id = self.data_login['id']
            username = self.data_login['username']
            role = self.data_login['role']
            database_manager.session_login(user_id, username, role)
        else:
            pass


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())