"""
==============================================================================
test_ui.py — Test Suite untuk Komponen UI Aplikasi POS
==============================================================================

Framework  : pytest + pytest-qt (qtbot)
Deskripsi  : Berisi unit test dan integration test dasar untuk setiap
             komponen UI di direktori src/ui/. Semua panggilan ke database
             dan layer backend di-mock menggunakan unittest.mock agar tes
             dapat berjalan tanpa koneksi database nyata (headless-friendly).

Cara menjalankan:
    pytest tests/test_ui.py -v
    pytest tests/test_ui.py -v -k "test_login"   # filter nama tes tertentu

Dependensi:
    pip install pytest pytest-qt
==============================================================================
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock, mock_open

# ---------------------------------------------------------------------------
# Pastikan root proyek ada di sys.path agar import relatif berfungsi
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QDialog


# ===========================================================================
# SECTION 1: FIXTURES — Inisialisasi widget dengan mock backend
# ===========================================================================

@pytest.fixture
def login_page(qtbot):
    """
    Fixture untuk LoginPage.

    Mem-patch DatabaseManager agar tidak menyentuh SQLite sungguhan saat
    tombol login diklik maupun saat inisialisasi widget.
    """
    with patch("src.ui.login.DatabaseManager") as MockDB:
        MockDB.return_value = MagicMock()
        from src.ui.login import LoginPage
        widget = LoginPage(on_login_success=MagicMock())
        qtbot.addWidget(widget)
        yield widget, MockDB


@pytest.fixture
def register_dialog(qtbot):
    """
    Fixture untuk RegisterDialog.

    Mem-patch DatabaseManager dan ScreenSize agar dialog dapat dibuat
    tanpa koneksi DB dan tanpa bergantung pada resolusi layar fisik.
    """
    with patch("src.ui.register.DatabaseManager") as MockDB, \
         patch("src.ui.register.ScreenSize") as MockScreen:
        MockScreen.return_value.get_centered_position.return_value = (100, 100)
        MockDB.return_value = MagicMock()
        from src.ui.register import RegisterDialog
        dialog = RegisterDialog()
        qtbot.addWidget(dialog)
        yield dialog, MockDB


@pytest.fixture
def tambah_barang_dialog(qtbot):
    """
    Fixture untuk TambahBarangBaru (dialog tambah produk baru).

    Mem-patch DatabaseManager dan ScreenSize.
    """
    with patch("src.ui.barang_baru.DatabaseManager") as MockDB, \
         patch("src.ui.barang_baru.ScreenSize") as MockScreen:
        MockScreen.return_value.get_centered_position.return_value = (100, 100)
        MockDB.return_value = MagicMock()
        from src.ui.barang_baru import TambahBarangBaru
        dialog = TambahBarangBaru()
        qtbot.addWidget(dialog)
        yield dialog, MockDB


@pytest.fixture
def hapus_produk_dialog(qtbot):
    """
    Fixture untuk HapusProdukDialog (dialog hapus produk).

    Mem-patch DatabaseManager dan ScreenSize.
    """
    with patch("src.ui.hapus_produk.DatabaseManager") as MockDB, \
         patch("src.ui.hapus_produk.ScreenSize") as MockScreen:
        MockScreen.return_value.get_centered_position.return_value = (100, 100)
        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance
        from src.ui.hapus_produk import HapusProdukDialog
        dialog = HapusProdukDialog()
        qtbot.addWidget(dialog)
        yield dialog, mock_db_instance


@pytest.fixture
def discount_popup(qtbot):
    """
    Fixture untuk DiscountPopup.

    Dialog ini tidak memerlukan database, namun membutuhkan
    discount_state dict dan apply_callback callable.
    """
    from src.ui.discount import DiscountPopup
    apply_cb = MagicMock()
    state = {"mode": None, "percent": 0, "nominal_input": 0}
    dialog = DiscountPopup(parent=None, discount_state=state, apply_callback=apply_cb)
    qtbot.addWidget(dialog)
    yield dialog, apply_cb


@pytest.fixture
def tambah_pelanggan_dialog(qtbot):
    """
    Fixture untuk TambahPelangganDialog.

    Dialog ini tidak memanggil DB secara langsung (validasi dan submit
    dilakukan oleh pemanggil), namun ScreenSize di-patch untuk keamanan.
    """
    with patch("src.ui.tambah_pelanggan.ScreenSize") as MockScreen:
        MockScreen.return_value.get_centered_position.return_value = (100, 100)
        from src.ui.tambah_pelanggan import TambahPelangganDialog
        dialog = TambahPelangganDialog()
        qtbot.addWidget(dialog)
        yield dialog


@pytest.fixture
def welcome_window(qtbot):
    """Fixture untuk WelcomeWindow (tidak ada dependency DB)."""
    from src.ui.welcome import WelcomeWindow
    widget = WelcomeWindow()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def error_window(qtbot):
    """Fixture untuk ErrorWindow (tidak ada dependency DB)."""
    from src.ui.error import ErrorWindow
    widget = ErrorWindow()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def dialog_title_bar(qtbot):
    """Fixture untuk DialogTitleBar."""
    from src.ui.dialog_title_bar import DialogTitleBar
    widget = DialogTitleBar("Judul Test")
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def manajemen_produk(qtbot):
    """
    Fixture untuk ManajemenProduk.

    Kelas ini memanggil DatabaseManager saat inisialisasi (table_data).
    Seluruh interaksi DB di-mock.
    """
    with patch("src.ui.manajemen_produk.DatabaseManager") as MockDB, \
         patch("src.ui.barang_baru.DatabaseManager"), \
         patch("src.ui.hapus_produk.DatabaseManager"), \
         patch("src.ui.edit_produk.DatabaseManager"), \
         patch("src.utils.fungsi.NavigationButton", new_callable=lambda: _MockNavButton):
        mock_db = MagicMock()
        mock_db.get_produk_satuan.return_value = []
        mock_db.get_produk_paket.return_value = []
        mock_db.get_rows_produk.return_value = 0
        MockDB.return_value = mock_db

        from src.ui.manajemen_produk import ManajemenProduk
        widget = ManajemenProduk()
        qtbot.addWidget(widget)
        yield widget, mock_db


@pytest.fixture
def dashboard(qtbot):
    """
    Fixture untuk Dashboard.

    Semua sub-widget yang memerlukan DB di-mock secara agresif agar
    Dashboard bisa diinisialisasi dalam lingkungan headless.
    """
    user_data = {"role": "Super_user", "nama": "Tester"}
    with patch("src.ui.dashboard.DatabaseManager") as MockDB, \
         patch("src.ui.welcome.asset_path", return_value=""), \
         patch("src.ui.error.asset_path", return_value=""), \
         patch("src.ui.dashboard.asset_path", return_value=""), \
         patch("src.ui.manajemen_produk.DatabaseManager"), \
         patch("src.ui.transaksi.DatabaseManager"), \
         patch("src.ui.sejarah_transaksi.DatabaseManager"):
        MockDB.return_value = MagicMock()
        from src.ui.dashboard import Dashboard
        widget = Dashboard(data=user_data)
        qtbot.addWidget(widget)
        yield widget, MockDB


# ---------------------------------------------------------------------------
# Helper internal: NavigationButton pengganti untuk tes ManajemenProduk
# (menghindari path asset yang tidak ada)
# ---------------------------------------------------------------------------
class _MockNavButton:
    """Pengganti NavigationButton agar ManajemenProduk bisa diinisialisasi."""
    def __new__(cls, *args, **kwargs):
        from PySide6.QtWidgets import QPushButton
        return QPushButton()


# ===========================================================================
# SECTION 2: TEST — LoginPage
# ===========================================================================

class TestLoginPage:
    """Kumpulan tes untuk komponen LoginPage (src/ui/login.py)."""

    def test_widget_terbuat_dan_terlihat(self, login_page):
        """
        Memastikan LoginPage berhasil diinstansiasi dan widget utama ada.
        Widget harus memiliki atribut text_input dan login_button.
        """
        widget, _ = login_page
        assert widget is not None
        assert hasattr(widget, "text_input"), "LoginPage harus memiliki atribut text_input"
        assert hasattr(widget, "login_button"), "LoginPage harus memiliki atribut login_button"

    def test_text_input_adalah_qlineedit(self, login_page):
        """
        Memastikan text_input adalah instance QLineEdit dengan EchoMode Password
        (karena ini field kunci/password).
        """
        widget, _ = login_page
        assert isinstance(widget.text_input, QLineEdit)
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password

    def test_ketik_teks_pada_input(self, qtbot, login_page):
        """
        Simulasi pengguna mengetik teks pada field input menggunakan
        qtbot.keyClicks(). Memastikan teks berhasil masuk ke widget.
        """
        widget, _ = login_page
        widget.show()
        qtbot.keyClicks(widget.text_input, "123456")
        assert widget.text_input.text() == "123456"

    def test_login_gagal_input_bukan_angka(self, qtbot, login_page):
        """
        Memastikan pesan error muncul ketika pengguna mengetik teks bukan angka
        (misalnya huruf) lalu mengklik tombol login.
        """
        widget, MockDB = login_page
        widget.show()
        widget.text_input.setText("abc")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        assert "Kunci Hanya Berupa Angka" in widget.error_info.text()

    def test_login_berhasil_memanggil_callback(self, qtbot, login_page):
        """
        Memastikan on_login_success callback dipanggil ketika login berhasil.
        DatabaseManager.verify_login di-mock untuk mengembalikan (True, {...}).
        """
        widget, MockDB = login_page
        fake_user = {"nama": "Tester", "role": "Admin"}
        MockDB.return_value.verify_login.return_value = (True, fake_user)
        widget.show()
        widget.text_input.setText("123456")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        widget.on_login_success.assert_called_once_with(fake_user)

    def test_login_gagal_menampilkan_pesan_error(self, qtbot, login_page):
        """
        Memastikan pesan error dari DB ditampilkan di label error_info
        ketika verify_login mengembalikan (False, pesan_error).
        """
        widget, MockDB = login_page
        MockDB.return_value.verify_login.return_value = (False, "Kunci salah!")
        widget.show()
        widget.text_input.setText("999999")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        assert "Kunci salah!" in widget.error_info.text()

    def test_toggle_password_visibility(self, qtbot, login_page):
        """
        Memastikan toggle_visibility_button mengubah EchoMode dari Password
        ke Normal dan sebaliknya.
        """
        widget, _ = login_page
        widget.show()
        # Kondisi awal: password tersembunyi
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password
        qtbot.mouseClick(widget.toggle_visibility_button, Qt.MouseButton.LeftButton)
        # Setelah klik: seharusnya Normal
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Normal
        qtbot.mouseClick(widget.toggle_visibility_button, Qt.MouseButton.LeftButton)
        # Setelah klik ke-2: kembali Password
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password

    def test_session_info_mengubah_teks(self, login_page):
        """
        Memastikan metode session_info() mengubah teks label error_info.
        Digunakan untuk menampilkan informasi sesi yang sudah berakhir.
        """
        widget, _ = login_page
        widget.session_info("Sesi telah berakhir. Silakan login ulang.")
        assert "Sesi telah berakhir" in widget.error_info.text()


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


# ===========================================================================
# SECTION 6: TEST — DiscountPopup
# ===========================================================================

class TestDiscountPopup:
    """Kumpulan tes untuk DiscountPopup (src/ui/discount.py)."""

    def test_dialog_terbuat_dengan_field_input(self, discount_popup):
        """
        Memastikan DiscountPopup terbuat dengan field percent_input,
        nominal_input, dan tombol-tombol yang dibutuhkan.
        """
        dialog, _ = discount_popup
        assert hasattr(dialog, "percent_input")
        assert hasattr(dialog, "nominal_input")
        assert hasattr(dialog, "apply_button")
        assert hasattr(dialog, "reset_button")
        assert hasattr(dialog, "cancel_button")

    def test_ketik_persen_diskon(self, qtbot, discount_popup):
        """
        Simulasi pengguna mengetik nilai persentase diskon (misalnya '10')
        pada field percent_input.
        """
        dialog, _ = discount_popup
        dialog.show()
        dialog.percent_input.clear()
        qtbot.keyClicks(dialog.percent_input, "10")
        assert "10" in dialog.percent_input.text()

    def test_isi_persen_menonaktifkan_nominal(self, qtbot, discount_popup):
        """
        Memastikan mengisi field percent_input menonaktifkan (disable)
        field nominal_input untuk mencegah konflik diskon ganda.
        """
        dialog, _ = discount_popup
        dialog.show()
        dialog.percent_input.clear()
        dialog.nominal_input.clear()
        dialog.percent_input.setText("15")
        # Picu event textChanged secara manual
        dialog.percent_input.textChanged.emit("15")
        assert not dialog.nominal_input.isEnabled(), \
            "nominal_input harus disabled saat percent_input terisi"

    def test_apply_discount_memanggil_callback(self, qtbot, discount_popup):
        """
        Memastikan klik tombol Terapkan memanggil apply_callback
        dengan payload yang sesuai (mode 'percent').
        """
        dialog, apply_cb = discount_popup
        dialog.show()
        dialog.percent_input.setText("20")
        dialog.nominal_input.clear()
        qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        apply_cb.assert_called_once()
        args = apply_cb.call_args[0][0]
        assert args["mode"] == "percent"
        assert args["percent"] == 20

    def test_reset_discount_mengosongkan_semua_field(self, qtbot, discount_popup):
        """
        Memastikan klik tombol Reset mengosongkan kedua field input
        dan memanggil callback dengan mode None.
        """
        dialog, apply_cb = discount_popup
        dialog.show()
        dialog.percent_input.setText("10")
        qtbot.mouseClick(dialog.reset_button, Qt.MouseButton.LeftButton)
        assert dialog.percent_input.text() == ""
        assert dialog.nominal_input.text() == ""

    def test_preview_label_berubah_saat_ketik_persen(self, qtbot, discount_popup):
        """
        Memastikan preview_label diperbarui saat pengguna mengetik
        nilai persentase pada field percent_input.
        """
        dialog, _ = discount_popup
        dialog.show()
        dialog.percent_input.setText("25")
        dialog.percent_input.textChanged.emit("25")
        assert "25" in dialog.preview_label.text() or "%" in dialog.preview_label.text()


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


# ===========================================================================
# SECTION 8: TEST — WelcomeWindow & ErrorWindow
# ===========================================================================

class TestWelcomeWindow:
    """Kumpulan tes untuk WelcomeWindow (src/ui/welcome.py)."""

    def test_widget_terbuat_tanpa_error(self, welcome_window):
        """
        Memastikan WelcomeWindow berhasil diinstansiasi tanpa exception.
        Widget ini hanya menampilkan gambar selamat datang.
        """
        assert welcome_window is not None

    def test_widget_dapat_ditampilkan(self, qtbot, welcome_window):
        """
        Memastikan WelcomeWindow dapat ditampilkan (show()) tanpa error.
        """
        welcome_window.show()
        assert welcome_window.isVisible()


class TestErrorWindow:
    """Kumpulan tes untuk ErrorWindow (src/ui/error.py)."""

    def test_widget_terbuat_tanpa_error(self, error_window):
        """
        Memastikan ErrorWindow berhasil diinstansiasi tanpa exception.
        Widget ini menampilkan halaman error 404.
        """
        assert error_window is not None

    def test_widget_dapat_ditampilkan(self, qtbot, error_window):
        """
        Memastikan ErrorWindow dapat ditampilkan (show()) tanpa error.
        """
        error_window.show()
        assert error_window.isVisible()


# ===========================================================================
# SECTION 9: TEST — DialogTitleBar
# ===========================================================================

class TestDialogTitleBar:
    """Kumpulan tes untuk DialogTitleBar (src/ui/dialog_title_bar.py)."""

    def test_title_bar_terbuat_dengan_judul(self, dialog_title_bar):
        """
        Memastikan DialogTitleBar berhasil dibuat dan memiliki
        tombol close (tombol_x).
        """
        assert dialog_title_bar is not None
        assert hasattr(dialog_title_bar, "tombol_x")

    def test_tinggi_title_bar_adalah_40(self, dialog_title_bar):
        """
        Memastikan tinggi DialogTitleBar sesuai desain yaitu 40px.
        """
        assert dialog_title_bar.height() == 40

    def test_tombol_x_ada_dan_bisa_diklik(self, qtbot, dialog_title_bar):
        """
        Memastikan tombol 'X' pada title bar dapat diklik tanpa error.
        (Tidak ada parent dialog sehingga close_dialog tidak melakukan apa-apa)
        """
        dialog_title_bar.show()
        qtbot.mouseClick(dialog_title_bar.tombol_x, Qt.MouseButton.LeftButton)
        # Tidak ada exception = sukses


# ===========================================================================
# SECTION 10: TEST — Komponen UI Dasar (BaseTableWidget, BaseDataPage)
# ===========================================================================

class TestBaseTableWidget:
    """Kumpulan tes untuk BaseTableWidget (src/ui/ui_base.py)."""

    @pytest.fixture
    def concrete_table(self, qtbot):
        """
        Fixture untuk subclass konkret BaseTableWidget menggunakan
        ProdukSatuanTable dari ManajemenProduk sebagai implementasi nyata.
        """
        from src.ui.manajemen_produk import ProdukSatuanTable
        widget = ProdukSatuanTable()
        qtbot.addWidget(widget)
        return widget

    def test_tabel_terbuat_dengan_kolom_yang_benar(self, concrete_table):
        """
        Memastikan QTableWidget memiliki jumlah kolom sesuai COLUMN_WIDTHS
        yang didefinisikan di ProdukSatuanTable.
        """
        from src.ui.manajemen_produk import ProdukSatuanTable
        expected_cols = len(ProdukSatuanTable.COLUMN_WIDTHS)
        assert concrete_table.table.columnCount() == expected_cols

    def test_set_data_mengisi_tabel(self, concrete_table):
        """
        Memastikan set_data() mengisi baris tabel dengan data yang diberikan.
        """
        sample_data = [
            {"sku": "A001", "nama_barang": "Pensil", "stock": 10,
             "harga_jual": 2000, "tgl_masuk": "2025-01-01"},
        ]
        concrete_table.set_data(sample_data)
        # Pastikan baris pertama, kolom pertama (SKU) terisi
        item = concrete_table.table.item(0, 0)
        assert item is not None
        assert item.text() == "A001"


# ===========================================================================
# SECTION 11: TEST — ActionButton (ui_base.py)
# ===========================================================================

class TestActionButton:
    """Kumpulan tes untuk komponen ActionButton (src/ui/ui_base.py)."""

    @pytest.fixture
    def action_button(self, qtbot):
        """Fixture untuk ActionButton dengan teks dan warna tertentu."""
        from src.ui.ui_base import ActionButton
        btn = ActionButton("Klik Saya", "#00ff00", width=150, height=40)
        qtbot.addWidget(btn)
        return btn

    def test_button_terbuat_dengan_teks_benar(self, action_button):
        """
        Memastikan ActionButton dibuat dengan teks yang sesuai.
        """
        assert action_button.text() == "Klik Saya"

    def test_button_ukuran_sesuai(self, action_button):
        """
        Memastikan ActionButton memiliki ukuran width=150, height=40.
        """
        assert action_button.width() == 150
        assert action_button.height() == 40

    def test_klik_mengemit_sinyal_clicked(self, qtbot, action_button):
        """
        Memastikan klik pada ActionButton mengemit sinyal clicked.
        Menggunakan qtbot.waitSignal() untuk menangkap sinyal.
        """
        with qtbot.waitSignal(action_button.clicked, timeout=1000):
            qtbot.mouseClick(action_button, Qt.MouseButton.LeftButton)


# ===========================================================================
# SECTION 12: TEST INTEGRASI — Dashboard (init + navigasi sidebar)
# ===========================================================================

class TestDashboard:
    """
    Integration test untuk Dashboard (src/ui/dashboard.py).
    Menguji inisialisasi dan interaksi sidebar navigasi.
    """

    def test_dashboard_terbuat_dengan_sidebar(self, dashboard):
        """
        Memastikan Dashboard berhasil dibuat dengan atribut sidebar kiri,
        sidebar kanan, dan main_stack.
        """
        widget, _ = dashboard
        assert hasattr(widget, "sidebar_left")
        assert hasattr(widget, "sidebar_right")
        assert hasattr(widget, "main_stack")

    def test_sidebar_kanan_tersembunyi_saat_awal(self, dashboard):
        """
        Memastikan sidebar kanan disembunyikan saat Dashboard pertama
        kali dibuat (hanya sidebar kiri yang terlihat).
        """
        widget, _ = dashboard
        widget.show()
        assert not widget.sidebar_right.isVisible(), \
            "Sidebar kanan harus tersembunyi pada awal"
        assert widget.sidebar_left.isVisible(), \
            "Sidebar kiri harus terlihat pada awal"

    def test_klik_menu_menampilkan_sidebar_kanan(self, qtbot, dashboard):
        """
        Memastikan klik button_menu_left menyembunyikan sidebar kiri
        dan menampilkan sidebar kanan (efek toggle sidebar).
        """
        widget, _ = dashboard
        widget.show()
        qtbot.mouseClick(widget.button_menu_left, Qt.MouseButton.LeftButton)
        assert widget.sidebar_right.isVisible()
        assert not widget.sidebar_left.isVisible()

    def test_klik_menu_kanan_mengembalikan_sidebar_kiri(self, qtbot, dashboard):
        """
        Memastikan klik button_menu_right mengembalikan tampilan ke
        sidebar kiri (toggle balik).
        """
        widget, _ = dashboard
        widget.show()
        # Buka sidebar kanan dahulu
        qtbot.mouseClick(widget.button_menu_left, Qt.MouseButton.LeftButton)
        # Lalu klik menu kanan untuk toggle kembali
        qtbot.mouseClick(widget.button_menu_right, Qt.MouseButton.LeftButton)
        assert widget.sidebar_left.isVisible()
        assert not widget.sidebar_right.isVisible()

    def test_role_super_user_memperlihatkan_semua_menu(self, dashboard):
        """
        Memastikan semua tombol menu tersedia untuk role 'Super_user'
        (tidak ada yang disembunyikan karena pembatasan role).
        """
        widget, _ = dashboard
        widget.show()
        # Dengan role Super_user, tombol kas dan user harus terlihat
        assert widget.button_kas_left.isVisible()
        assert widget.button_user_left.isVisible()

    def test_welcome_widget_aktif_saat_awal(self, dashboard):
        """
        Memastikan main_stack menampilkan WelcomeWindow sebagai widget
        aktif pertama saat Dashboard baru dibuka.
        """
        widget, _ = dashboard
        current = widget.main_stack.currentWidget()
        assert current is widget.welcome_widget, \
            "WelcomeWindow harus menjadi widget aktif pertama"


# ===========================================================================
# SECTION 13: TEST — DiscountPopup dengan state awal terisi
# ===========================================================================

class TestDiscountPopupDenganStateAwal:
    """Test DiscountPopup ketika diinisialisasi dengan state diskon yang sudah ada."""

    def test_popup_menampilkan_nilai_persen_yang_ada(self, qtbot):
        """
        Memastikan DiscountPopup mengisi percent_input dengan nilai dari
        discount_state saat dialog dibuka (mode='percent', percent=15).
        """
        from src.ui.discount import DiscountPopup
        state = {"mode": "percent", "percent": 15, "nominal_input": 0}
        dialog = DiscountPopup(parent=None, discount_state=state, apply_callback=MagicMock())
        qtbot.addWidget(dialog)
        assert dialog.percent_input.text() == "15"

    def test_popup_menampilkan_nilai_nominal_yang_ada(self, qtbot):
        """
        Memastikan DiscountPopup mengisi nominal_input dengan nilai dari
        discount_state saat dialog dibuka (mode='nominal', nominal=25000).
        """
        from src.ui.discount import DiscountPopup
        state = {"mode": "nominal", "percent": 0, "nominal_input": 25000}
        dialog = DiscountPopup(parent=None, discount_state=state, apply_callback=MagicMock())
        qtbot.addWidget(dialog)
        # Format nominal menggunakan titik sebagai separator ribuan
        assert "25" in dialog.nominal_input.text()


# ===========================================================================
# SECTION 14: TEST — WidgetKecil (komponen input reusable di barang_baru.py)
# ===========================================================================

class TestWidgetKecil:
    """Test untuk class WidgetKecil yang digunakan sebagai form input."""

    @pytest.fixture
    def widget_kecil(self, qtbot):
        """Fixture untuk WidgetKecil."""
        from src.ui.barang_baru import WidgetKecil
        widget = WidgetKecil("", "Label Test", "Placeholder Test")
        qtbot.addWidget(widget)
        return widget

    def test_widget_terinstansiasi(self, widget_kecil):
        """
        Memastikan WidgetKecil berhasil dibuat dan memiliki atribut data (QLineEdit).
        """
        assert hasattr(widget_kecil, "data")
        assert isinstance(widget_kecil.data, QLineEdit)

    def test_get_data_mengembalikan_teks_yang_diisi(self, qtbot, widget_kecil):
        """
        Memastikan get_data() mengembalikan teks yang diketik user,
        dengan strip whitespace di kedua ujung.
        """
        widget_kecil.data.setText("  Pensil 2B  ")
        result = widget_kecil.get_data()
        assert result == "Pensil 2B"

    def test_get_data_mengembalikan_string_kosong_jika_belum_diisi(self, widget_kecil):
        """
        Memastikan get_data() mengembalikan string kosong jika input belum diisi.
        """
        widget_kecil.data.clear()
        result = widget_kecil.get_data()
        assert result == ""

    def test_placeholder_text_sesuai(self, widget_kecil):
        """
        Memastikan placeholder text pada QLineEdit sesuai dengan yang
        diberikan saat konstruksi WidgetKecil.
        """
        assert widget_kecil.data.placeholderText() == "Placeholder Test"

# ===========================================================================
# SECTION 15: TEST — UserAdministrator & related classes
# ===========================================================================

from PySide6.QtCore import QEvent, QPointF, QRect
from PySide6.QtGui import QMouseEvent, QStandardItemModel
from PySide6.QtWidgets import QStyleOptionViewItem, QTableWidget, QMessageBox
from PySide6.QtTest import QSignalSpy


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
        dialog.kunci_input.setText(" 1234567890 ")
        dialog.role_input.setCurrentText("Super_user")
        data = dialog.get_data()
        assert data == {"id": 2, "nama": "Ujang", "kunci": "1234567890", "role": "Super_user"}

    def test_password_delegate_masking_normal_empty_dan_max12(self, user_admin_module):
        model = QStandardItemModel(1, 1)
        delegate = user_admin_module.PasswordDelegate()
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 100, 30)
        option.widget = None

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

        spy_edit = QSignalSpy(table.edit_requested)
        spy_delete = QSignalSpy(table.delete_requested)

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

        assert len(spy_edit) == 1
        assert len(spy_delete) == 1
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

        with patch.object(widget, "table_data") as mock_table_data:
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
            db.delete_user.side_effect = ValueError("hapus gagal")
            widget._on_hapus_user_by_row(0)
            MockMsg.critical.assert_called_once()

    def test_filter_search_pagination_reset_refresh_shortcut_dan_edge(self, user_admin_widget):
        widget, db, _ = user_admin_widget

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
            widget.refresh_data()
            assert widget.page_input.text() == "1"
            assert widget.search_input.text() == ""
            assert widget.filter_role.currentIndex() == 0
            mock_table_data.assert_called_once()

        with patch.object(widget, "handle_shortcut") as mock_shortcut:
            mock_shortcut()
            mock_shortcut.assert_called_once()

        delattr(widget, "search_input")
        db.get_users_count.return_value = 0
        db.get_users_for_table.return_value = []
        widget.table_data()
        assert widget.pages == 1
        widget.table_user._all_rows = []
