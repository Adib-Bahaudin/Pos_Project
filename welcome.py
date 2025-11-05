from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel


class WelcomeWindow(QWidget):
    """Window untuk menampilkan halaman welcome"""

    # Konstanta
    CONTENT_SIZE = 500
    WELCOME_IMAGE_PATH = "data/welcome.png"

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi user interface"""
        root_layout = QHBoxLayout()

        content_frame = QFrame()
        content_frame.setFixedSize(self.CONTENT_SIZE, self.CONTENT_SIZE)
        content_layout = QVBoxLayout(content_frame)

        # Label untuk gambar welcome
        welcome_label = self._create_welcome_label()
        content_layout.addWidget(welcome_label)

        content_frame.setLayout(content_layout)
        root_layout.addWidget(content_frame)
        self.setLayout(root_layout)

    def _create_welcome_label(self) -> QLabel:
        """Membuat label dengan gambar welcome"""
        label = QLabel()
        label.setPixmap(QPixmap(self.WELCOME_IMAGE_PATH))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setScaledContents(True)
        return label