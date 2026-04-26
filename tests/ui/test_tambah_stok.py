import pytest
from PySide6.QtCore import Qt

from src.ui.tambah_stok import TambahStokDialog

class TestDialogTambahStok:

    def test_dialog_tambah_stok_tampil(self, qtbot):
        """
        Test untuk memastikan dialog Tambah Stok dapat diinisialisasi 
        dan dirender dengan benar.
    
        'qtbot' adalah fixture bawaan dari pytest-qt yang otomatis 
        menangani QApplication dan event loop.
        """

        dialog = TambahStokDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        assert dialog.isVisible() is True
        qtbot.stop()