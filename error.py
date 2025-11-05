from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel


class ErrorWindow(QWidget):
    """Window untuk menampilkan halaman error 404"""

    # Konstanta
    CONTENT_SIZE = 500
    ERROR_IMAGE_PATH = "data/error 404.png"

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi user interface"""
        root_layout = QHBoxLayout()
        root_widget = QFrame()

        content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setFixedSize(self.CONTENT_SIZE, self.CONTENT_SIZE)

        # Label untuk gambar error
        error_label = self._create_error_label(content_widget)
        content_layout.addWidget(error_label)

        content_widget.setLayout(content_layout)
        root_layout.addWidget(content_widget)
        root_widget.setLayout(root_layout)
        self.setLayout(root_layout)

    def _create_error_label(self, parent: QWidget) -> QLabel:
        """Membuat label dengan gambar error"""
        label = QLabel(parent)
        label.setPixmap(QPixmap(self.ERROR_IMAGE_PATH))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setScaledContents(True)
        return label