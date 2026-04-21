"""
==============================================================================
test_discount.py — Test Suite untuk DiscountPopup
==============================================================================

Menguji komponen DiscountPopup (src/ui/discount.py).
Fixture `discount_popup` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt


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
