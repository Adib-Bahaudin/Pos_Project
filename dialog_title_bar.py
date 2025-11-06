import sys

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QFont, QMouseEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QLabel, QApplication, QPushButton


class DialogTitleBar(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.drag_position = QPoint()

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(8, 0, 8, 0)
        root_frame = QFrame()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        icon = QLabel()
        icon.setFixedSize(20, 20)
        icon.setPixmap(QPixmap("data/Black White Geometric Letter B Modern Logo.svg"))
        icon.setScaledContents(True)
        root_layout.addWidget(icon)

        main_layout.addStretch()

        label = QLabel()
        label.setText(text)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        main_layout.addWidget(label)

        main_layout.addStretch()

        self.tombol_x = QPushButton()
        self.tombol_x.setFixedSize(20, 20)
        self.tombol_x.setText("X")
        self.tombol_x.setFont(QFont("Terminal", 11, QFont.Weight.Bold))
        self.tombol_x.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #ff0000;
                color: #ffffff;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        self.tombol_x.clicked.connect(self.close_dialog)
        main_layout.addWidget(self.tombol_x)

        root_frame.setLayout(main_layout)
        root_layout.addWidget(root_frame)
        self.setLayout(root_layout)
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
            }
        """)

    def close_dialog(self):
        """Menutup dialog parent"""
        if self.parent_dialog:
            self.parent_dialog.close()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press untuk drag"""
        if event.button() == Qt.MouseButton.LeftButton and self.parent_dialog:
            self.drag_position = event.globalPosition().toPoint() - self.parent_dialog.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move untuk drag window"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.parent_dialog:
            self.parent_dialog.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = DialogTitleBar("Contoh")
    window.show()
    sys.exit(app.exec())