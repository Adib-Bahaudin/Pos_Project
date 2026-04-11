from typing import Union

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex, QDate, QMargins
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QTextCharFormat
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QComboBox, 
    QDateEdit, QTableView, QHeaderView
)
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet, QLineSeries, 
    QValueAxis, QBarCategoryAxis
)

from fungsi import CustomCalendar

class KasFlowTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Tanggal", "No. Transaksi", "Tipe", "Jumlah", "Laba"]

    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            col = index.column()
            if col == 0:
                return row.get('tanggal', '')
            elif col == 1:
                return row.get('no_transaksi', '')
            elif col == 2:
                return row.get('tipe', '')
            elif col == 3:
                return f"Rp {row.get('jumlah', 0):,.0f}"
            elif col == 4:
                return f"Rp {row.get('laba', 0):,.0f}"
            
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 2:
                tipe = self._data[index.row()].get('tipe', '')
                if tipe == 'Income':
                    return QColor("#00ff00")
                elif tipe == 'Expense':
                    return QColor("#ff0000")
            elif index.column() == 4:
                laba = self._data[index.row()].get('laba', 0)
                if laba > 0:
                    return QColor("#00ff00")
                elif laba < 0:
                    return QColor("#ff0000")

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

class LaporanKasFlow(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_mock_data()

    def _setup_ui(self):
        self.setStyleSheet("background-color: #000000; color: #ffffff;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # 1. Header & Filters
        header_layout = QHBoxLayout()
        
        title_label = QLabel("LAPORAN KAS FLOW")
        title_label.setFont(QFont("Times New Roman", 24, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()

        filter_label = QLabel("Filter:  ")
        filter_label.setFont(QFont("Segoe UI", 12))
        header_layout.addWidget(filter_label)

        self.cb_rentang = QComboBox()
        self.cb_rentang.addItems(["Hari Ini", "Minggu Ini", "Bulan Ini", "Custom"])
        self.cb_rentang.setMinimumWidth(150)
        self.cb_rentang.setFixedHeight(35)
        self.cb_rentang.setStyleSheet(self._combo_style())
        header_layout.addWidget(self.cb_rentang)

        header_layout.addSpacing(20)

        header_format = QTextCharFormat()
        header_format.setBackground(QColor("#2b2b2b"))
        header_format.setForeground(QColor("#A9B7C6"))

        self.date_start = QDateEdit(QDate.currentDate())
        self.date_start.setCalendarPopup(True)
        self.date_start.setFixedHeight(35)
        self.date_start.setStyleSheet(self._date_style())
        
        cal_start = CustomCalendar()
        cal_start.setHeaderTextFormat(header_format)
        self.date_start.setCalendarWidget(cal_start)
        
        header_layout.addWidget(self.date_start)

        to_label = QLabel(" - ")
        to_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(to_label)

        self.date_end = QDateEdit(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        self.date_end.setFixedHeight(35)
        self.date_end.setStyleSheet(self._date_style())
        
        cal_end = CustomCalendar()
        cal_end.setHeaderTextFormat(header_format)
        self.date_end.setCalendarWidget(cal_end)
        
        header_layout.addWidget(self.date_end)

        main_layout.addLayout(header_layout)

        main_layout.addSpacing(10)

        # 2. Summary Cards
        cards_layout = QHBoxLayout()
        cards_layout.setContentsMargins(20, 0, 20, 0)
        cards_layout.setSpacing(15)

        self.card_pemasukan, self.lbl_pemasukan_val = self._create_card("Total Pemasukan", "Rp 0", "#00ff00")
        self.card_pengeluaran, self.lbl_pengeluaran_val = self._create_card("Total Pengeluaran", "Rp 0", "#ff0000")
        self.card_net, self.lbl_net_val = self._create_card("Saldo Bersih (Net)", "Rp 0", "#00aaff")
        self.card_awal, self.lbl_awal_val = self._create_card("Saldo Awal", "Rp 0", "#ffffff")

        cards_layout.addWidget(self.card_pemasukan)
        cards_layout.addWidget(self.card_pengeluaran)
        cards_layout.addWidget(self.card_net)
        cards_layout.addWidget(self.card_awal)

        main_layout.addLayout(cards_layout)

        main_layout.addSpacing(10)

        # 3. Chart Layout
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        self.chart_view.setMaximumHeight(320)
        self.chart_view.setStyleSheet("background: transparent; border: none;")
        main_layout.addWidget(self.chart_view)

        # 4. Transaction Table
        table_label = QLabel("Detail Transaksi")
        table_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        main_layout.addWidget(table_label)

        self.table_view = QTableView()
        self.table_model = KasFlowTableModel([])
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.verticalHeader().setDefaultSectionSize(30)
        self.table_view.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setStyleSheet(self._table_style())
        
        main_layout.addWidget(self.table_view)

    def _create_card(self, title: str, value: str, value_color: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        
        card.setMaximumHeight(95) 
        
        card.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border: 2px solid #333333;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(card)
        
        layout.setContentsMargins(10, 10, 10, 10)
        
        layout.setSpacing(4) 

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10)) 
        lbl_title.setStyleSheet("color: #aaaaaa; border: none;")
        
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {value_color}; border: none;")

        lbl_comparison = QLabel("vs kemarin: +0%")
        lbl_comparison.setFont(QFont("Segoe UI", 8))
        lbl_comparison.setStyleSheet("color: #777777; border: none;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_comparison)

        return card, lbl_value

    def _update_chart(self):
        chart = QChart()
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setMargins(QMargins(10, 10, 10, 10))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundBrush(QBrush(QColor("#141414")))
        chart.setTitle("Arus Kas 7 Hari Terakhir")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        bar_series = QBarSeries()
        
        set_income = QBarSet("Pemasukan")
        set_income.setColor(QColor("#00aa00"))
        set_income.append([500000, 700000, 450000, 800000, 600000, 950000, 1200000])
        
        set_expense = QBarSet("Pengeluaran")
        set_expense.setColor(QColor("#aa0000"))
        set_expense.append([150000, 200000, 100000, 250000, 150000, 300000, 400000])

        bar_series.append(set_income)
        bar_series.append(set_expense)
        chart.addSeries(bar_series)

        line_series = QLineSeries()
        line_series.setName("Net Cash Flow")
        line_series.setColor(QColor("#00aaff"))
        pen = line_series.pen()
        pen.setWidth(3)
        line_series.setPen(pen)
        net_flows = [350000, 500000, 350000, 550000, 450000, 650000, 800000]
        for i, val in enumerate(net_flows):
            line_series.append(i, val)
        chart.addSeries(line_series)

        categories = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        bar_series.attachAxis(axis_x)
        line_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("Rp %i")
        axis_y.setRange(0, 1500000)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bar_series.attachAxis(axis_y)
        line_series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        chart.legend().setBackgroundVisible(False)

        self.chart_view.setChart(chart)

    def _load_mock_data(self):
        # Memperbarui ringkasan (Mock)
        self.lbl_pemasukan_val.setText("Rp 5.200.000")
        self.lbl_pengeluaran_val.setText("Rp 1.550.000")
        self.lbl_net_val.setText("Rp 3.650.000")
        self.lbl_awal_val.setText("Rp 10.000.000")
        
        # Memperbarui grafik (Mock)
        self._update_chart()

        # Memperbarui tabel (Mock)
        mock_transactions = [
            {"tanggal": "2026-04-11 10:00", "no_transaksi": "TRX-1001", "tipe": "Income", "jumlah": 150000, "laba": 50000},
            {"tanggal": "2026-04-11 11:30", "no_transaksi": "TRX-1002", "tipe": "Expense", "jumlah": -50000, "laba": -50000},
            {"tanggal": "2026-04-11 12:15", "no_transaksi": "TRX-1003", "tipe": "Income", "jumlah": 300000, "laba": 120000},
            {"tanggal": "2026-04-11 14:00", "no_transaksi": "TRX-1004", "tipe": "Expense", "jumlah": -20000, "laba": -20000},
            {"tanggal": "2026-04-11 15:45", "no_transaksi": "TRX-1005", "tipe": "Income", "jumlah": 750000, "laba": 250000},
        ]
        self.table_model = KasFlowTableModel(mock_transactions)
        self.table_view.setModel(self.table_model)
        
    def _combo_style(self) -> str:
        return """
            QComboBox {
                background-color: #1e1e1e; 
                color: white; 
                padding: 4px 8px; /* Padding sedikit lebih lebar agar teks tidak menempel border */
                border: 1px solid #444;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #444;
            }
            /* --- FIX: Menggunakan Ikon Custom --- */
            QComboBox::down-arrow {
                image: url(data/icon_down.svg);
                width: 12px;
                height: 12px;
            }
            /* Styling list dropdown saat Combo Box diklik agar senada */
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                selection-background-color: #0078D7;
            }
        """

    def _date_style(self) -> str:
        return """
            QDateEdit {
                background-color: #1e1e1e; 
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #444;
            }
            /* --- FIX: Menggunakan Ikon Custom --- */
            QDateEdit::down-arrow {
                image: url(data/icon_down.svg);
                width: 12px;  /* Sesuaikan ukuran ikon jika dirasa kurang besar/kecil */
                height: 12px;
            }
            QCalendarWidget QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2b2b2b;
                border-bottom: 1px solid #444;
                min-height: 30px;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
                font-weight: bold;
                padding: 4px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #555;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item {
                background-color: transparent;
                color: white;
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QCalendarWidget QTableView {
                background-color: #1e1e1e;
                color: white;
                selection-background-color: #0078D7;
                selection-color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
            }
        """

    def _table_style(self) -> str:
        return """
            QTableView { 
                background-color: #2d2d2d; 
                alternate-background-color: #545454; 
                color: white; 
                border: none; 
                outline: none; 
                font-family: "Segoe UI";
                font-size: 14px;
            }
            QTableView::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QHeaderView::section:horizontal {
                background-color: #a6a6a6;
                color: black; 
                font-weight: bold;
                border: none; 
                padding: 6px; 
                font-family: "Segoe UI";
                font-size: 14px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 150);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(150, 150, 150, 255);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """
