from unittest.mock import patch, MagicMock
import pytest

from PySide6.QtWidgets import QTableView

class TestLaporanKasFlowPage:
    """Kumpulan tes untuk komponen LaporanKasFlow (src/ui/laporan_kas_flow.py)"""

    def test_widget_bisa_dibuat_tanpa_hit_db(self, qtbot):
        with patch("src.ui.laporan_kas_flow.DatabaseManager") as MockDB, \
             patch("src.ui.laporan_kas_flow.LaporanKasFlow._setup_ui") as mock_setup_ui, \
             patch("src.ui.laporan_kas_flow.LaporanKasFlow._connect_signals") as mock_connect, \
             patch("src.ui.laporan_kas_flow.LaporanKasFlow._on_filter_changed") as mock_filter_changed:
            
            from src.ui.laporan_kas_flow import LaporanKasFlow
            widget = LaporanKasFlow()
            qtbot.addWidget(widget)

            assert widget is not None
            assert hasattr(widget, "db_manager")
            MockDB.assert_called_once()
            mock_setup_ui.assert_called_once()
            mock_connect.assert_called_once()
            mock_filter_changed.assert_called_once()

    def test_setup_ui_membangun_komponen_utama(self, qtbot):
        """
        Menguji _setup_ui secara nyata:
        - widget filter & tanggal terbuat
        - cards summary terbuat
        - chart_view terbuat
        - table_view + table_model terpasang
        """
        with patch("src.ui.laporan_kas_flow.DatabaseManager"), \
             patch("src.ui.laporan_kas_flow.LaporanKasFlow._on_filter_changed"):
            from src.ui.laporan_kas_flow import LaporanKasFlow, KasFlowTableModel

            widget = LaporanKasFlow()
            qtbot.addWidget(widget)
            widget.show()

            # 1) Filter area
            assert hasattr(widget, "cb_rentang")
            assert widget.cb_rentang.count() == 4
            assert [widget.cb_rentang.itemText(i) for i in range(widget.cb_rentang.count())] == [
                "Hari Ini", "Minggu Ini", "Bulan Ini", "Custom"
            ]

            assert hasattr(widget, "date_start")
            assert hasattr(widget, "date_end")
            assert widget.date_start.calendarPopup() is True
            assert widget.date_end.calendarPopup() is True

            # 2) Summary cards + label nilai
            for attr in [
                "card_pemasukan", "lbl_pemasukan_val",
                "card_pengeluaran", "lbl_pengeluaran_val",
                "card_net", "lbl_net_val",
                "card_awal", "lbl_awal_val",
            ]:
                assert hasattr(widget, attr), f"{attr} harus terbuat di _setup_ui"

            assert widget.lbl_pemasukan_val.text() == "Rp 0"
            assert widget.lbl_pengeluaran_val.text() == "Rp 0"
            assert widget.lbl_net_val.text() == "Rp 0"
            assert widget.lbl_awal_val.text() == "Rp 0"

            # 3) Chart view
            assert hasattr(widget, "chart_view")
            assert widget.chart_view.minimumHeight() == 250
            assert widget.chart_view.maximumHeight() == 320

            # 4) Table
            assert hasattr(widget, "table_view")
            assert isinstance(widget.table_view, QTableView)
            assert hasattr(widget, "table_model")
            assert isinstance(widget.table_model, KasFlowTableModel)
            assert widget.table_view.model() is widget.table_model
            assert widget.table_model.rowCount() == 0
            assert widget.table_model.columnCount() == 5