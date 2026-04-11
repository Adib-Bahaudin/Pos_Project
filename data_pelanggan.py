import math

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QDialog
)

from database import DatabaseManager
from ui_base import BaseTableWidget, BaseDataPage
from tambah_pelanggan import TambahPelangganDialog
from edit_pelanggan import EditPelangganDialog
from message import CustomMessageBox

class PelangganTable(BaseTableWidget):
    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [50, 0, 150, 0, 100]
    HEADERS = ["ID", "NAMA PELANGGAN", "NO HANDPHONE", "ALAMAT", "TRANSAKSI"]
    FIELDS = ["id", "nama", "nomer_hp", "alamat", "total_transaksi"]
    LEFT_ALIGN_FIELDS = ["nama", "alamat"]


class DataPelanggan(BaseDataPage):
    HEADER_TITLE = "DATA PELANGGAN"
    SEARCH_PLACEHOLDER = "Cari Nama atau No. HP ..."

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_connections()

        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.handle_shortcut)

    def _add_custom_widgets(self, layout):
        action_buttons_widget = self._create_action_buttons()
        layout.addWidget(action_buttons_widget)
        layout.addSpacing(20)

    def _create_action_buttons(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        self.button_tambah = self._create_action_button("Tambah Pelanggan", "#00ff00")
        self.button_edit = self._create_action_button("Edit Pelanggan", "#ff8000")
        self.button_hapus = self._create_action_button("Hapus Pelanggan", "#ff0000")

        layout.addWidget(self.button_tambah)
        layout.addWidget(self.button_edit)
        layout.addWidget(self.button_hapus)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_data_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.table_pelanggan = PelangganTable()
        self.stack.addWidget(self.table_pelanggan)
        layout.addWidget(self.stack)

        navigation_widget = self._create_bottom_navigation()
        layout.addWidget(navigation_widget)

        widget.setLayout(layout)
        return widget

    def _setup_connections(self):
        self.button_tambah.clicked.connect(self._show_tambah_dialog)
        self.button_edit.clicked.connect(self._show_edit_dialog)
        self.button_hapus.clicked.connect(self._show_hapus_dialog)

    def on_reset_click(self):
        pass

    def _show_tambah_dialog(self):
        dialog = TambahPelangganDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            database = DatabaseManager()

            response = database.insert_customer(
                nama=data["nama"],
                nomer_hp=data["nomer_hp"],
                alamat=data["alamat"]
            )

            if response.get("success"):
                CustomMessageBox.information(
                    self,
                    "Berhasil",
                    f"Pelanggan '{data['nama']}' berhasil ditambahkan."
                )
                self.table_data()
            else:
                CustomMessageBox.critical(
                    self,
                    "Gagal",
                    f"Gagal menambahkan pelanggan:\n{response.get('message')}"
                )

    def _show_edit_dialog(self):
        table = self.table_pelanggan.table
        current_row = table.currentRow()
        
        if current_row < 0:
            CustomMessageBox.critical(self, "Peringatan", "Pilih data pelanggan yang akan diedit terlebih dahulu!")
            return
            
        data_to_edit = None
        if len(self.table_pelanggan._all_rows) > current_row:
            data_to_edit = self.table_pelanggan._all_rows[current_row]
            
        if not data_to_edit:
            return

        dialog = EditPelangganDialog(data_to_edit, self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            database = DatabaseManager()

            response = database.update_customer(
                id_customer=data["id"],
                nama=data["nama"],
                nomer_hp=data["nomer_hp"],
                alamat=data["alamat"]
            )

            if response.get("success"):
                CustomMessageBox.information(
                    self,
                    "Berhasil",
                    f"Pelanggan '{data['nama']}' berhasil diperbarui."
                )
                self.table_data()
            else:
                CustomMessageBox.critical(
                    self,
                    "Gagal",
                    f"Gagal memperbarui pelanggan:\n{response.get('message')}"
                )

    def _show_hapus_dialog(self):
        # Placeholder
        print("Show Hapus Dialog")


    def table_data(self, offset=0):
        current = bool(self.search_input.property("active"))
        text = self.search_input.text().strip()
        database = DatabaseManager()

        if current == False or (text == "" and current == True):
            if current:
                self.search_input.setProperty("active", not current)
                self.search_input.style().unpolish(self.search_input)
                self.search_input.style().polish(self.search_input)

            data = database.get_customers(limit=10, offset=offset)
            self.table_pelanggan.set_data(data)
        elif text != "" and current == True:
            data = database.search_customers(keyword=text, limit=10, offset=offset)
            self.table_pelanggan.set_data(data)

        if offset == 0:
            self.page_input.setText("1")
        else:
            text_page = int(offset / 10) + 1
            self.page_input.setText(str(text_page))


    def custom_page(self):
        text = self.search_input.text().strip()
        current = bool(self.search_input.property("active"))
        database = DatabaseManager()

        if current == False or (text == "" and current == True):
            self.pages = math.ceil(database.get_customers_count() / 10)
        else:
            self.pages = math.ceil(database.get_customers_count(text) / 10)

        page = int(self.page_input.text().strip())
        if page >= self.pages:
            self.page_input.setText(str(self.pages))
            self.table_data((self.pages - 1) * 10)
        elif page <= 0:
            self.table_data()
        else:
            self.table_data((page - 1) * 10)

    def next_page(self):
        page = int(self.page_input.text().strip())
        database = DatabaseManager()
        text = self.search_input.text().strip()
        current = bool(self.search_input.property("active"))

        if current == False or (text == "" and current == True):
            self.pages = math.ceil(database.get_customers_count() / 10)
        else:
            self.pages = math.ceil(database.get_customers_count(text) / 10)

        if page < self.pages:
            page = page + 1
            self.table_data((page - 1) * 10)

    def prev_page(self):
        page = int(self.page_input.text().strip())
        if page > 1:
            page -= 1
            self.table_data((page - 1) * 10)

    def refresh_data(self):
        self.table_data()
        self.search_input.clear()
        self.page_input.setText("1")
