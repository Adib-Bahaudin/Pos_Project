import sys

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap, QFont, Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QApplication, QPushButton,
                               QMainWindow, QVBoxLayout, QFrame, QStackedWidget)

from dashboard import Dashboard
from fungsi import ScreenSize
from login import LoginPage
from database import DatabaseManager

class TitleBar(QWidget):

    def __init__(self, parent:'MainWindow'):
        super().__init__()

        self.drag_position = QPoint()
        self.parent_window: MainWindow = parent
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border-bottom: 2px solid #ffffff;
            }
        """)

        frame_main = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10,0,0,0)
        main_layout.setSpacing(3)

        icon_pojok = QLabel(self)
        icon_pojok.setFixedSize(30,30)
        icon = QPixmap("data/Black White Geometric Letter B Modern Logo.svg")
        icon_pojok.setPixmap(icon)
        icon_pojok.setScaledContents(True)

        main_layout.addWidget(icon_pojok)

        label = QLabel(self)
        label.setStyleSheet("color: #FFFFFF;")
        label.setText("arokah Copy & Printing")
        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(25)
        font.setBold(True)
        font.setItalic(True)
        label.setFont(font)

        main_layout.addWidget(label)

        main_layout.addStretch()

        self.tombol_min = QPushButton(self)
        self.tombol_min.setFixedSize(20,20)
        self.tombol_min.setText("_")
        self.tombol_min.setFont(QFont("Terminal", 12, QFont.Weight.Bold))
        self.tombol_min.setStyleSheet("""
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

        main_layout.addWidget(self.tombol_min)

        self.tombol_min.clicked.connect(self.on_minimize)

        main_layout.addSpacing(10)

        tombol_ex = QPushButton(self)
        tombol_ex.setFixedSize(25, 25)
        tombol_ex.setText("X")
        tombol_ex.setFont(QFont("Terminal", 12, QFont.Weight.Bold))
        tombol_ex.setStyleSheet("""
                    QPushButton {
                        border: none;
                        border-radius: 7px;
                        background-color: #ff0000;
                    }
                    QPushButton:hover {
                        background-color: #5500ff;
                    }
                """)

        main_layout.addWidget(tombol_ex)

        tombol_ex.clicked.connect(self.on_close)

        main_layout.addSpacing(15)

        frame_main.setLayout(main_layout)
        frame_layout.addWidget(frame_main)

        self.setLayout(frame_layout)

    def on_minimize(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def on_close(self):
        if self.parent_window:
            self.parent_window.close_session()
            self.parent_window.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.dashboard_widget = None
        self.login = False
        self.datalogin = {"id":None, "username":None, "role": None}

        self.setWindowTitle("coba")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        screen_size = ScreenSize()
        size = screen_size.get_app_size()
        self.setFixedSize(size)

        x, y = screen_size.get_centered_position()
        self.move(x,y)

        stack_size = screen_size.get_app_dimensions()

        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: green")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        title_bar = TitleBar(self)
        main_layout.addWidget(title_bar)

        self.stack = QStackedWidget()
        main_wrapper = QFrame()
        main_wrapper.setFrameShape(QFrame.Shape.NoFrame)
        main_wrapper_lay = QVBoxLayout(main_wrapper)
        main_wrapper_lay.setContentsMargins(0, 0, 0, 0)
        main_wrapper_lay.addWidget(self.stack)
        main_wrapper.setFixedSize(stack_size[0], stack_size[1]-50)
        
        main_layout.addWidget(main_wrapper)

        login = LoginPage(self.on_login_success)
        self.stack.addWidget(login)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.chek_sessions()

    def chek_sessions(self):
        coki = DatabaseManager()
        login_sesi, hasil = coki.verify_session()

        if login_sesi:
            self.on_login_success(hasil)
        else:
            print(hasil)

    def on_login_success(self, data):
        print(f"main.py: Login Berhasil, Selamat Datang {data['username']}")

        self.login = True
        self.datalogin = {"id": data['user_id'], "username": data['username'], "role": data['role']}

        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

        dashboard = Dashboard(data)
        self.stack.addWidget(dashboard)
        self.stack.setCurrentWidget(dashboard)

    def close_session(self):
        if self.login:
            coki = DatabaseManager()
            userid = self.datalogin['id']
            username = self.datalogin['username']
            role = self.datalogin['role']
            coki.session_login(userid,username,role)
        else:
            print("Belum Login")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())