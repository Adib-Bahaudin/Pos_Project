from PySide6.QtCore import QSize, Qt, QCoreApplication, QEvent, QTimer
from PySide6.QtWidgets import QApplication, QCalendarWidget, QPushButton, QStyledItemDelegate, QStyle, QStyleOptionViewItem, QSpinBox
from PySide6.QtGui import QColor, QIcon, QBrush, QKeyEvent


class ScreenSize:
    """Utility class untuk menghitung ukuran dan posisi aplikasi berdasarkan screen"""

    # Konstanta
    DEFAULT_WIDTH_PERCENTAGE = 0.9
    DEFAULT_HEIGHT_PERCENTAGE = 0.97

    def __init__(self):
        self._initialize_screen_properties()
        self._calculate_app_dimensions()

    def _initialize_screen_properties(self):
        """Inisialisasi properti screen"""
        self.screen = QApplication.primaryScreen()
        if self.screen is None:
            raise RuntimeError("No primary screen found")

        self.available_geometry = self.screen.availableGeometry()
        self.screen_width = self.available_geometry.width()
        self.screen_height = self.available_geometry.height()

        self.width_percentage = self.DEFAULT_WIDTH_PERCENTAGE
        self.height_percentage = self.DEFAULT_HEIGHT_PERCENTAGE

    def _calculate_app_dimensions(self):
        """Menghitung dimensi aplikasi berdasarkan persentase screen"""
        self.app_width = int(self.screen_width * self.width_percentage)
        self.app_height = int(self.screen_height * self.height_percentage)

    def get_app_size(self) -> QSize:
        """
        Mendapatkan ukuran aplikasi sebagai QSize

        Returns:
            QSize: Ukuran aplikasi (width, height)
        """
        return QSize(self.app_width, self.app_height)

    def get_app_dimensions(self) -> tuple[int, int]:
        """
        Mendapatkan dimensi aplikasi sebagai tuple

        Returns:
            tuple: (width, height)
        """
        return self.app_width, self.app_height

    def get_centered_position(
            self,
            window_width: int | None = None,
            window_height: int | None = None
    ) -> tuple[int, int]:
        """
        Menghitung posisi untuk center window di screen

        Args:
            window_width: Lebar window (optional, default: app_width)
            window_height: Tinggi window (optional, default: app_height)

        Returns:
            tuple: (x, y) posisi untuk center window
        """
        width = window_width if window_width else self.app_width
        height = window_height if window_height else self.app_height

        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2

        return x, y

    def get_screen_info(self) -> dict:
        """
        Mendapatkan informasi lengkap tentang screen dan aplikasi

        Returns:
            dict: Dictionary berisi informasi screen dan app
        """
        return {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'app_width': self.app_width,
            'app_height': self.app_height,
            'width_percentage': self.width_percentage * 100,
            'height_percentage': self.height_percentage * 100,
        }

class CustomCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

    def paintCell(self, painter, rect, date):
        if date.month() == self.monthShown():
            super().paintCell(painter, rect, date)
        else:
            painter.save()
            
            painter.setPen(QColor("#555555"))
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))
            
            painter.restore()

class MacroSpinBox(QSpinBox):
    def event(self, e):
        if e.type() == QEvent.Type.KeyPress:
            if e.key() == Qt.Key.Key_Tab:
                print("Tab ditekan di QSpinBox! Memindahkan fokus lalu menjadwalkan macro...")
                
                hasil = super().event(e)
                
                QTimer.singleShot(0, self.jalankan_macro)
                
                return hasil
                
        return super().event(e)

    def jalankan_macro(self):
        target_widget = QApplication.focusWidget()
        
        if target_widget:
            print(f"- Macro berjalan pada elemen: {target_widget.__class__.__name__}")
            
            down_press = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
            down_release = QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
            QCoreApplication.postEvent(target_widget, down_press)
            QCoreApplication.postEvent(target_widget, down_release)

            left_press = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Left, Qt.KeyboardModifier.NoModifier)
            left_release = QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Left, Qt.KeyboardModifier.NoModifier)
            QCoreApplication.postEvent(target_widget, left_press)
            QCoreApplication.postEvent(target_widget, left_release)
            
            print("- Macro selesai dieksekusi!\n")

class NavigationButton(QPushButton):
    """Tombol navigasi dengan efek hover"""

    BUTTON_SIZE = 35

    def __init__(self, icon_normal: str, icon_hover: str):
        super().__init__()

        self.icon_normal = QIcon(icon_normal)
        self.icon_hover = QIcon(icon_hover)

        self._setup_ui()

    def _setup_ui(self):
        """Inisialisasi tampilan tombol"""
        self.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.setStyleSheet("""
            QPushButton{
                background-color: transparent;
                border: none;
            }
        """)
        self.setIconSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(self.icon_normal)

    def enterEvent(self, event):
        """Handler ketika mouse masuk ke area tombol"""
        self.setIcon(self.icon_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handler ketika mouse keluar dari area tombol"""
        self.setIcon(self.icon_normal)
        super().leaveEvent(event)

class CurrencyDelegate(QStyledItemDelegate):
    # 1. Tambahkan parameter horizontal_padding di init
    def __init__(self, horizontal_padding=15, parent=None):
        super().__init__(parent)
        self.horizontal_padding = horizontal_padding

    # 2. Tambahkan sizeHint untuk memanipulasi lebar kolom saat di-ResizeToContents
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        # Tambahkan ruang ekstra ke kiri dan kanan sesuai nilai padding
        size.setWidth(size.width() + (self.horizontal_padding * 2))
        size.setHeight(size.height() + 8) 
        return size

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        
        text = opt.text
        opt.text = "" 
        
        painter.save()
        
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter)

        if text:
            foreground = index.data(Qt.ItemDataRole.ForegroundRole)
            if foreground:
                if isinstance(foreground, QBrush):
                    painter.setPen(foreground.color())
                else:
                    painter.setPen(foreground)
            elif opt.state & QStyle.StateFlag.State_Selected:
                painter.setPen(opt.palette.highlightedText().color())
            else:
                painter.setPen(opt.palette.text().color())

            parts = str(text).split(" ", 1)
            if len(parts) == 2 and "Rp" in parts[0]:
                simbol = parts[0]
                nominal = parts[1]

                # 3. Gunakan self.horizontal_padding sebagai jarak dari tepi kiri
                rect_kiri = opt.rect.adjusted(self.horizontal_padding, 0, 0, 0)
                painter.drawText(rect_kiri, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, simbol)

                # 4. Gunakan -self.horizontal_padding sebagai jarak dari tepi kanan
                rect_kanan = opt.rect.adjusted(0, 0, -self.horizontal_padding, 0)
                painter.drawText(rect_kanan, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, nominal)
            else:
                rect_fallback = opt.rect.adjusted(0, 0, -self.horizontal_padding, 0)
                painter.drawText(rect_fallback, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, text)

        painter.restore()