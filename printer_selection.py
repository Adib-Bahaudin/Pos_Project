from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QComboBox
)
from PySide6.QtPrintSupport import QPrinterInfo
from PySide6.QtGui import QKeySequence, QShortcut

from dialog_title_bar import DialogTitleBar


class PrinterSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setObjectName("printerSelectionDialog")
        self.setMinimumWidth(360)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        
        self.title_bar = DialogTitleBar("Pilih Printer", self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        main_layout.addWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        
        lbl_printer = QLabel("Pilih Printer:")
        lbl_printer.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(lbl_printer)
        
        self.combo_printer = QComboBox()
        self.combo_printer.setStyleSheet("""
            QComboBox {
                background-color: #111827;
                border: 2px solid #263241;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QComboBox:focus {
                border: 2px solid #00ff00;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data/icon_down.svg);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #111827;
                color: white;
                selection-background-color: #0d6efd;
                border: 1px solid #263241;
            }
        """)
        
        default_printer = QPrinterInfo.defaultPrinterName()
        available_printers = QPrinterInfo.availablePrinterNames()
        
        if default_printer:
            self.combo_printer.addItem(default_printer)
            
        for p in available_printers:
            if p != default_printer:
                self.combo_printer.addItem(p)
                
        layout.addWidget(self.combo_printer)
        
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        
        self.cancel_button = QPushButton("Batal")
        self.cancel_button.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 4px;")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Lanjutkan")
        self.apply_button.setStyleSheet("background-color: #0d6efd; color: white; padding: 8px; border-radius: 4px;")
        self.apply_button.clicked.connect(self.accept)
        
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        layout.addLayout(button_row)
        
        self.setStyleSheet("""
            QDialog#printerSelectionDialog {
                background-color: #1e1e1e;
                border: 2px solid #00ff00;
            }
            QWidget#contentWidget {
                background-color: transparent;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Shortcuts
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter.activated.connect(self.apply_button.click)
        
        self.shortcut_numpad_enter = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.shortcut_numpad_enter.activated.connect(self.apply_button.click)
        
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.shortcut_esc.activated.connect(self.cancel_button.click)
        
    def get_selected_printer(self):
        return self.combo_printer.currentText()
