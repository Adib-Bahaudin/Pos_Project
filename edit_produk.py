import sys

from PySide6.QtGui import Qt, QFont, QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QMainWindow, QPushButton, QApplication, QFrame, \
    QHBoxLayout, QLabel, QComboBox, QLineEdit

from dialog_title_bar import DialogTitleBar

class EditProduk(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root_layout = QVBoxLayout()
        root_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        title_bar = DialogTitleBar("Edit Produk", self)
        main_layout.addWidget(title_bar)

        search_layout = QHBoxLayout()

        frame_search = QFrame()
        frame_search.setFixedSize(900, 95)
        frame_search.setStyleSheet("""
            border : 2px solid #90EE90;
            border-radius : 10px;
        """)

        search_content_layout = QVBoxLayout()

        label_satu = self._create_label_and_icon(
            "data/cari_label.svg",
            "Cari Produk : "
        )
        search_content_layout.addWidget(label_satu)

        search_main_layout = QHBoxLayout()

        combo_box = QComboBox()
        combo_box.setFixedSize(150,45)
        combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
        combo_box.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }
            QComboBox:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data/panah atas bawah.png);
                width: 25px;
                height: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 2px solid #90EE90;
                selection-background-color: #90EE90;
                selection-color: #000000;
                color: #FFFFFF;
                padding: 5px;
            }
        """)
        combo_box.addItems(["Satuan", "Paket"])
        search_main_layout.addWidget(combo_box)

        self.search_line_edit = LineEdit("Cari SKU atau Nama Produk...")
        search_main_layout.addWidget(self.search_line_edit)

        search_btn = self._create_button(
            "CARI",
            100,
            "#00aaff",
            "#ffffff"
        )
        search_main_layout.addWidget(search_btn)

        search_content_layout.addLayout(search_main_layout)
        frame_search.setLayout(search_content_layout)
        search_layout.addWidget(frame_search)

        main_layout.addLayout(search_layout)

        main_layout.addStretch()

        root_widget.setLayout(main_layout)
        root_layout.addWidget(root_widget)
        self.setLayout(root_layout)
        self.setMinimumSize(1000, 500)
        self.setStyleSheet("""
            border : 2px solid #90EE90;
            background-color: #000000;
        """)

    @staticmethod
    def _create_button(text, width, color_1, color_2) -> QPushButton:

        button = QPushButton()
        button.setText(text)
        button.setFixedHeight(45)
        button.setFixedWidth(width)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_1};
                color: {color_2};
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: {color_2};
                color: {color_1};
            }}
        """)

        return button

    @staticmethod
    def _create_label_and_icon(icon_path, text) -> QFrame:

        frame = QFrame()
        frame.setStyleSheet("""
            border: none;
            background-color: transparent;
        """)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setPixmap(QPixmap(icon_path))
        icon_label.setScaledContents(True)
        content_layout.addWidget(icon_label)

        label = QLabel()
        label.setFont(QFont("Segoe UI", 12))
        label.setText(text)
        label.setStyleSheet("""
            color: #ffffff;
        """)
        content_layout.addWidget(label)

        frame.setLayout(content_layout)
        return frame

class LineEdit(QLineEdit):
    def __init__(self, placeholder_text=""):
        super().__init__()

        self.setFixedHeight(45)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px 15px;
                color: #FFFFFF;
                font-size: 14px;
                selection-background-color: #90EE90;
                selection-color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #90EE90;
                background-color: #252525;
            }
            QLineEdit:focus {
                border: 2px solid #7FFF7F;
                background-color: #2a2a2a;
            }
        """)
        self.setPlaceholderText(placeholder_text)

    def data(self):
        return self.text().strip()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        button = QPushButton("EDIT PRODUK")
        button.setFixedSize(200, 200)
        button.clicked.connect(self.show_dialog)
        main_layout.addWidget(button)

        self.setCentralWidget(button)

    def show_dialog(self):
        dialog = EditProduk(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())