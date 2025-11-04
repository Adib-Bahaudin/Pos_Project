from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QFrame, QStackedWidget
)

from database import DatabaseManager
from manajemen_produk import ManajemenProduk
from error import ErrorWindow
from welcome import WelcomeWindow

class Dashboard(QWidget):
    """Dashboard utama aplikasi dengan sidebar navigasi"""

    def __init__(self, data):
        super().__init__()
        self.user_role = data.get('role')
        self._init_ui()
        self._setup_connections()
        self._apply_role_permissions()

    def _init_ui(self):
        """Inisialisasi user interface"""
        # Layout utama
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Buat sidebar kiri dan kanan
        self.sidebar_left = self._create_left_sidebar()
        self.sidebar_right = self._create_right_sidebar()
        self.sidebar_right.hide()

        # Stack widget untuk konten utama
        self.main_stack = QStackedWidget()

        if not hasattr(self, 'welcome'):
            self.welcome = WelcomeWindow()
            self.main_stack.addWidget(self.welcome)

        if not hasattr(self, 'error_handling'):
            self.error_handling = ErrorWindow()
            self.main_stack.addWidget(self.error_handling)

        # Tambahkan widget ke layout
        main_layout.addWidget(self.sidebar_left)
        main_layout.addWidget(self.sidebar_right)
        main_layout.addWidget(self.main_stack)

        # Frame root
        root_frame = QFrame()
        root_frame.setLayout(main_layout)
        root_layout.addWidget(root_frame)

        self.setLayout(root_layout)
        self.setStyleSheet("""
            background-color: #000000;
        """)

    def _create_left_sidebar(self):
        """Membuat sidebar kiri dengan icon saja"""
        widget = QWidget()
        widget.setFixedWidth(50)
        widget.setStyleSheet(self._get_sidebar_style())

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Tombol menu
        self.btn_menu_left = self._create_icon_button(
            "data/menu putih.png", size=30
        )
        layout.addWidget(self.btn_menu_left)
        layout.addSpacing(25)

        # Tombol navigasi
        self.btn_transaksi_left = self._create_nav_button(
            "data/Transaksi putih.png",
            "data/Transaksi hijau.png"
        )
        layout.addWidget(self.btn_transaksi_left)

        self.btn_sejarah_left = self._create_nav_button(
            "data/sejarah putih.png",
            "data/sejarah hijau.png"
        )
        layout.addWidget(self.btn_sejarah_left)

        self.btn_manajemen_left = self._create_nav_button(
            "data/manajemen putih.png",
            "data/manajemen hijau.png"
        )
        layout.addWidget(self.btn_manajemen_left)

        self.btn_pelanggan_left = self._create_nav_button(
            "data/pelanggan putih.png",
            "data/pelanggan hijau.png"
        )
        layout.addWidget(self.btn_pelanggan_left)

        self.btn_kas_left = self._create_nav_button(
            "data/kas putih.png",
            "data/kas hijau.png"
        )
        layout.addWidget(self.btn_kas_left)

        self.btn_buku_left = self._create_nav_button(
            "data/buku putih.png",
            "data/buku hijau.png"
        )
        layout.addWidget(self.btn_buku_left)

        layout.addStretch()

        # Tombol logout
        self.btn_logout_left = self._create_nav_button(
            "data/logout putih.png",
            "data/logout hijau.png"
        )
        layout.addWidget(self.btn_logout_left)

        return widget

    def _create_right_sidebar(self):
        """Membuat sidebar kanan dengan icon dan text"""
        widget = QWidget()
        widget.setFixedWidth(250)
        widget.setStyleSheet(self._get_sidebar_style(with_text=True))

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Tombol menu
        self.btn_menu_right = self._create_icon_button(
            "data/menu putih.png", size=30
        )
        layout.addWidget(self.btn_menu_right)
        layout.addSpacing(25)

        # Tombol navigasi dengan text
        self.btn_transaksi_right = self._create_nav_button_with_text(
            "data/Transaksi putih.png",
            "data/Transaksi hijau.png",
            " Input Transaksi"
        )
        layout.addWidget(self.btn_transaksi_right)

        self.btn_sejarah_right = self._create_nav_button_with_text(
            "data/sejarah putih.png",
            "data/sejarah hijau.png",
            " Sejarah Transaksi"
        )
        layout.addWidget(self.btn_sejarah_right)

        self.btn_manajemen_right = self._create_nav_button_with_text(
            "data/manajemen putih.png",
            "data/manajemen hijau.png",
            " Manajemen Produk"
        )
        layout.addWidget(self.btn_manajemen_right)

        self.btn_pelanggan_right = self._create_nav_button_with_text(
            "data/pelanggan putih.png",
            "data/pelanggan hijau.png",
            " Data Customer"
        )
        layout.addWidget(self.btn_pelanggan_right)

        self.btn_kas_right = self._create_nav_button_with_text(
            "data/kas putih.png",
            "data/kas hijau.png",
            " Laporan Kas Flow"
        )
        layout.addWidget(self.btn_kas_right)

        self.btn_buku_right = self._create_nav_button_with_text(
            "data/buku putih.png",
            "data/buku hijau.png",
            " Tutup Buku"
        )
        layout.addWidget(self.btn_buku_right)

        layout.addStretch()

        # Tombol logout
        self.btn_logout_right = self._create_nav_button_with_text(
            "data/logout putih.png",
            "data/logout hijau.png",
            " Log Out"
        )
        layout.addWidget(self.btn_logout_right)

        return widget

    @staticmethod
    def _create_icon_button(icon_path, size=30):
        """Helper untuk membuat tombol dengan icon saja"""
        button = QPushButton()
        button.setFixedSize(size, size)

        icon = QIcon()
        icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        button.setIcon(icon)
        button.setIconSize(QSize(22, 22))

        return button

    @staticmethod
    def create_icon(button, icon_normal, icon_checked):
        icon = QIcon()
        icon.addFile(icon_normal, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addFile(icon_checked, QSize(), QIcon.Mode.Normal, QIcon.State.On)
        button.setIcon(icon)
        button.setIconSize(QSize(22, 22))

        return button

    def _create_nav_button(self, icon_normal, icon_checked):
        """Helper untuk membuat tombol navigasi dengan 2 state icon"""
        button = QPushButton()
        button.setFixedSize(30, 30)

        button = self.create_icon(button, icon_normal, icon_checked)
        button.setCheckable(True)
        button.setAutoExclusive(True)

        return button

    def _create_nav_button_with_text(self, icon_normal, icon_checked, text):
        """Helper untuk membuat tombol navigasi dengan icon dan text"""
        button = QPushButton()
        button.setFixedHeight(30)

        button = self.create_icon(button, icon_normal, icon_checked)
        button.setText(text)
        button.setFont(QFont("Arial", 15))
        button.setCheckable(True)
        button.setAutoExclusive(True)

        return button

    @staticmethod
    def _get_sidebar_style(with_text=False):
        """Mendapatkan stylesheet untuk sidebar"""
        base_style = """
            QWidget {
                background-color: #000000;
                border-right: 2px solid #ffffff;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                background-color: #000000;
            }
            QPushButton:hover {
                background-color: #141414;
            }
            QPushButton:checked {
                background-color: #454545;
            }
        """

        if with_text:
            base_style += """
                QWidget {
                    padding-left: 4px;
                }
                QPushButton {
                    color: #ffffff;
                    text-align: left;
                }
                QPushButton:checked {
                    color: rgb(0, 255, 0);
                    background-color: #000000;
                    font-weight: bold;
                    border: 2px solid #ffffff;
                }
            """

        return base_style

    def _setup_connections(self):
        """Setup semua signal-slot connections"""
        # Toggle sidebar
        self.btn_menu_left.clicked.connect(self._show_right_sidebar)
        self.btn_menu_right.clicked.connect(self._show_left_sidebar)

        # Sinkronisasi tombol kiri-kanan
        self._sync_buttons(self.btn_transaksi_left, self.btn_transaksi_right)
        self._sync_buttons(self.btn_sejarah_left, self.btn_sejarah_right)
        self._sync_buttons(self.btn_manajemen_left, self.btn_manajemen_right)
        self._sync_buttons(self.btn_pelanggan_left, self.btn_pelanggan_right)
        self._sync_buttons(self.btn_kas_left, self.btn_kas_right)
        self._sync_buttons(self.btn_buku_left, self.btn_buku_right)

        # Handler khusus
        self.btn_transaksi_left.toggled.connect(self._on_clicked)
        self.btn_manajemen_left.toggled.connect(self._on_clicked)

        # Logout
        self.btn_logout_left.clicked.connect(self._on_logout)
        self.btn_logout_right.clicked.connect(self._on_logout)

    @staticmethod
    def _sync_buttons(btn_left, btn_right):
        """Sinkronisasi state 2 tombol (kiri-kanan)"""
        btn_left.toggled.connect(btn_right.setChecked)
        btn_right.toggled.connect(btn_left.setChecked)

    def _show_right_sidebar(self):
        """Tampilkan sidebar kanan, sembunyikan kiri"""
        self.sidebar_right.show()
        self.sidebar_left.hide()

    def _show_left_sidebar(self):
        """Tampilkan sidebar kiri, sembunyikan kanan"""
        self.sidebar_left.show()
        self.sidebar_right.hide()

    def _apply_role_permissions(self):
        """Terapkan permission berdasarkan role user"""
        if self.user_role != "Super_user":
            self.btn_kas_left.hide()
            self.btn_kas_right.hide()

    def _on_clicked(self):
        """Handler ketika tombol diklik"""
        self.undowidth()
        if self.btn_manajemen_left.isChecked():
            self.btn_manajemen_right.setMinimumWidth(260)
            if not hasattr(self, 'manajemen_widget'):
                self.manajemen_widget = ManajemenProduk()
                self.main_stack.addWidget(self.manajemen_widget)
            self.main_stack.setCurrentWidget(self.manajemen_widget)
        elif self.btn_transaksi_left.isChecked():
            self.btn_transaksi_right.setMinimumWidth(260)
            self.main_stack.setCurrentWidget(self.error_handling)

    def undowidth(self):
        self.btn_transaksi_right.setMinimumWidth(10)
        self.btn_sejarah_right.setMinimumWidth(10)
        self.btn_manajemen_right.setMinimumWidth(10)
        self.btn_pelanggan_right.setMinimumWidth(10)
        self.btn_kas_right.setMinimumWidth(10)
        self.btn_buku_right.setMinimumWidth(10)

    def _on_logout(self):
        """Handler logout: hapus session dan kembali ke login"""
        db_manager = DatabaseManager()
        db_manager.delete_session()

        parent_window = self.window()
        parent_window.close()

        from main import MainWindow
        main_window = MainWindow()
        main_window.show()

        parent_window.deleteLater()