"""
==============================================================================
test_hapus_produk.py — Test Suite untuk HapusProdukDialog
==============================================================================

Menguji komponen HapusProdukDialog (src/ui/hapus_produk.py).
Fixture `hapus_produk_dialog` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from PySide6.QtCore import Qt


# ===========================================================================
# SECTION 5: TEST — HapusProdukDialog
# ===========================================================================

class TestHapusProdukDialog:
    """Kumpulan tes untuk HapusProdukDialog (src/ui/hapus_produk.py)."""

    def test_dialog_terbuat_dengan_elemen_utama(self, hapus_produk_dialog):
        """
        Memastikan HapusProdukDialog berhasil dibuat dan memiliki elemen
        utama: input_sku, input_verifikasi, button_hapus, button_batal.
        """
        dialog, _ = hapus_produk_dialog
        assert hasattr(dialog, "input_sku")
        assert hasattr(dialog, "input_verifikasi")
        assert hasattr(dialog, "button_hapus")
        assert hasattr(dialog, "button_batal")

    def test_button_hapus_nonaktif_saat_awal(self, hapus_produk_dialog):
        """
        Memastikan button_hapus dalam keadaan disabled saat dialog pertama
        dibuka (sebelum produk dicari dan ditemukan).
        """
        dialog, _ = hapus_produk_dialog
        assert not dialog.button_hapus.isEnabled(), \
            "Tombol hapus harus disabled sebelum produk ditemukan"

    def test_cari_tanpa_sku_menampilkan_status(self, qtbot, hapus_produk_dialog):
        """
        Memastikan mencari produk tanpa mengisi SKU menampilkan
        pesan status error pada label_status.
        """
        dialog, _ = hapus_produk_dialog
        dialog.show()
        dialog.input_sku.clear()
        qtbot.mouseClick(dialog.button_cari, Qt.MouseButton.LeftButton)
        assert "SKU wajib diisi" in dialog.label_status.text()

    def test_cari_sku_tidak_ditemukan(self, qtbot, hapus_produk_dialog):
        """
        Memastikan label detail dan status berubah ketika SKU yang dicari
        tidak ada di database (DB di-mock mengembalikan None).
        """
        dialog, mock_db = hapus_produk_dialog
        mock_db.get_produk_for_delete.return_value = None
        dialog.show()
        dialog.input_sku.setText("INVALID-SKU")
        qtbot.mouseClick(dialog.button_cari, Qt.MouseButton.LeftButton)
        assert "tidak ditemukan" in dialog.label_detail.text()
        assert not dialog.button_hapus.isEnabled()

    def test_cari_sku_berhasil_mengaktifkan_tombol_hapus(self, qtbot, hapus_produk_dialog):
        """
        Memastikan button_hapus menjadi enabled setelah pencarian
        produk berhasil (DB mengembalikan data produk valid).
        """
        dialog, mock_db = hapus_produk_dialog
        mock_db.get_produk_for_delete.return_value = {
            "sku": "ABC-001",
            "nama_barang": "Pensil 2B",
            "stok": 50,
            "harga_jual": 3000,
            "harga_beli": 2000,
        }
        dialog.show()
        dialog.input_sku.setText("ABC-001")
        qtbot.mouseClick(dialog.button_cari, Qt.MouseButton.LeftButton)
        assert dialog.button_hapus.isEnabled(), \
            "Tombol hapus harus aktif setelah produk ditemukan"

    def test_hapus_tanpa_verifikasi_ditolak(self, qtbot, hapus_produk_dialog):
        """
        Memastikan penghapusan gagal ketika teks verifikasi bukan 'HAPUS'.
        Label status harus menampilkan pesan gagal verifikasi.
        """
        dialog, mock_db = hapus_produk_dialog
        mock_db.get_produk_for_delete.return_value = {
            "sku": "ABC-001", "nama_barang": "Pensil 2B",
            "stok": 50, "harga_jual": 3000, "harga_beli": 2000,
        }
        dialog.show()
        # Cari produk terlebih dahulu
        dialog.input_sku.setText("ABC-001")
        dialog.button_cari.click()
        # Ketik verifikasi yang salah
        dialog.input_verifikasi.setText("TIDAK")
        qtbot.mouseClick(dialog.button_hapus, Qt.MouseButton.LeftButton)
        assert "Verifikasi gagal" in dialog.label_status.text()

    def test_ketik_verifikasi_hapus(self, qtbot, hapus_produk_dialog):
        """
        Simulasi pengguna mengetik kata 'HAPUS' pada field verifikasi
        menggunakan qtbot.keyClicks().
        """
        dialog, _ = hapus_produk_dialog
        dialog.show()
        qtbot.keyClicks(dialog.input_verifikasi, "HAPUS")
        assert dialog.input_verifikasi.text() == "HAPUS"

    def test_tombol_batal_memanggil_reject(self, qtbot, hapus_produk_dialog):
        """
        Memastikan klik tombol Batal mengirimkan sinyal rejected.
        """
        dialog, _ = hapus_produk_dialog
        dialog.show()
        with qtbot.waitSignal(dialog.rejected, timeout=2000):
            qtbot.mouseClick(dialog.button_batal, Qt.MouseButton.LeftButton)

    def test_hapus_berhasil_menutup_dialog(self, qtbot, hapus_produk_dialog):
        """
        Simulasi alur hapus produk secara penuh:
        1. Cari produk (DB mengembalikan data valid)
        2. Ketik 'HAPUS' pada verifikasi
        3. Klik tombol Hapus
        4. DB.delete_produk_bersih mengembalikan sukses
        5. Dialog harus menutup (accepted)
        """
        dialog, mock_db = hapus_produk_dialog
        mock_db.get_produk_for_delete.return_value = {
            "sku": "ABC-001", "nama_barang": "Pensil 2B",
            "stok": 50, "harga_jual": 3000, "harga_beli": 2000,
        }
        mock_db.delete_produk_bersih.return_value = {
            "deleted": True,
            "deleted_produk_paket": 0,
        }
        dialog.show()
        dialog.input_sku.setText("ABC-001")
        dialog.button_cari.click()
        dialog.input_verifikasi.setText("HAPUS")

        with qtbot.waitSignal(dialog.accepted, timeout=2000):
            qtbot.mouseClick(dialog.button_hapus, Qt.MouseButton.LeftButton)
