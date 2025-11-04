from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel


class ErrorWindow(QWidget):
    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout()
        root_widget = QFrame()

        content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setFixedSize(500,500)

        label = QLabel(content_widget)
        label.setPixmap(QPixmap("data/error 404.png"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setScaledContents(True)

        content_layout.addWidget(label)

        content_widget.setLayout(content_layout)
        root_layout.addWidget(content_widget)
        root_widget.setLayout(root_layout)
        self.setLayout(root_layout)