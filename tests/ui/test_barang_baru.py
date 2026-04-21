"""
==============================================================================
test_barang_baru.py — Test Suite untuk TambahBarangBaru
==============================================================================

Menguji komponen TambahBarangBaru (src/ui/barang_baru.py).
Fixture `tambah_barang_dialog` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from unittest.mock import patch, mock_open
from PySide6.QtCore import Qt


# ===========================================================================
# SECTION 4: TEST — TambahBarangBaru
# ===========================================================================

class TestTambahBarangBaru:
    """Kumpulan tes untuk komponen TambahBarangBaru (src/ui/barang_baru.py)."""

    def test_inisialisasi_dan_ui_dasar(self, qtbot, tambah_barang_dialog):
        """Memastikan UI utama diinisialisasi dengan benar dan field-field utama ada."""
        dialog, _ = tambah_barang_dialog
        dialog.show()
        
        # Cek keberadaan field
        for attr in ["nama", "harga_jual", "sku", "combo_selector"]:
            assert hasattr(dialog, attr)
            
        # Cek isi combo_selector
        items = [dialog.combo_selector.itemText(i) for i in range(dialog.combo_selector.count())]
        assert items == ["Satuan", "Paket"]
        
        # Cek ganti mode paket
        dialog.combo_selector.setCurrentIndex(1)
        assert dialog.stack.currentIndex() == 1
        assert dialog.stack0.currentIndex() == 1
        
        # Cek interaksi UI lain
        dialog.nama.data.clear()
        qtbot.keyClicks(dialog.nama.data, "Mie Goreng")
        assert dialog.nama.data.text() == "Mie Goreng"
        
        # Cek tombol Batal
        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            qtbot.mouseClick(dialog.btn_batal, Qt.MouseButton.LeftButton)

    @pytest.mark.parametrize("index,jenis_expected,data_expected", [
        (0, "satuan", {"nama_barang": "Barang A", "harga_jual": "5000", "harga_beli": "3000", "stok": "100", "sku": "SKU-01"}),
        (1, "paket", {"nama_paket": "Barang A", "harga_jual": "5000", "nama_barang": "Barang B", "per_satuan": "10", "sku": "SKU-01"})
    ])
    def test_get_data(self, tambah_barang_dialog, index, jenis_expected, data_expected):
        """Memastikan get_data() mengembalikan format dict yang benar untuk kedua mode."""
        dialog, _ = tambah_barang_dialog
        dialog.combo_selector.setCurrentIndex(index)
        
        # Set common text
        dialog.nama.data.setText("Barang A")
        dialog.harga_jual.data.setText("5000")
        dialog.sku.data.setText("SKU-01")
        
        if index == 0:
            dialog.harga_beli.data.setText("3000")
            dialog.stok.data.setText("100")
        else:
            dialog.nama_barang.data.setText("Barang B")
            dialog.convert.data.setText("10")
            
        jenis, data = dialog.get_data()
        assert jenis == jenis_expected
        assert data == data_expected

    @pytest.mark.parametrize("index", [0, 1])
    def test_validasi_field_kosong(self, qtbot, tambah_barang_dialog, index):
        """Mencakup baris 358: Memastikan label_peringatan terisi ketika tombol Tambahkan diklik dengan field kosong pada mode Satuan dan Paket."""
        dialog, _ = tambah_barang_dialog
        dialog.show()
        dialog.combo_selector.setCurrentIndex(index)
        # Empty fields
        dialog.nama.data.clear()
        dialog.harga_jual.data.clear()
        dialog.sku.data.clear()
        
        qtbot.mouseClick(dialog.btn_tambahkan, Qt.MouseButton.LeftButton)
        assert dialog.label_peringatan.text() == "Semua Kolom Wajib Diisi"

    @pytest.mark.parametrize("index, db_return, expected_accepted, expected_warning", [
        (0, {"is_valid": True}, True, ""), # Satuan Berhasil
        (1, {"is_valid": True}, True, ""), # Paket Berhasil
        (0, {"is_valid": False, "nama_barang": True, "sku_barang": True}, False, "Nama Barang dan SKU sudah ada"),
        (0, {"is_valid": False, "nama_barang": True, "sku_barang": False}, False, "Nama Barang sudah ada"),
        (0, {"is_valid": False, "nama_barang": False, "sku_barang": True}, False, "SKU sudah ada"),
        (1, {"is_valid": False, "nama_barang": True, "sku_barang": False, "nama_produk": False}, False, "Nama Barang sudah ada"),
        (1, {"is_valid": False, "nama_barang": False, "sku_barang": True, "nama_produk": False}, False, "SKU sudah ada"),
        (1, {"is_valid": False, "nama_barang": False, "sku_barang": False, "nama_produk": True}, False, "Nama Barang Tidak Ditemukan"),
    ])
    def test_validasi_data_ke_db(self, qtbot, tambah_barang_dialog, index, db_return, expected_accepted, expected_warning):
        """Menguji kombinasi validasi data Satuan & Paket langsung dari mock database."""
        dialog, mock_db = tambah_barang_dialog
        dialog.combo_selector.setCurrentIndex(index)
        
        dialog.nama.data.setText("ValidName")
        dialog.harga_jual.data.setText("1000")
        dialog.sku.data.setText("SKU-123")
        if index == 0:
            dialog.harga_beli.data.setText("500")
            dialog.stok.data.setText("10")
        else:
            dialog.nama_barang.data.setText("SubItem")
            dialog.convert.data.setText("2")

        mock_db.return_value.verify_is_valid.return_value = db_return
        
        if expected_accepted:
            with qtbot.waitSignal(dialog.accepted, timeout=1000):
                qtbot.mouseClick(dialog.btn_tambahkan, Qt.MouseButton.LeftButton)
        else:
            qtbot.mouseClick(dialog.btn_tambahkan, Qt.MouseButton.LeftButton)
            assert expected_warning in dialog.label_peringatan.text()

    @pytest.mark.parametrize("file_return, file_content, db_return, expected_msg_type, expected_text", [
        (("", ""), None, None, None, None), # Batal import
        (("dummy.csv", "CSV"), "Error", None, "critical", "Format file salah"), # Exception builtins.open
        (("empty.csv", "CSV"), "", None, "critical", "File kosong"), # Mencakup baris 410 (raise ValueError)
        (("dummy.csv", "CSV"), "a,b\n1,2", {"error_format": "Kolom tidak sesuai"}, "critical", "Kolom tidak sesuai"),
        (("dummy.csv", "CSV"), "a,b\n1,2", {"berhasil": 2, "gagal": 0, "errors": []}, "information", "Berhasil diimpor: 2"),
        (("dummy.csv", "CSV"), "a,b\n1,2", {"berhasil": 1, "gagal": 1, "errors": ["Err1"]}, "warning", "Gagal diimpor: 1"),
        (("dummy.csv", "CSV"), "a,b\n1,2", {"berhasil": 0, "gagal": 2, "errors": ["E1","E2"]}, "critical", "Gagal diimpor: 2"),
        (("dummy.csv", "CSV"), "a,b\n1,2", {"berhasil": 1, "gagal": 7, "errors": ["e1","e2","e3","e4","e5","e6","e7"]}, "warning", "... dan 2 baris lainnya."), 
    ])
    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    @patch("src.ui.barang_baru.CustomMessageBox")
    def test_import_csv(self, mock_msg, mock_filedialog, tambah_barang_dialog, file_return, file_content, db_return, expected_msg_type, expected_text):
        """Kumpulan tes import CSV yang disederhanakan melalui parameterisasi."""
        dialog, mock_db = tambah_barang_dialog
        mock_filedialog.return_value = file_return
        
        if db_return:
            mock_db.return_value.import_batch_csv.return_value = db_return
            
        if file_content == "Error":
            with patch("builtins.open", side_effect=Exception("I/O Error")):
                dialog.import_csv_dialog()
            assert mock_msg.critical.called
            assert expected_text in mock_msg.critical.call_args[0][2]
        elif file_content is not None:
            with patch("builtins.open", mock_open(read_data=file_content)):
                dialog.import_csv_dialog()
            msg_mock = getattr(mock_msg, expected_msg_type)
            assert msg_mock.called
            assert expected_text in msg_mock.call_args[0][2]
        else:
            dialog.import_csv_dialog()
            assert not mock_msg.critical.called

    @pytest.mark.parametrize("exists, save_return, copy_side_effect, expected_msg_type, expected_text", [
        (False, None, None, "critical", "tidak ditemukan"),
        (True, ("path.csv", "CSV"), None, "information", "berhasil disimpan"), # Mencakup baris 410 copy2
        (True, ("path.csv", "CSV"), Exception("Perm denied"), "critical", "Perm denied"),
    ])
    @patch("os.path.exists")
    @patch("PySide6.QtWidgets.QFileDialog.getSaveFileName")
    @patch("shutil.copy2", autospec=True)
    @patch("src.ui.barang_baru.CustomMessageBox")
    def test_download_template_csv(self, mock_msg, mock_copy, mock_save, mock_exists, tambah_barang_dialog, exists, save_return, copy_side_effect, expected_msg_type, expected_text):
        """Kumpulan tes untuk fungsi download template CSV."""
        dialog, _ = tambah_barang_dialog
        mock_exists.return_value = exists
        if save_return:
            mock_save.return_value = save_return
        if copy_side_effect:
            mock_copy.side_effect = copy_side_effect
            
        dialog.download_template_csv()
        
        msg_mock = getattr(mock_msg, expected_msg_type)
        assert msg_mock.called
        assert expected_text in msg_mock.call_args[0][2]
