"""
user_administrator.py — Frontend UI untuk halaman User Management.

Halaman ini menampilkan daftar user dalam tabel dengan fitur:
- Filter berdasarkan role (Super_user, Kasir, dll.)
- Tombol aksi global: Tambah, Edit, Hapus User
- Kolom password di-mask dengan karakter bulat (••••••••)
- Kolom aksi berisi tombol Edit & Hapus per-baris

CATATAN UNTUK DEVELOPER:
    Semua method yang diawali komentar `# >>> BACKEND:` adalah
    placeholder yang harus dihubungkan ke logika database.
"""

from PySide6.QtCore import (
    Qt, QRect, QSize, QPoint, QModelIndex, QPersistentModelIndex, QEvent
)
from PySide6.QtGui import (
    QFont, QShortcut, QKeySequence, QIcon, QPainter, QPen,
    QColor, QCursor, QPixmap, QMouseEvent
)
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox,
    QStackedWidget, QStyledItemDelegate, QStyle,
    QStyleOptionViewItem, QApplication, QToolTip
)

from config import asset_path, asset_uri
from src.ui.ui_base import BaseTableWidget, BaseDataPage

_PASSWORD_CHAR = "●"
_ACTION_ICON_SIZE = 20 
_ACTION_BUTTON_GAP = 12
_ACTION_BUTTON_PADDING = 14

COL_ID = 0
COL_NAMA = 1
COL_ROLE = 2
COL_PASSWORD = 3
COL_AKSI = 4

