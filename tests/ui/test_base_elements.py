"""
==============================================================================
test_base_elements.py — Test Suite untuk Komponen UI Dasar
==============================================================================

Menguji komponen UI yang bersifat reusable atau utility:
  - WelcomeWindow  (src/ui/welcome.py)
  - ErrorWindow    (src/ui/error.py)
  - DialogTitleBar (src/ui/dialog_title_bar.py)
  - BaseTableWidget – diuji melalui ProdukSatuanTable (src/ui/ui_base.py)
  - ActionButton   (src/ui/ui_base.py)
  - WidgetKecil    (src/ui/barang_baru.py)

Fixture global (`welcome_window`, `error_window`, `dialog_title_bar`)
tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit


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
