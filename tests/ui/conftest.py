"""
==============================================================================
conftest.py — Pusat Fixture untuk Test Suite UI
==============================================================================

Berisi semua @pytest.fixture yang digunakan bersama oleh seluruh file
tes di direktori tests/ui/. Juga menyertakan helper internal _MockNavButton.

Cara menjalankan:
    pytest tests/ui/ -v
==============================================================================
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock, mock_open

# ---------------------------------------------------------------------------
# Pastikan root proyek ada di sys.path agar import ke src/ berfungsi
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


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
