"""
==============================================================================
test_user_admin.py — Test Suite untuk UserAdministrator & Related Classes
==============================================================================

Menguji komponen-komponen di src/ui/user_administrator.py:
  - UserFormDialog
  - PasswordDelegate
  - ActionDelegate
  - UserTable
  - UserAdministrator (widget utama)

Fixtures lokal (`user_admin_module`, `user_admin_widget`) didefinisikan
di sini karena bersifat spesifik untuk modul ini.
==============================================================================
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QEvent, QPointF, QRect, Qt
from PySide6.QtGui import QMouseEvent, QStandardItemModel
from PySide6.QtWidgets import (
    QDialog, QMessageBox, QStyleOptionViewItem, QTableWidget,
)
from PySide6.QtTest import QSignalSpy


# ===========================================================================
# Fixtures lokal — spesifik untuk modul user_administrator
# ===========================================================================

@pytest.fixture
def user_admin_module():
    from src.ui import user_administrator as module
    return module


@pytest.fixture
def user_admin_widget(qtbot, user_admin_module):
    with patch("src.ui.user_administrator.DatabaseManager") as MockDB, \
         patch("src.ui.user_administrator.CustomMessageBox") as MockMsg:
        db = MagicMock()
        db.get_users_for_table.return_value = []
        db.get_users_count.return_value = 0
        MockDB.return_value = db
        widget = user_admin_module.UserAdministrator()
        qtbot.addWidget(widget)
        yield widget, db, MockMsg


# ===========================================================================
# SECTION 15: TEST — UserAdministrator & related classes
# ===========================================================================

class TestSection15UserAdministrator:
    def test_user_form_dialog_tambah_mode_dan_placeholder(self, qtbot, user_admin_module):
        dialog = user_admin_module.UserFormDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Tambah User"
        assert dialog.id_user is None
        assert dialog.kunci_input.placeholderText() == "Harus 10 digit angka"

    def test_user_form_dialog_edit_mode_dan_role(self, qtbot, user_admin_module):
        dialog = user_admin_module.UserFormDialog(user_data={"id": 9, "nama": "Budi", "role": "Super_user"})
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Edit User"
        assert dialog.id_user == 9
        assert dialog.nama_input.text() == "Budi"
        assert dialog.role_input.currentText() == "Super_user"
        assert dialog.kunci_input.placeholderText() == "Kosongkan jika tidak diubah"

    def test_user_form_dialog_get_data_dan_perubahan_role(self, qtbot, user_admin_module):
        dialog = user_admin_module.UserFormDialog(user_data={"id": 2, "nama": "A", "role": "Admin"})
        qtbot.addWidget(dialog)
        dialog.nama_input.setText("  Ujang  ")
        dialog.kunci_input.setText(" 123456 ")
        dialog.role_input.setCurrentText("Super_user")
        data = dialog.get_data()
        assert data == {"id": 2, "nama": "Ujang", "kunci": "123456", "role": "Super_user"}

    def test_password_delegate_masking_normal_empty_dan_max12(self, user_admin_module):
        model = QStandardItemModel(1, 1)
        delegate = user_admin_module.PasswordDelegate()
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 100, 30)

        class _FakeStyle:
            def drawPrimitive(self, *args, **kwargs):
                return None

        with patch("src.ui.user_administrator.QApplication.style", return_value=_FakeStyle()):
            with patch.object(delegate, "initStyleOption", return_value=None):
                painter = MagicMock()

                model.setData(model.index(0, 0), "abcde")
                delegate.paint(painter, option, model.index(0, 0))
                assert painter.drawText.call_args_list[-1].args[-1] == "●●●●●"

                model.setData(model.index(0, 0), "")
                delegate.paint(painter, option, model.index(0, 0))
                assert painter.drawText.call_args_list[-1].args[-1] == ""

                model.setData(model.index(0, 0), "x" * 50)
                delegate.paint(painter, option, model.index(0, 0))
                assert painter.drawText.call_args_list[-1].args[-1] == "●" * 12

    def test_action_delegate_icon_rects(self, qtbot, user_admin_module):
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)
        edit_rect, delete_rect = delegate._icon_rects(QRect(0, 0, 100, 40))
        assert edit_rect.width() == 20
        assert delete_rect.width() == 20
        assert delete_rect.x() > edit_rect.x()

    def test_action_delegate_event_hover_dan_leave(self, qtbot, user_admin_module):
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        idx = table.model().index(0, user_admin_module.COL_AKSI)
        with patch.object(table, "indexAt", return_value=idx), \
             patch.object(table, "visualRect", return_value=QRect(0, 0, 100, 40)), \
             patch("src.ui.user_administrator.QToolTip.showText"), \
             patch("src.ui.user_administrator.QToolTip.hideText"):
            move_edit = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(35, 20),
                QPointF(35, 20),
                QPointF(35, 20),
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.viewport(), move_edit)
            assert delegate._hover_zone == "edit"

            move_delete = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(65, 20),
                QPointF(65, 20),
                QPointF(65, 20),
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.viewport(), move_delete)
            assert delegate._hover_zone == "delete"

            move_out = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(5, 20),
                QPointF(5, 20),
                QPointF(5, 20),
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.viewport(), move_out)
            assert delegate._hover_row == -1
            assert delegate._hover_zone == ""

            delegate._hover_row = 0
            leave_ev = QEvent(QEvent.Type.Leave)
            delegate.eventFilter(table.viewport(), leave_ev)
            assert delegate._hover_row == -1

    def test_action_delegate_click_emit_signal_dan_resolve(self, qtbot, user_admin_module):
        table = user_admin_module.UserTable()
        qtbot.addWidget(table)
        delegate = table._action_delegate

        edit_calls = []
        delete_calls = []
        table.edit_requested.connect(edit_calls.append)
        table.delete_requested.connect(delete_calls.append)

        idx = table.table.model().index(0, user_admin_module.COL_AKSI)
        with patch.object(table.table, "indexAt", return_value=idx), \
             patch.object(table.table, "visualRect", return_value=QRect(0, 0, 100, 40)):
            release_edit = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                QPointF(35, 20),
                QPointF(35, 20),
                QPointF(35, 20),
                user_admin_module.Qt.MouseButton.LeftButton,
                user_admin_module.Qt.MouseButton.LeftButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.table.viewport(), release_edit)

            release_delete = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                QPointF(65, 20),
                QPointF(65, 20),
                QPointF(65, 20),
                user_admin_module.Qt.MouseButton.LeftButton,
                user_admin_module.Qt.MouseButton.LeftButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.table.viewport(), release_delete)

        assert len(edit_calls) == 1
        assert len(delete_calls) == 1
        assert delegate._resolve_user_table() is table

    def test_user_table_inisialisasi_delegate_set_data_dan_row_height(self, qtbot, user_admin_module):
        table = user_admin_module.UserTable()
        qtbot.addWidget(table)
        assert table.table.columnCount() == 5
        assert table.table.itemDelegateForColumn(user_admin_module.COL_PASSWORD) is table._password_delegate
        assert table.table.itemDelegateForColumn(user_admin_module.COL_AKSI) is table._action_delegate

        rows = [{"id": 1, "nama": "Ana", "role": "Admin", "password": "123", "aksi": ""}]
        table.set_data(rows)
        assert table._all_rows == rows
        assert table.table.rowHeight(0) == 45

    def test_on_tambah_user_accepted_dan_rejected(self, user_admin_widget):
        widget, _, MockMsg = user_admin_widget
        with patch("src.ui.user_administrator.RegisterDialog") as MockDialog, \
             patch.object(widget, "table_data") as mock_table_data:
            MockDialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            widget._on_tambah_user()
            mock_table_data.assert_called_once()
            MockMsg.information.assert_called_once()

            mock_table_data.reset_mock()
            MockMsg.information.reset_mock()
            MockDialog.return_value.exec.return_value = QDialog.DialogCode.Rejected
            widget._on_tambah_user()
            mock_table_data.assert_not_called()
            MockMsg.information.assert_not_called()

    def test_on_edit_user_branch_selection(self, user_admin_widget):
        widget, _, MockMsg = user_admin_widget
        widget.table_user._all_rows = [{"id": 1, "nama": "Ana", "role": "Admin", "password": "1111"}]
        with patch.object(widget.table_user.table, "currentRow", return_value=-1):
            widget._on_edit_user()
            MockMsg.critical.assert_called_once()

        with patch.object(widget.table_user.table, "currentRow", return_value=0), \
             patch.object(widget, "_on_edit_user_by_row") as mock_by_row:
            widget._on_edit_user()
            mock_by_row.assert_called_once_with(0)

    def test_on_hapus_user_branch_selection(self, user_admin_widget):
        widget, _, MockMsg = user_admin_widget
        widget.table_user._all_rows = [{"id": 1, "nama": "Ana", "role": "Admin", "password": "1111"}]
        with patch.object(widget.table_user.table, "currentRow", return_value=-1):
            widget._on_hapus_user()
            MockMsg.critical.assert_called_once()

        with patch.object(widget.table_user.table, "currentRow", return_value=0), \
             patch.object(widget, "_on_hapus_user_by_row") as mock_by_row:
            widget._on_hapus_user()
            mock_by_row.assert_called_once_with(0)

    def test_on_edit_user_by_row_sukses_dan_gagal(self, user_admin_widget):
        widget, db, MockMsg = user_admin_widget
        widget.table_user._all_rows = [{"id": 2, "nama": "B", "role": "Admin", "password": "2222"}]

        with patch("src.ui.user_administrator.UserFormDialog") as MockForm, \
             patch.object(widget, "table_data") as mock_table_data:
            MockForm.return_value.exec.return_value = QDialog.DialogCode.Accepted
            MockForm.return_value.get_data.return_value = {"id": 2, "nama": "B2", "kunci": "3333", "role": "Super_user"}
            widget._on_edit_user_by_row(0)
            db.update_user.assert_called_once_with(2, "B2", "3333", "Super_user")
            mock_table_data.assert_called_once()
            MockMsg.information.assert_called_once()

            db.update_user.reset_mock()
            mock_table_data.reset_mock()
            MockMsg.information.reset_mock()
            db.update_user.side_effect = ValueError("gagal")
            widget._on_edit_user_by_row(0)
            MockMsg.critical.assert_called_once()

    def test_on_hapus_user_by_row_cancel_sukses_dan_gagal(self, user_admin_widget):
        widget, db, MockMsg = user_admin_widget
        widget.table_user._all_rows = [{"id": 10, "nama": "C", "role": "Admin", "password": "4444"}]

        with patch("src.ui.user_administrator.DeleteUserConfirmDialog") as MockVerifyDialog, \
             patch.object(widget, "table_data") as mock_table_data:

            widget.table_user._all_rows = [{"id": 99, "nama": "   ", "role": "Admin", "password": "x"}]
            widget._on_hapus_user_by_row(0)

            MockMsg.critical.assert_called_with(
                widget, "Gagal", "Nama user tidak valid untuk proses hapus."
            )
            MockVerifyDialog.assert_not_called()
            MockMsg.question.assert_not_called()
            db.delete_user.assert_not_called()
            mock_table_data.assert_not_called()

            MockMsg.critical.reset_mock()
            MockMsg.question.reset_mock()
            db.delete_user.reset_mock()
            mock_table_data.reset_mock()
            MockVerifyDialog.reset_mock()

            widget.table_user._all_rows = [{"id": 10, "nama": "C", "role": "Admin", "password": "4444"}]

            MockVerifyDialog.return_value.exec.return_value = QDialog.DialogCode.Rejected
            widget._on_hapus_user_by_row(0)
            db.delete_user.assert_not_called()
            MockMsg.question.assert_not_called()

            db.delete_user.reset_mock()
            MockMsg.question.reset_mock()
            mock_table_data.reset_mock()

            MockVerifyDialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            MockMsg.question.return_value = QMessageBox.StandardButton.No
            widget._on_hapus_user_by_row(0)
            db.delete_user.assert_not_called()

            MockMsg.question.return_value = QMessageBox.StandardButton.Yes
            widget._on_hapus_user_by_row(0)
            db.delete_user.assert_called_once_with(10)
            mock_table_data.assert_called_once()
            MockMsg.information.assert_called_once()

            db.delete_user.reset_mock()
            mock_table_data.reset_mock()
            MockMsg.information.reset_mock()
            MockMsg.critical.reset_mock()

            db.delete_user.side_effect = ValueError("hapus gagal")
            widget._on_hapus_user_by_row(0)
            MockMsg.critical.assert_called_once()

    def test_filter_search_pagination_reset_refresh_shortcut_dan_edge(self, user_admin_widget):
        widget, db, _ = user_admin_widget
        widget.USERS_PER_PAGE = 5

        with patch.object(widget, "table_data") as mock_table_data:
            widget._on_filter_changed()
            mock_table_data.assert_called_once()

        db.get_users_for_table.return_value = []
        db.get_users_count.return_value = 0
        widget.table_data(offset=0)
        assert widget.pages == 1
        assert widget.page_input.text() == "1"

        db.get_users_for_table.return_value = [{"id": 1, "nama": "X", "role": "Admin", "password": "1", "aksi": ""}]
        db.get_users_count.return_value = 12
        widget.table_data(offset=5)
        assert widget.pages == 3
        assert widget.page_input.text() == "2"

        with patch.object(widget, "table_data") as mock_table_data:
            widget.pages = 3
            widget.page_input.setText("0")
            widget.custom_page()
            mock_table_data.assert_called_with()

            widget.page_input.setText("5")
            widget.custom_page()
            mock_table_data.assert_called_with(10)

            widget.page_input.setText("2")
            widget.custom_page()
            mock_table_data.assert_called_with(5)

            widget.page_input.setText("1")
            widget.pages = 3
            widget.next_page()
            mock_table_data.assert_called_with(5)

            widget.page_input.setText("2")
            widget.prev_page()
            mock_table_data.assert_called_with(0)

        widget.search_input.setText("keyword")
        widget.filter_role.setCurrentIndex(1)
        widget.on_reset_click()
        assert widget.filter_role.currentIndex() == 0
        assert widget.search_input.text() == ""

        with patch.object(widget, "table_data") as mock_table_data:
            widget.search_input.setText("abc")
            widget.filter_role.setCurrentIndex(1)
            mock_table_data.reset_mock()
            widget.refresh_data()
            assert widget.page_input.text() == "1"
            assert widget.search_input.text() == ""
            assert widget.filter_role.currentIndex() == 0
            assert mock_table_data.call_count == 2

        with patch.object(widget, "handle_shortcut") as mock_shortcut:
            mock_shortcut()
            mock_shortcut.assert_called_once()

        delattr(widget, "search_input")
        db.get_users_count.return_value = 0
        db.get_users_for_table.return_value = []
        widget.table_data()
        assert widget.pages == 1
        widget.table_user._all_rows = []

    def test_is_object_valid_returns_false_on_runtime_error(self, user_admin_module):
        """
        Lines 168-169: _is_object_valid harus mengembalikan False
        ketika isValid() melempar RuntimeError (objek Qt sudah di-destroy).
        """
        with patch("src.ui.user_administrator.isValid", side_effect=RuntimeError("C++ object destroyed")):
            result = user_admin_module.ActionDelegate._is_object_valid(MagicMock())
        assert result is False

    def test_get_table_and_viewport_returns_none_when_viewport_raises(self, qtbot, user_admin_module):
        """
        Lines 177-178: _get_table_and_viewport harus mengembalikan (None, None)
        apabila table.viewport() melempar RuntimeError.
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        with patch("src.ui.user_administrator.isValid", return_value=True), \
             patch.object(table, "viewport", side_effect=RuntimeError("viewport gone")):
            result = delegate._get_table_and_viewport()

        assert result == (None, None)

    def test_get_table_and_viewport_returns_none_when_viewport_invalid(self, qtbot, user_admin_module):
        """
        Line 181: _get_table_and_viewport harus mengembalikan (None, None)
        apabila viewport ada tetapi dianggap tidak valid oleh _is_object_valid.
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        with patch.object(
            user_admin_module.ActionDelegate,
            "_is_object_valid",
            staticmethod(lambda obj: obj is table),
        ):
            result = delegate._get_table_and_viewport()

        assert result == (None, None)

    def test_action_delegate_paint_no_hover(self, qtbot, user_admin_module):
        """
        Lines 200-218: ActionDelegate.paint() dieksekusi tanpa hover aktif
        (kedua ikon seharusnya di-render dengan opacity 0.55).
        Memastikan painter.save/restore terpanggil dan ikon di-paint.
        """
        table = user_admin_module.UserTable()
        qtbot.addWidget(table)
        table.set_data([{"id": 1, "nama": "Tes", "role": "Admin", "password": "pw", "aksi": ""}])

        delegate = table._action_delegate
        idx = table.table.model().index(0, user_admin_module.COL_AKSI)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 120, 45)

        painter = MagicMock()
        delegate._icon_edit = MagicMock()
        delegate._icon_delete = MagicMock()
        with patch("src.ui.user_administrator.QApplication.style") as mock_app_style, \
             patch.object(delegate, "initStyleOption"):
            mock_app_style.return_value.drawPrimitive = MagicMock()
            delegate.paint(painter, option, idx)

        painter.save.assert_called_once()
        painter.restore.assert_called_once()
        opacity_calls = [c.args[0] for c in painter.setOpacity.call_args_list]
        assert opacity_calls == [0.55, 0.55]

    def test_action_delegate_paint_with_hover_edit(self, qtbot, user_admin_module):
        """
        Lines 200-218: Saat hover_row == baris yang di-render dan hover_zone == 'edit',
        ikon edit harus opacity 1.0 dan ikon delete 0.55.
        """
        table = user_admin_module.UserTable()
        qtbot.addWidget(table)
        table.set_data([{"id": 1, "nama": "Tes", "role": "Admin", "password": "pw", "aksi": ""}])

        delegate = table._action_delegate
        delegate._hover_row = 0
        delegate._hover_zone = "edit"

        idx = table.table.model().index(0, user_admin_module.COL_AKSI)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 120, 45)

        painter = MagicMock()
        delegate._icon_edit = MagicMock()
        delegate._icon_delete = MagicMock()
        with patch("src.ui.user_administrator.QApplication.style") as mock_app_style, \
             patch.object(delegate, "initStyleOption"):
            mock_app_style.return_value.drawPrimitive = MagicMock()
            delegate.paint(painter, option, idx)

        opacity_calls = [c.args[0] for c in painter.setOpacity.call_args_list]
        assert opacity_calls[0] == 1.0
        assert opacity_calls[1] == 0.55

    def test_action_delegate_paint_with_hover_delete(self, qtbot, user_admin_module):
        """
        Lines 200-218: Saat hover_zone == 'delete', ikon delete 1.0 dan edit 0.55.
        """
        table = user_admin_module.UserTable()
        qtbot.addWidget(table)
        table.set_data([{"id": 1, "nama": "Tes", "role": "Admin", "password": "pw", "aksi": ""}])

        delegate = table._action_delegate
        delegate._hover_row = 0
        delegate._hover_zone = "delete"

        idx = table.table.model().index(0, user_admin_module.COL_AKSI)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 120, 45)

        painter = MagicMock()
        delegate._icon_edit = MagicMock()
        delegate._icon_delete = MagicMock()
        with patch("src.ui.user_administrator.QApplication.style") as mock_app_style, \
             patch.object(delegate, "initStyleOption"):
            mock_app_style.return_value.drawPrimitive = MagicMock()
            delegate.paint(painter, option, idx)

        opacity_calls = [c.args[0] for c in painter.setOpacity.call_args_list]
        assert opacity_calls[0] == 0.55
        assert opacity_calls[1] == 1.0

    def test_event_filter_delegates_to_super_when_obj_not_viewport(self, qtbot, user_admin_module):
        """
        Line 226: Saat eventFilter dipanggil dengan obj yang bukan viewport,
        method harus memanggil super().eventFilter() (dan tidak crash).
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        other = QTableWidget(1, 1)
        qtbot.addWidget(other)

        event = QEvent(QEvent.Type.MouseMove)
        result = delegate.eventFilter(other, event)
        assert result is False

    def test_event_filter_mousemove_outside_aksi_column_resets_hover(self, qtbot, user_admin_module):
        """
        Lines 260-264: Saat MouseMove di kolom selain COL_AKSI dan hover_row != -1,
        hover_row dan hover_zone harus di-reset ke -1 / ''.
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)
        delegate._hover_row = 0
        delegate._hover_zone = "edit"

        non_aksi_idx = table.model().index(0, user_admin_module.COL_NAMA)

        with patch.object(table, "indexAt", return_value=non_aksi_idx):
            move_ev = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(10, 10), QPointF(10, 10), QPointF(10, 10),
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.viewport(), move_ev)

        assert delegate._hover_row == -1
        assert delegate._hover_zone == ""

    def test_event_filter_mousemove_outside_aksi_column_no_reset_when_hover_already_clear(
        self, qtbot, user_admin_module
    ):
        """
        Lines 260-264 (guard if self._hover_row != -1): Saat hover sudah -1,
        block reset tidak boleh dipanggil (tidak ada update viewport yang tidak perlu).
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)
        delegate._hover_row = -1 

        non_aksi_idx = table.model().index(0, user_admin_module.COL_NAMA)
        with patch.object(table, "indexAt", return_value=non_aksi_idx), \
             patch.object(table.viewport(), "update") as mock_update:
            move_ev = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(10, 10), QPointF(10, 10), QPointF(10, 10),
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.MouseButton.NoButton,
                user_admin_module.Qt.KeyboardModifier.NoModifier,
            )
            delegate.eventFilter(table.viewport(), move_ev)

        mock_update.assert_not_called()

    def test_resolve_user_table_uses_table_when_parent_invalid(self, qtbot, user_admin_module):
        """
        Line 306: Jika parent() tidak valid (None atau rejected oleh _is_object_valid),
        _resolve_user_table harus fallback mencari sinyal dari self._table.
        """
        user_table_widget = user_admin_module.UserTable()
        qtbot.addWidget(user_table_widget)

        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)
        delegate._table = user_table_widget

        with patch.object(delegate, "parent", return_value=None):
            result = delegate._resolve_user_table()

        assert result is user_table_widget

    def test_resolve_user_table_uses_table_when_parent_is_invalid_qt_object(
        self, qtbot, user_admin_module
    ):
        """
        Line 306 (cabang else): Ketika _is_object_valid(self._table) juga False,
        widget di-set None dan loop tidak berjalan → return None (line 311).
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        plain = QTableWidget(1, 1)
        qtbot.addWidget(plain)
        delegate._table = plain

        with patch.object(delegate, "parent", return_value=None), \
             patch.object(
                 user_admin_module.ActionDelegate,
                 "_is_object_valid",
                 staticmethod(lambda obj: False),
             ):
            result = delegate._resolve_user_table()

        assert result is None

    def test_resolve_user_table_returns_none_when_chain_has_no_signals(
        self, qtbot, user_admin_module
    ):
        """
        Line 311: _resolve_user_table mengembalikan None apabila seluruh rantai
        parent sudah habis tanpa menemukan widget yang memiliki edit_requested
        dan delete_requested.
        """
        table = QTableWidget(1, 5)
        qtbot.addWidget(table)
        delegate = user_admin_module.ActionDelegate(table, parent=table)

        plain = QTableWidget(1, 1)
        qtbot.addWidget(plain)
        delegate._table = plain

        with patch.object(delegate, "parent", return_value=None):
            result = delegate._resolve_user_table()

        assert result is None
