from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication


class ScreenSize:
    def __init__(self):
        self.screen = QApplication.primaryScreen()
        if self.screen is None:
            raise RuntimeError("No primary screen found")

        self.available_geometry = self.screen.availableGeometry()
        self.screen_width = self.available_geometry.width()
        self.screen_height = self.available_geometry.height()

        self.width_percentage = 0.9
        self.height_percentage = 0.97

        self.app_width = int(self.screen_width * self.width_percentage)
        self.app_height = int(self.screen_height * self.height_percentage)

    def get_app_size(self):
        return QSize(self.app_width, self.app_height)

    def get_app_dimensions(self):
        return self.app_width, self.app_height

    def get_centered_position(self, window_width=None, window_height=None):
        w = window_width if window_width else self.app_width
        h = window_height if window_height else self.app_height
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2
        return x, y

    def get_screen_info(self):
        return {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'app_width': self.app_width,
            'app_height': self.app_height,
            'width_percentage': self.width_percentage * 100,
            'height_percentage': self.height_percentage * 100,
        }
