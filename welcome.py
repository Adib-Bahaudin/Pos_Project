from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        root_layout = QHBoxLayout()

        content_frame = QFrame()
        content_frame.setFixedSize(500,500)
        content_layout = QVBoxLayout(content_frame)

        label = QLabel()
        label.setPixmap(QPixmap("data/welcome.png"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setScaledContents(True)
        content_layout.addWidget(label)

        content_frame.setLayout(content_layout)
        root_layout.addWidget(content_frame)
        self.setLayout(root_layout)