class PasswordDelegate(QStyledItemDelegate):
    """
    Menampilkan teks pada kolom password sebagai karakter bulat (●●●●●●●●).
    Teks asli tetap tersimpan di model, hanya rendering yang di-mask.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mask_font = QFont("Segoe UI", 12)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex):
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        raw_text = index.data(Qt.ItemDataRole.DisplayRole)
        if raw_text:
            masked = _PASSWORD_CHAR * min(len(str(raw_text)), 12)
        else:
            masked = ""

        painter.save()
        painter.setFont(self._mask_font)
        painter.setPen(QPen(QColor("#ffffff")))

        text_rect = option.rect.adjusted(12, 0, -8, 0)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            masked,
        )
        painter.restore()


class ActionDelegate(QStyledItemDelegate):
    """
    Render dua ikon (Edit & Hapus) secara berdampingan di dalam cell kolom AKSI.

    Fitur UX:
    - Hover effect: ikon memudar (opacity) saat cursor di atas area tombol.
    - Cursor berubah menjadi PointingHandCursor saat di area ikon.
    - Tooltip "Edit User" / "Hapus User".
    """

    def __init__(self, table_widget, parent=None):
        super().__init__(parent)
        self._table = table_widget

        self._icon_edit = QIcon(asset_path("edit produk.svg"))
        self._icon_delete = QIcon(asset_path("tong_sampah_putih.svg"))

        self._hover_row = -1
        self._hover_zone = ""

        self._table.viewport().installEventFilter(self)
        self._table.viewport().setMouseTracking(True)

    def _icon_rects(self, cell_rect: QRect):
        """Kembalikan tuple (edit_rect, delete_rect) relatif terhadap cell."""
        y_center = cell_rect.center().y() - _ACTION_ICON_SIZE // 2
        total_width = _ACTION_ICON_SIZE * 2 + _ACTION_BUTTON_GAP
        x_start = cell_rect.center().x() - total_width // 2

        edit_rect = QRect(x_start, y_center, _ACTION_ICON_SIZE, _ACTION_ICON_SIZE)
        delete_rect = QRect(
            x_start + _ACTION_ICON_SIZE + _ACTION_BUTTON_GAP,
            y_center,
            _ACTION_ICON_SIZE,
            _ACTION_ICON_SIZE,
        )
        return edit_rect, delete_rect

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex):
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        edit_rect, delete_rect = self._icon_rects(option.rect)

        painter.save()

        is_hover_row = (index.row() == self._hover_row)

        edit_opacity = 1.0 if (is_hover_row and self._hover_zone == "edit") else 0.55
        painter.setOpacity(edit_opacity)
        self._icon_edit.paint(painter, edit_rect)

        delete_opacity = 1.0 if (is_hover_row and self._hover_zone == "delete") else 0.55
        painter.setOpacity(delete_opacity)
        self._icon_delete.paint(painter, delete_rect)

        painter.restore()

    def eventFilter(self, obj, event: QEvent):
        if obj is not self._table.viewport():
            return super().eventFilter(obj, event)

        event_type = event.type()

        if event_type == QEvent.Type.MouseMove:
            mouse_event: QMouseEvent = event  # type: ignore[assignment]
            pos = mouse_event.position().toPoint()
            index = self._table.indexAt(pos)

            if index.isValid() and index.column() == COL_AKSI:
                cell_rect = self._table.visualRect(index)
                edit_rect, delete_rect = self._icon_rects(cell_rect)

                old_row, old_zone = self._hover_row, self._hover_zone

                if edit_rect.contains(pos):
                    self._hover_row = index.row()
                    self._hover_zone = "edit"
                    self._table.viewport().setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    QToolTip.showText(self._table.viewport().mapToGlobal(pos), "Edit User")
                elif delete_rect.contains(pos):
                    self._hover_row = index.row()
                    self._hover_zone = "delete"
                    self._table.viewport().setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    QToolTip.showText(self._table.viewport().mapToGlobal(pos), "Hapus User")
                else:
                    self._hover_row = -1
                    self._hover_zone = ""
                    self._table.viewport().unsetCursor()
                    QToolTip.hideText()

                if (old_row, old_zone) != (self._hover_row, self._hover_zone):
                    self._table.viewport().update()
            else:
                if self._hover_row != -1:
                    self._hover_row = -1
                    self._hover_zone = ""
                    self._table.viewport().unsetCursor()
                    self._table.viewport().update()

        elif event_type == QEvent.Type.MouseButtonRelease:
            mouse_event_rel: QMouseEvent = event  # type: ignore[assignment]
            pos = mouse_event_rel.position().toPoint()
            index = self._table.indexAt(pos)

            if index.isValid() and index.column() == COL_AKSI:
                cell_rect = self._table.visualRect(index)
                edit_rect, delete_rect = self._icon_rects(cell_rect)

                if edit_rect.contains(pos):
                    self._on_edit_clicked(index.row())
                elif delete_rect.contains(pos):
                    self._on_delete_clicked(index.row())

        elif event_type == QEvent.Type.Leave:
            if self._hover_row != -1:
                self._hover_row = -1
                self._hover_zone = ""
                self._table.viewport().update()

        return super().eventFilter(obj, event)

    def _on_edit_clicked(self, row: int):
        """
        Dipanggil saat ikon Edit pada baris tertentu diklik.

        # >>> BACKEND: Hubungkan ke dialog edit user.
        #     Contoh:
        #         user_data = self._table.parent()._all_rows[row]
        #         dialog = EditUserDialog(user_data, self._table)
        #         dialog.exec()
        """
        print(f"[ActionDelegate] Edit clicked — row {row}")

    def _on_delete_clicked(self, row: int):
        """
        Dipanggil saat ikon Hapus pada baris tertentu diklik.

        # >>> BACKEND: Hubungkan ke konfirmasi & logika hapus user.
        #     Contoh:
        #         user_data = self._table.parent()._all_rows[row]
        #         confirm = CustomMessageBox.question(...)
        #         if confirm: database.delete_user(user_data['id'])
        """
        print(f"[ActionDelegate] Delete clicked — row {row}")


class UserTable(BaseTableWidget):
    """
    Tabel daftar user dengan kolom: ID, NAMA, ROLE, KUNCI/PASSWORD, AKSI.
    Menggunakan delegate khusus pada kolom PASSWORD dan AKSI.
    """

    TABLE_WIDTH = 800
    TABLE_ROW_COUNT = 5
    COLUMN_WIDTHS = [60, 0, 120, 0, 120]
    HEADERS = ["ID", "NAMA", "ROLE", "KUNCI/PASSWORD", "AKSI"]
    FIELDS = ["id", "nama", "role", "password", "aksi"]
    LEFT_ALIGN_FIELDS = ["nama"]

    def __init__(self):
        super().__init__()
        self._apply_styling()
        self._apply_delegates()

    def _apply_styling(self):
        """Override default styling tabel agar sesuai dark theme."""
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                alternate-background-color: #232323;
                gridline-color: #333333;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 6px;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0d47a1;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px 5px;
                border: none;
                border-bottom: 2px solid #00aaff;
                font-family: "Segoe UI";
                font-weight: bold;
                font-size: 13px;
            }
            QTableCornerButton::section {
                background-color: #2a2a2a;
                border: none;
            }
            /* Scrollbar */
            QScrollBar:vertical {
                background: #1a1a1a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777777;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        for row in range(self.TABLE_ROW_COUNT):
            self.table.setRowHeight(row, 45)

    def _apply_delegates(self):
        """Pasang delegate khusus pada kolom Password dan Aksi."""
        self._password_delegate = PasswordDelegate(self.table)
        self.table.setItemDelegateForColumn(COL_PASSWORD, self._password_delegate)

        self._action_delegate = ActionDelegate(self.table, parent=self.table)
        self.table.setItemDelegateForColumn(COL_AKSI, self._action_delegate)

    def set_data(self, rows: list[dict]):
        """Override: atur data dan pastikan row height konsisten."""
        super().set_data(rows)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 45)


class UserAdministrator(BaseDataPage):
    """
    Halaman utama User Management.
    Menampilkan filter role, tombol aksi, search bar, dan tabel user.
    """

    HEADER_TITLE = "USER MANAGEMENT"
    SEARCH_PLACEHOLDER = "Cari Nama atau ID User ..."

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_connections()

        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(self.handle_shortcut)

    def _add_custom_widgets(self, layout):
        """Tambahkan filter role dan tombol aksi di atas search bar."""
        controls_widget = self._create_controls_bar()
        layout.addWidget(controls_widget)
        layout.addSpacing(10)

    def _create_controls_bar(self) -> QWidget:
        """
        Susun Tombol Aksi secara horizontal.
        Layout: spacer -- [Tambah] [Edit] [Hapus]
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        self.button_tambah = self._create_action_button("Tambah User", "#00ff00")
        self.button_edit = self._create_action_button("Edit User", "#ff8000")
        self.button_hapus = self._create_action_button("Hapus User", "#ff0000")

        layout.addWidget(self.button_tambah)
        layout.addWidget(self.button_edit)
        layout.addWidget(self.button_hapus)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_data_widget(self) -> QWidget:
        """Buat widget berisi filter, tabel user, dan navigasi halaman."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 10)
        
        filter_layout.addStretch()
        
        filter_container = QWidget()
        filter_container.setFixedWidth(800)
        fc_layout = QHBoxLayout(filter_container)
        fc_layout.setContentsMargins(0, 0, 0, 0)

        self.filter_role = QComboBox()
        self.filter_role.addItems(["Semua", "Super_user", "Kasir"])
        self.filter_role.setFont(QFont("Segoe UI", 14))
        self.filter_role.setFixedSize(180, 35)
        self.filter_role.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_role.setStyleSheet(f"""
            QComboBox {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 10px;
                padding-left: 12px;
                font-family: "Segoe UI";
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: #00aaff;
            }}
            QComboBox:focus {{
                border-color: #00aaff;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #444444;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
            QComboBox::down-arrow {{
                image: url({asset_uri("icon_down.svg")});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1a1a1a;
                color: #ffffff;
                selection-background-color: #0d47a1;
                selection-color: #ffffff;
                border: 1px solid #444444;
                outline: none;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding-left: 10px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #333333;
            }}
        """)
        fc_layout.addWidget(self.filter_role)
        fc_layout.addStretch()
        
        filter_layout.addWidget(filter_container)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)

        self.stack = QStackedWidget()
        self.table_user = UserTable()
        self.table_user.table.setSelectionBehavior(
            self.table_user.table.SelectionBehavior.SelectRows
        )
        self.table_user.table.setSelectionMode(
            self.table_user.table.SelectionMode.SingleSelection
        )
        self.stack.addWidget(self.table_user)
        layout.addWidget(self.stack)

        navigation_widget = self._create_bottom_navigation()
        layout.addWidget(navigation_widget)

        widget.setLayout(layout)
        return widget

    def _setup_connections(self):
        """Hubungkan sinyal tombol ke handler."""
        self.button_tambah.clicked.connect(self._on_tambah_user)
        self.button_edit.clicked.connect(self._on_edit_user)
        self.button_hapus.clicked.connect(self._on_hapus_user)
        self.filter_role.currentIndexChanged.connect(self._on_filter_changed)

    # == PLACEHOLDER METHODS =================================================
    # Semua method di bawah ini adalah placeholder frontend.
    # Hubungkan ke backend/database manager sesungguhnya saat integrasi.
    # ========================================================================

    def _on_tambah_user(self):
        """
        Handler tombol Tambah User.

        # >>> BACKEND: Tampilkan dialog tambah user, lalu panggil
        #     database.insert_user(...) jika dialog diterima.
        """
        print("[UserAdministrator] Tambah User clicked")

    def _on_edit_user(self):
        """
        Handler tombol Edit User (dari toolbar atas).

        # >>> BACKEND: Ambil baris terpilih dari tabel, tampilkan dialog
        #     edit, lalu panggil database.update_user(...).
        """
        table = self.table_user.table
        current_row = table.currentRow()

        if current_row < 0:
            # >>> BACKEND: Ganti print dengan CustomMessageBox.critical(...)
            print("[UserAdministrator] Pilih user terlebih dahulu!")
            return

        print(f"[UserAdministrator] Edit User clicked — row {current_row}")

    def _on_hapus_user(self):
        """
        Handler tombol Hapus User (dari toolbar atas).

        # >>> BACKEND: Ambil baris terpilih, konfirmasi, lalu panggil
        #     database.delete_user(user_id).
        """
        table = self.table_user.table
        current_row = table.currentRow()

        if current_row < 0:
            # >>> BACKEND: Ganti print dengan CustomMessageBox.critical(...)
            print("[UserAdministrator] Pilih user terlebih dahulu!")
            return

        print(f"[UserAdministrator] Hapus User clicked — row {current_row}")

    def _on_filter_changed(self, index: int):
        """
        Handler saat filter role berubah.

        # >>> BACKEND: Panggil table_data() ulang dengan filter role.
        """
        role = self.filter_role.currentText()
        print(f"[UserAdministrator] Filter role changed: {role}")
        self.table_data()

    # -- Data Loading (Placeholder) ------------------------------------------
    def table_data(self, offset=0):
        """
        Muat data user ke tabel.

        # >>> BACKEND: Ganti dummy_data dengan query dari database.
        #     Contoh:
        #         database = DatabaseManager()
        #         role_filter = self.filter_role.currentText()
        #         search_text = self.search_input.text().strip()
        #         if role_filter == "Semua":
        #             data = database.get_users(limit=5, offset=offset)
        #         else:
        #             data = database.get_users_by_role(role_filter, limit=5, offset=offset)
        #         self.table_user.set_data(data)
        """
        # --- Dummy Data (hapus saat integrasi backend) ---
        dummy_data = [
            {"id": "U001", "nama": "Admin Utama",   "role": "Super_user", "password": "hashed_pw_1", "aksi": ""},
            {"id": "U002", "nama": "Siti Rahayu",    "role": "Kasir",      "password": "hashed_pw_2", "aksi": ""},
            {"id": "U003", "nama": "Budi Santoso",   "role": "Kasir",      "password": "hashed_pw_3", "aksi": ""},
            {"id": "U004", "nama": "Ahmad Yani",     "role": "Super_user", "password": "hashed_pw_4", "aksi": ""},
            {"id": "U005", "nama": "Dewi Lestari",   "role": "Kasir",      "password": "hashed_pw_5", "aksi": ""},
        ]

        role_filter = self.filter_role.currentText()
        if role_filter != "Semua":
            dummy_data = [d for d in dummy_data if d["role"] == role_filter]

        search_text = self.search_input.text().strip().lower()
        if search_text:
            dummy_data = [
                d for d in dummy_data
                if search_text in d["nama"].lower() or search_text in d["id"].lower()
            ]

        self.table_user.set_data(dummy_data)

        if offset == 0:
            self.page_input.setText("1")
        else:
            text_page = int(offset / 5) + 1
            self.page_input.setText(str(text_page))

    def custom_page(self):
        """
        Navigasi ke halaman tertentu berdasarkan input.

        # >>> BACKEND: Hitung total halaman dari database.
        #     self.pages = math.ceil(database.get_users_count() / 5)
        """
        page = int(self.page_input.text().strip() or "1")
        self.pages = 1  # Placeholder
        if page >= self.pages:
            self.page_input.setText(str(self.pages))
            self.table_data((self.pages - 1) * 5)
        elif page <= 0:
            self.table_data()
        else:
            self.table_data((page - 1) * 5)

    def next_page(self):
        """
        Navigasi ke halaman berikutnya.

        # >>> BACKEND: Hitung total halaman dari database.
        """
        page = int(self.page_input.text().strip() or "1")
        self.pages = 1  # Placeholder
        if page < self.pages:
            page += 1
            self.table_data((page - 1) * 5)

    def prev_page(self):
        """Navigasi ke halaman sebelumnya."""
        page = int(self.page_input.text().strip() or "1")
        if page > 1:
            page -= 1
            self.table_data((page - 1) * 5)

    def on_reset_click(self):
        """Reset filter dan pencarian."""
        self.filter_role.setCurrentIndex(0)

    def refresh_data(self):
        """Refresh seluruh halaman (dipanggil dari dashboard saat navigasi)."""
        self.table_data()
        self.search_input.clear()
        self.filter_role.setCurrentIndex(0)
        self.page_input.setText("1")
