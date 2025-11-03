from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFrame, QStackedWidget

from database import DatabaseManager

class Dashboard(QWidget):
    def __init__(self, data):
        super().__init__()

        role = data['role']
        print(role)

        frame_root = QFrame()
        layout_root = QVBoxLayout()
        layout_root.setContentsMargins(0,0,0,0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        widget_kiri = QWidget()
        widget_kiri.setFixedWidth(50)
        widget_kiri.setStyleSheet("""
            QWidget {
                background-color: #000000;
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
        """)
        layout_kiri = QVBoxLayout(widget_kiri)
        layout_kiri.setContentsMargins(10,10,10,10)
        layout_kiri.setSpacing(15)

        tombol_menu_kiri = QPushButton(widget_kiri)
        tombol_menu_kiri.setFixedSize(30,30)
        icon_menu_kiri = QIcon()
        icon_menu_kiri.addFile("data/menu putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        tombol_menu_kiri.setIcon(icon_menu_kiri)
        tombol_menu_kiri.setIconSize(QSize(22,22))
        #tombol_menu_kiri.setCheckable(True)
        #tombol_menu_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_menu_kiri)

        layout_kiri.addSpacing(25)

        tombol_transaksi_kiri = QPushButton(widget_kiri)
        tombol_transaksi_kiri.setFixedSize(30, 30)
        icon_transaksi_kiri = QIcon()
        icon_transaksi_kiri.addFile("data/Transaksi putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_transaksi_kiri.addFile("data/Transaksi hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_transaksi_kiri.setIcon(icon_transaksi_kiri)
        tombol_transaksi_kiri.setIconSize(QSize(22, 22))
        tombol_transaksi_kiri.setCheckable(True)
        tombol_transaksi_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_transaksi_kiri)

        tombol_sejarah_kiri = QPushButton(widget_kiri)
        tombol_sejarah_kiri.setFixedSize(30, 30)
        icon_sejarah_kiri = QIcon()
        icon_sejarah_kiri.addFile("data/sejarah putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_sejarah_kiri.addFile("data/sejarah hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_sejarah_kiri.setIcon(icon_sejarah_kiri)
        tombol_sejarah_kiri.setIconSize(QSize(22, 22))
        tombol_sejarah_kiri.setCheckable(True)
        tombol_sejarah_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_sejarah_kiri)

        self.tombol_manajemen_kiri = QPushButton(widget_kiri)
        self.tombol_manajemen_kiri.setFixedSize(30, 30)
        icon_manajemen_kiri = QIcon()
        icon_manajemen_kiri.addFile("data/manajemen putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_manajemen_kiri.addFile("data/manajemen hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.tombol_manajemen_kiri.setIcon(icon_manajemen_kiri)
        self.tombol_manajemen_kiri.setIconSize(QSize(22, 22))
        self.tombol_manajemen_kiri.setCheckable(True)
        self.tombol_manajemen_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(self.tombol_manajemen_kiri)

        tombol_pelanggan_kiri = QPushButton(widget_kiri)
        tombol_pelanggan_kiri.setFixedSize(30, 30)
        icon_pelanggan_kiri = QIcon()
        icon_pelanggan_kiri.addFile("data/pelanggan putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_pelanggan_kiri.addFile("data/pelanggan hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_pelanggan_kiri.setIcon(icon_pelanggan_kiri)
        tombol_pelanggan_kiri.setIconSize(QSize(22, 22))
        tombol_pelanggan_kiri.setCheckable(True)
        tombol_pelanggan_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_pelanggan_kiri)

        tombol_kas_kiri = QPushButton(widget_kiri)
        tombol_kas_kiri.setFixedSize(30, 30)
        icon_kas_kiri = QIcon()
        icon_kas_kiri.addFile("data/kas putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_kas_kiri.addFile("data/kas hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_kas_kiri.setIcon(icon_kas_kiri)
        tombol_kas_kiri.setIconSize(QSize(22, 22))
        tombol_kas_kiri.setCheckable(True)
        tombol_kas_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_kas_kiri)

        tombol_buku_kiri = QPushButton(widget_kiri)
        tombol_buku_kiri.setFixedSize(30, 30)
        icon_buku_kiri = QIcon()
        icon_buku_kiri.addFile("data/buku putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_buku_kiri.addFile("data/buku hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_buku_kiri.setIcon(icon_buku_kiri)
        tombol_buku_kiri.setIconSize(QSize(22, 22))
        tombol_buku_kiri.setCheckable(True)
        tombol_buku_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_buku_kiri)

        layout_kiri.addStretch()

        tombol_logout_kiri = QPushButton(widget_kiri)
        tombol_logout_kiri.setFixedSize(30, 30)
        icon_logout_kiri = QIcon()
        icon_logout_kiri.addFile("data/logout putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_logout_kiri.addFile("data/logout hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_logout_kiri.setIcon(icon_logout_kiri)
        tombol_logout_kiri.setIconSize(QSize(22, 22))
        tombol_logout_kiri.setCheckable(True)
        tombol_logout_kiri.setAutoExclusive(True)

        layout_kiri.addWidget(tombol_logout_kiri)

        #=#=#=#=#=#=#=#=#=#=#=#= Widget Kanan #=#=#=#=#=#=#=#=#=#=#=#=
        widget_kanan = QWidget()
        widget_kanan.setFixedWidth(250)
        widget_kanan.setStyleSheet("""
                    QWidget {
                        background-color: #000000;
                        padding-left: 4px;
                    }
                    QPushButton {
                        border: none;
                        border-radius: 8px;
                        background-color: #000000;
                        color: #ffffff;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #141414;
                    }
                    QPushButton:checked {
                        background-color: #454545;
                        color: rgb(0, 255, 0);
                        text-weight: bold;
                    }
                """)
        widget_kanan.hide()
        layout_kanan = QVBoxLayout(widget_kanan)
        layout_kanan.setContentsMargins(10, 10, 10, 10)
        layout_kanan.setSpacing(15)

        tombol_menu_kanan = QPushButton(widget_kanan)
        tombol_menu_kanan.setFixedSize(30, 30)
        icon_menu_kanan = QIcon()
        icon_menu_kanan.addFile("data/menu putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        tombol_menu_kanan.setIcon(icon_menu_kanan)
        tombol_menu_kanan.setIconSize(QSize(22, 22))
        # tombol_menu_kanan.setCheckable(True)
        # tombol_menu_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_menu_kanan)

        layout_kanan.addSpacing(25)

        tombol_transaksi_kanan = QPushButton(widget_kanan)
        tombol_transaksi_kanan.setFixedHeight(30)
        icon_transaksi_kanan = QIcon()
        icon_transaksi_kanan.addFile("data/Transaksi putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_transaksi_kanan.addFile("data/Transaksi hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_transaksi_kanan.setIcon(icon_transaksi_kanan)
        tombol_transaksi_kanan.setText(" Input Transaksi")
        tombol_transaksi_kanan.setFont(QFont("Arial", 15))
        tombol_transaksi_kanan.setIconSize(QSize(22, 22))
        tombol_transaksi_kanan.setCheckable(True)
        tombol_transaksi_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_transaksi_kanan)

        tombol_sejarah_kanan = QPushButton(widget_kanan)
        tombol_sejarah_kanan.setFixedHeight(30)
        icon_sejarah_kanan = QIcon()
        icon_sejarah_kanan.addFile("data/sejarah putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_sejarah_kanan.addFile("data/sejarah hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_sejarah_kanan.setIcon(icon_sejarah_kanan)
        tombol_sejarah_kanan.setText(" Sejarah Transaksi")
        tombol_sejarah_kanan.setFont(QFont("Arial", 15))
        tombol_sejarah_kanan.setIconSize(QSize(22, 22))
        tombol_sejarah_kanan.setCheckable(True)
        tombol_sejarah_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_sejarah_kanan)

        tombol_manajemen_kanan = QPushButton(widget_kanan)
        tombol_manajemen_kanan.setFixedHeight(30)
        icon_manajemen_kanan = QIcon()
        icon_manajemen_kanan.addFile("data/manajemen putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_manajemen_kanan.addFile("data/manajemen hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_manajemen_kanan.setIcon(icon_manajemen_kanan)
        tombol_manajemen_kanan.setText(" Manajemen Produk")
        tombol_manajemen_kanan.setFont(QFont("Arial", 15))
        tombol_manajemen_kanan.setIconSize(QSize(22, 22))
        tombol_manajemen_kanan.setCheckable(True)
        tombol_manajemen_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_manajemen_kanan)

        tombol_pelanggan_kanan = QPushButton(widget_kanan)
        tombol_pelanggan_kanan.setFixedHeight(30)
        icon_pelanggan_kanan = QIcon()
        icon_pelanggan_kanan.addFile("data/pelanggan putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_pelanggan_kanan.addFile("data/pelanggan hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_pelanggan_kanan.setIcon(icon_pelanggan_kanan)
        tombol_pelanggan_kanan.setText(" Data Customer")
        tombol_pelanggan_kanan.setFont(QFont("Arial", 15))
        tombol_pelanggan_kanan.setIconSize(QSize(22, 22))
        tombol_pelanggan_kanan.setCheckable(True)
        tombol_pelanggan_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_pelanggan_kanan)

        tombol_kas_kanan = QPushButton(widget_kanan)
        tombol_kas_kanan.setFixedHeight(30)
        icon_kas_kanan = QIcon()
        icon_kas_kanan.addFile("data/kas putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_kas_kanan.addFile("data/kas hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_kas_kanan.setIcon(icon_kas_kanan)
        tombol_kas_kanan.setText(" Laporan Kas Flow")
        tombol_kas_kanan.setFont(QFont("Arial", 15))
        tombol_kas_kanan.setIconSize(QSize(22, 22))
        tombol_kas_kanan.setCheckable(True)
        tombol_kas_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_kas_kanan)

        tombol_buku_kanan = QPushButton(widget_kanan)
        tombol_buku_kanan.setFixedHeight(30)
        icon_buku_kanan = QIcon()
        icon_buku_kanan.addFile("data/buku putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_buku_kanan.addFile("data/buku hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_buku_kanan.setIcon(icon_buku_kanan)
        tombol_buku_kanan.setText(" Tutup Buku")
        tombol_buku_kanan.setFont(QFont("Arial", 15))
        tombol_buku_kanan.setIconSize(QSize(22, 22))
        tombol_buku_kanan.setCheckable(True)
        tombol_buku_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_buku_kanan)

        layout_kanan.addStretch()

        tombol_logout_kanan = QPushButton(widget_kanan)
        tombol_logout_kanan.setFixedHeight(30)
        tombol_logout_kanan.setFixedWidth(260)
        icon_logout_kanan = QIcon()
        icon_logout_kanan.addFile("data/logout putih.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon_logout_kanan.addFile("data/logout hijau.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        tombol_logout_kanan.setIcon(icon_logout_kanan)
        tombol_logout_kanan.setText(" Log Out")
        tombol_logout_kanan.setFont(QFont("Arial", 15))
        tombol_logout_kanan.setIconSize(QSize(22, 22))
        tombol_logout_kanan.setCheckable(True)
        tombol_logout_kanan.setAutoExclusive(True)

        layout_kanan.addWidget(tombol_logout_kanan)

        #=#=#=#=#=#=#=#=#=#=#=#= Finishing Layout #=#=#=#=#=#=#=#=#=#=#=#=
        widget_kiri.setLayout(layout_kiri)
        widget_kanan.setLayout(layout_kanan)
        main_layout.addWidget(widget_kiri)
        main_layout.addWidget(widget_kanan)

        #main_layout.addStretch()

        #screen_size = ScreenSize()
        #stack_size = screen_size.get_app_dimensions()

        """
        main_stak = QStackedWidget()
        wraper = QFrame()
        wraper.setStyleSheet("""
            #border-radius: 8px;
        """)
        wraper.setFrameShape(QFrame.Shape.NoFrame)
        wraper_lay = QVBoxLayout(wraper)
        wraper_lay.setContentsMargins(0,0,0,0)
        wraper_lay.addWidget(main_stak)
        wraper.setFixedSize(stack_size[0] - 50, stack_size[1]-50)
        """


        self.main_stak = QStackedWidget()

        from manajemen_produk import ManajemenProduk
        self.manajemen = ManajemenProduk()

        #main_stak.addWidget(manajemen)

        main_layout.addWidget(self.main_stak)

        frame_root.setLayout(main_layout)
        layout_root.addWidget(frame_root)
        self.setLayout(layout_root)
        self.setStyleSheet("""
            background-color: #000000;
            border-right: 2px solid #454545;
        """)

        if role != "Super_user":
            tombol_kas_kiri.hide()
            tombol_kas_kanan.hide()

        #=#=#=#=#=#=#=#=#=#=#=#= klik #=#=#=#=#=#=#=#=#=#=#=#=
        tombol_menu_kiri.clicked.connect(widget_kanan.show)
        tombol_menu_kiri.clicked.connect(widget_kiri.hide)
        tombol_menu_kanan.clicked.connect(widget_kiri.show)
        tombol_menu_kanan.clicked.connect(widget_kanan.hide)
        tombol_transaksi_kiri.toggled.connect(tombol_transaksi_kanan.setChecked)
        tombol_transaksi_kanan.toggled.connect(tombol_transaksi_kiri.setChecked)
        tombol_sejarah_kiri.toggled.connect(tombol_sejarah_kanan.setChecked)
        tombol_sejarah_kanan.toggled.connect(tombol_sejarah_kiri.setChecked)
        self.tombol_manajemen_kiri.toggled.connect(tombol_manajemen_kanan.setChecked)
        self.tombol_manajemen_kiri.toggled.connect(self.onklik)
        tombol_manajemen_kanan.toggled.connect(self.tombol_manajemen_kiri.setChecked)
        tombol_pelanggan_kiri.toggled.connect(tombol_pelanggan_kanan.setChecked)
        tombol_pelanggan_kanan.toggled.connect(tombol_pelanggan_kiri.setChecked)
        tombol_kas_kiri.toggled.connect(tombol_kas_kanan.setChecked)
        tombol_kas_kanan.toggled.connect(tombol_kas_kiri.setChecked)
        tombol_buku_kiri.toggled.connect(tombol_buku_kanan.setChecked)
        tombol_buku_kanan.toggled.connect(tombol_buku_kiri.setChecked)
        tombol_logout_kiri.clicked.connect(self.onlogout)
        tombol_logout_kanan.clicked.connect(self.onlogout)

    def onklik(self):
        if self.tombol_manajemen_kiri.isChecked():
            self.main_stak.addWidget(self.manajemen)
        else:
            pass

    def onlogout(self):
        dell = DatabaseManager()
        dell.delete_session()
        #from PySide6.QtWidgets import QApplication
        #app = QApplication.instance()
        parentwindow = self.window()
        parentwindow.close()
        from main import MainWindow
        mainwindow = MainWindow()
        mainwindow.show()
        parentwindow.deleteLater()