"""
custom_message_box.py
─────────────────────
A fully-styled, frameless QDialog that acts as a drop-in visual
replacement for QMessageBox.

Supports four message types:
    • information()
    • warning()
    • critical()
    • question()

Each type mirrors the QMessageBox API:
    CustomMessageBox.<type>(parent, title, text) -> QMessageBox.StandardButton
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QIcon, QColor, QPainter, QFont
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)
import sys
import os


from PySide6.QtWidgets import QMessageBox

_BUTTON_MAP: dict[str, QMessageBox.StandardButton] = {
    "OK":     QMessageBox.StandardButton.Ok,
    "Cancel": QMessageBox.StandardButton.Cancel,
    "Yes":    QMessageBox.StandardButton.Yes,
    "No":     QMessageBox.StandardButton.No,
}


class _TitleBar(QWidget):
    """
    A draggable, custom title bar with:
      • SVG logo on the left
      • Title text
      • Close (×) button on the right
    """

    LOGO_PATH = r"data\Black White Geometric Letter B Modern Logo.svg"

    def __init__(self, title: str, parent: QDialog) -> None:
        super().__init__(parent)
        self._parent_dialog = parent
        self._drag_pos: QPoint | None = None

        self.setFixedHeight(44)
        self.setObjectName("TitleBar")
        self.setStyleSheet(
            """
            QWidget#TitleBar {
                background-color: #0d0d0d;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        logo_path = self.LOGO_PATH
        if os.path.isfile(logo_path):
            logo = QSvgWidget(logo_path, self)
            logo.setFixedSize(28, 28)
        else:
            logo = QLabel("B", self)
            logo.setFixedSize(28, 28)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo.setStyleSheet(
                "color: #0d0d0d; background: white; border-radius: 14px;"
                "font-weight: 900; font-size: 15px;"
            )
        layout.addWidget(logo)

        self._title_label = QLabel(title, self)
        self._title_label.setStyleSheet(
            "color: #ffffff; font-size: 13px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(self._title_label)

        layout.addStretch()

        close_btn = QPushButton("✕", self)
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setObjectName("CloseBtn")
        close_btn.setStyleSheet(
            """
            QPushButton#CloseBtn {
                background: transparent;
                color: #aaaaaa;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#CloseBtn:hover {
                background: #e81123;
                color: #ffffff;
            }
            QPushButton#CloseBtn:pressed {
                background: #c50f1f;
            }
            """
        )
        close_btn.clicked.connect(parent.reject)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._parent_dialog.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self._parent_dialog.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)


