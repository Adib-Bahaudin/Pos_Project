from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication


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
            window_width: int = None,
            window_height: int = None
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