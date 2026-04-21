"""
==============================================================================
test_register.py — Test Suite untuk RegisterDialog
==============================================================================

Menguji komponen RegisterDialog (src/ui/register.py).
Fixture `register_dialog` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit


# ===========================================================================
# SECTION 3: TEST — RegisterDialog
# ===========================================================================

class TestRegisterDialog:
    """Kumpulan tes untuk komponen RegisterDialog (src/ui/register.py)."""

    def test_dialog_terbuat_dengan_semua_field(self, register_dialog):
        """
        Memastikan RegisterDialog berhasil diinstansiasi dan memiliki
        semua field input yang diperlukan: input_nama, input_key,
        input_key_admin, combo_role.
        """
        dialog, _ = register_dialog
        assert hasattr(dialog, "input_nama")
        assert hasattr(dialog, "input_key")
        assert hasattr(dialog, "input_key_admin")
        assert hasattr(dialog, "combo_role")

    def test_input_key_admin_mode_password(self, register_dialog):
        """
        Memastikan field input_key_admin menggunakan EchoMode.Password
        untuk menyembunyikan kunci admin dari tampilan.
        """
        dialog, _ = register_dialog
        assert dialog.input_key_admin.echoMode() == QLineEdit.EchoMode.Password

    def test_validasi_gagal_jika_field_kosong(self, qtbot, register_dialog):
        """
        Memastikan label peringatan muncul ketika tombol Register diklik
        tanpa mengisi semua field (validasi input kosong).
        """
        dialog, _ = register_dialog
        dialog.show()
        # Semua field dikosongkan
        dialog.input_nama.clear()
        dialog.input_key.clear()
        dialog.input_key_admin.clear()
        qtbot.mouseClick(dialog.btn_register, Qt.MouseButton.LeftButton)
        assert dialog.label_peringatan.text() != "", \
            "Peringatan harus muncul saat field kosong"

    def test_ketik_nama_pada_input(self, qtbot, register_dialog):
        """
        Simulasi pengguna mengetik nama pada field input_nama menggunakan
        qtbot.keyClicks(). Memastikan teks tersimpan dengan benar.
        """
        dialog, _ = register_dialog
        dialog.show()
        qtbot.keyClicks(dialog.input_nama, "Budi Santoso")
        assert dialog.input_nama.text() == "Budi Santoso"

    def test_tombol_batal_menutup_dialog(self, qtbot, register_dialog):
        """
        Memastikan klik tombol Batal menutup dialog (memanggil reject).
        Menggunakan qtbot.waitSignal untuk menangkap sinyal rejected.
        """
        dialog, _ = register_dialog
        dialog.show()
        with qtbot.waitSignal(dialog.rejected, timeout=2000):
            qtbot.mouseClick(dialog.btn_batal, Qt.MouseButton.LeftButton)

    def test_otorisasi_gagal_key_admin_salah(self, qtbot, register_dialog):
        """
        Memastikan label peringatan muncul ketika key admin tidak valid
        (bukan Super_user). DB di-mock untuk mengembalikan status gagal.
        """
        dialog, MockDB = register_dialog
        dialog.show()
        # Isi semua field
        dialog.input_nama.setText("Citra")
        dialog.input_key.setText("1234567890")
        dialog.input_key_admin.setText("wrongkey")
        # Mock: verifikasi gagal
        MockDB.return_value.verify_login.return_value = (False, "Kunci salah")
        qtbot.mouseClick(dialog.btn_register, Qt.MouseButton.LeftButton)
        assert "Otorisasi Gagal" in dialog.label_peringatan.text()

    def test_combo_role_berisi_pilihan_yang_benar(self, register_dialog):
        """
        Memastikan combo_role berisi pilihan 'Admin' dan 'Super User'
        sesuai desain sistem.
        """
        dialog, _ = register_dialog
        items = [dialog.combo_role.itemText(i) for i in range(dialog.combo_role.count())]
        assert "Admin" in items
        assert "Super User" in items