class CustomMessageBox(QDialog):
    """
    A frameless, draggable, fully-styled message dialog.

    Usage (static helpers mirror QMessageBox):
        result = CustomMessageBox.information(parent, "Title", "Message")
        result = CustomMessageBox.warning(parent, "Title", "Message")
        result = CustomMessageBox.critical(parent, "Title", "Message")
        result = CustomMessageBox.question(parent, "Title", "Message")

    Returns a QMessageBox.StandardButton value.
    """

    Information = "information"
    Warning     = "warning"
    Critical    = "critical"
    Question    = "question"

    _TYPE_CONFIG: dict = {
        "information": (
            QStyle.StandardPixmap.SP_MessageBoxInformation,
            ["OK"],
            "#1a73e8",
        ),
        "warning": (
            QStyle.StandardPixmap.SP_MessageBoxWarning,
            ["OK", "Cancel"],
            "#f9ab00",
        ),
        "critical": (
            QStyle.StandardPixmap.SP_MessageBoxCritical,
            ["OK"],
            "#d93025",
        ),
        "question": (
            QStyle.StandardPixmap.SP_MessageBoxQuestion,
            ["Yes", "No"],
            "#0f9d58",
        ),
    }

    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        message: str,
        msg_type: str = "information",
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(420)

        self._clicked_button: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton

        sp_icon, btn_labels, accent = self._TYPE_CONFIG.get(
            msg_type, self._TYPE_CONFIG["information"]
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("Container")
        container.setStyleSheet(
            f"""
            QWidget#Container {{
                background-color: #000000;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }}
            """
        )
        root_layout.addWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._title_bar = _TitleBar(title, self)
        main_layout.addWidget(self._title_bar)

        stripe = QWidget()
        stripe.setFixedHeight(3)
        stripe.setStyleSheet(f"background: {accent}; border: none;")
        main_layout.addWidget(stripe)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 16)
        content_layout.setSpacing(20)

        icon_label = QLabel()
        icon_label.setFixedSize(52, 52)
        std_icon: QIcon = self.style().standardIcon(sp_icon)
        icon_label.setPixmap(std_icon.pixmap(52, 52))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        content_layout.addWidget(icon_label, 0)

        msg_label = QLabel(message)
        msg_label.setObjectName("MsgLabel")
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        msg_label.setStyleSheet(
            "color: #e0e0e0; font-size: 13px; line-height: 1.5; background: transparent;"
        )
        msg_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        content_layout.addWidget(msg_label, 1)

        main_layout.addWidget(content_widget)

        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #2e2e2e; border: none;")
        main_layout.addWidget(divider)

        btn_widget = QWidget()
        btn_widget.setStyleSheet("background: transparent;")
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(16, 12, 16, 16)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        for label in btn_labels:
            btn = QPushButton(label)
            btn.setFixedHeight(34)
            btn.setMinimumWidth(88)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            is_primary = (label in ("OK", "Yes"))
            if is_primary:
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background: {accent};
                        color: #ffffff;
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 0 18px;
                    }}
                    QPushButton:hover {{
                        background: {self._lighten(accent, 20)};
                    }}
                    QPushButton:pressed {{
                        background: {self._darken(accent, 20)};
                    }}
                    """
                )
            else:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background: #2e2e2e;
                        color: #cccccc;
                        border: 1px solid #444444;
                        border-radius: 6px;
                        font-size: 13px;
                        padding: 0 18px;
                    }
                    QPushButton:hover {
                        background: #3a3a3a;
                        color: #ffffff;
                        border-color: #666666;
                    }
                    QPushButton:pressed {
                        background: #252525;
                    }
                    """
                )

            std_btn = _BUTTON_MAP.get(label, QMessageBox.StandardButton.NoButton)
            # Capture std_btn in closure
            btn.clicked.connect(lambda checked=False, b=std_btn: self._on_button(b))
            btn_layout.addWidget(btn)

        main_layout.addWidget(btn_widget)

    def _on_button(self, std_btn: QMessageBox.StandardButton) -> None:
        self._clicked_button = std_btn
        if std_btn in (QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Yes):
            self.accept()
        else:
            self.reject()

    @staticmethod
    def _lighten(hex_color: str, amount: int) -> str:
        """Return a slightly lighter hex color."""
        c = QColor(hex_color)
        return QColor(
            min(c.red()   + amount, 255),
            min(c.green() + amount, 255),
            min(c.blue()  + amount, 255),
        ).name()

    @staticmethod
    def _darken(hex_color: str, amount: int) -> str:
        """Return a slightly darker hex color."""
        c = QColor(hex_color)
        return QColor(
            max(c.red()   - amount, 0),
            max(c.green() - amount, 0),
            max(c.blue()  - amount, 0),
        ).name()

    def paintEvent(self, event) -> None:
        """Paint a subtle drop-shadow behind the card."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        shadow_color = QColor(0, 0, 0, 80)
        margin = 12
        for i in range(margin, 0, -1):
            alpha = int(80 * (margin - i + 1) / margin)
            shadow_color.setAlpha(alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(
                self.rect().adjusted(i, i, -i, -i), 12, 12
            )
        painter.end()

    def clicked_button(self) -> QMessageBox.StandardButton:
        return self._clicked_button


    @staticmethod
    def information(
        parent: QWidget | None,
        title: str,
        message: str,
    ) -> QMessageBox.StandardButton:
        """Show an information dialog. Returns Ok."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox.Information)
        dlg.exec()
        return dlg.clicked_button()

    @staticmethod
    def warning(
        parent: QWidget | None,
        title: str,
        message: str,
    ) -> QMessageBox.StandardButton:
        """Show a warning dialog. Returns Ok or Cancel."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox.Warning)
        dlg.exec()
        return dlg.clicked_button()

    @staticmethod
    def critical(
        parent: QWidget | None,
        title: str,
        message: str,
    ) -> QMessageBox.StandardButton:
        """Show a critical/error dialog. Returns Ok."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox.Critical)
        dlg.exec()
        return dlg.clicked_button()

    @staticmethod
    def question(
        parent: QWidget | None,
        title: str,
        message: str,
    ) -> QMessageBox.StandardButton:
        """Show a question dialog. Returns Yes or No."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox.Question)
        dlg.exec()
        return dlg.clicked_button()