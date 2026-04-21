"""
==============================================================================
test_pelanggan.py — Test Suite untuk TambahPelangganDialog
==============================================================================

Menguji komponen TambahPelangganDialog (src/ui/tambah_pelanggan.py).
Fixture `tambah_pelanggan_dialog` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from PySide6.QtCore import Qt


# ===========================================================================
# SECTION 7: TEST — TambahPelangganDialog
# ===========================================================================

class TestTambahPelangganDialog:
    """Kumpulan tes untuk TambahPelangganDialog (src/ui/tambah_pelanggan.py)."""

    def test_dialog_terbuat_dengan_field_utama(self, tambah_pelanggan_dialog):
        """
        Memastikan TambahPelangganDialog berhasil dibuat dan memiliki
        field input utama: input_nama, input_nohp, input_alamat.
        """
        dialog = tambah_pelanggan_dialog
        assert hasattr(dialog, "input_nama")
        assert hasattr(dialog, "input_nohp")
        assert hasattr(dialog, "input_alamat")

    def test_ketik_nama_pelanggan(self, qtbot, tambah_pelanggan_dialog):
        """
        Simulasi pengguna mengetik nama pelanggan pada field input_nama
        menggunakan qtbot.keyClicks().
        """
        dialog = tambah_pelanggan_dialog
        dialog.show()
        dialog.input_nama.data.clear()
        qtbot.keyClicks(dialog.input_nama.data, "Rina Wati")
        assert dialog.input_nama.data.text() == "Rina Wati"

    def test_validasi_nama_kosong_menampilkan_peringatan(self, qtbot, tambah_pelanggan_dialog):
        """
        Memastikan label_peringatan muncul ketika tombol Tambahkan diklik
        tanpa mengisi nama pelanggan (nama adalah field wajib).
        """
        dialog = tambah_pelanggan_dialog
        dialog.show()
        dialog.input_nama.data.clear()
        qtbot.mouseClick(dialog.btn_tambahkan, Qt.MouseButton.LeftButton)
        assert dialog.label_peringatan.text() != ""

    def test_validasi_berhasil_jika_nama_terisi(self, qtbot, tambah_pelanggan_dialog):
        """
        Memastikan dialog diterima (accepted) ketika nama pelanggan diisi.
        Sinyal accepted harus diemit.
        """
        dialog = tambah_pelanggan_dialog
        dialog.show()
        dialog.input_nama.data.setText("Budi")
        with qtbot.waitSignal(dialog.accepted, timeout=2000):
            qtbot.mouseClick(dialog.btn_tambahkan, Qt.MouseButton.LeftButton)

    def test_get_data_mengembalikan_dict_lengkap(self, tambah_pelanggan_dialog):
        """
        Memastikan get_data() mengembalikan dict dengan key: nama, nomer_hp, alamat.
        """
        dialog = tambah_pelanggan_dialog
        dialog.input_nama.data.setText("Dewi")
        dialog.input_nohp.data.setText("081234567890")
        dialog.input_alamat.data.setText("Jl. Mawar No.1")
        data = dialog.get_data()
        assert data["nama"] == "Dewi"
        assert data["nomer_hp"] == "081234567890"
        assert data["alamat"] == "Jl. Mawar No.1"

    def test_tombol_batal_memanggil_reject(self, qtbot, tambah_pelanggan_dialog):
        """
        Memastikan klik tombol Batal mengirimkan sinyal rejected dari dialog.
        """
        dialog = tambah_pelanggan_dialog
        dialog.show()
        with qtbot.waitSignal(dialog.rejected, timeout=2000):
            qtbot.mouseClick(dialog.btn_batal, Qt.MouseButton.LeftButton)
