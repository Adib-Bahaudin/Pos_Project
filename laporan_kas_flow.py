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
from database import DatabaseManager

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
        self.db_manager = DatabaseManager()
        self._setup_ui()
        self._connect_signals()
        self._on_filter_changed()

    def _setup_ui(self):
        self.setStyleSheet("background-color: #000000; color: #ffffff;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # 1. Header & Filters
        header_layout = QHBoxLayout()
        
        title_label = QLabel("LAPORAN LABA PENJUALAN")
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
        self.card_pengeluaran, self.lbl_pengeluaran_val = self._create_card("Total HPP", "Rp 0", "#ff0000")
        self.card_net, self.lbl_net_val = self._create_card("Total Pajak", "Rp 0", "#ffcc00")
        self.card_awal, self.lbl_awal_val = self._create_card("Total Laba Bersih", "Rp 0", "#ffffff")

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

    def _connect_signals(self):
        self.cb_rentang.currentIndexChanged.connect(self._on_filter_changed)
        self.date_start.dateChanged.connect(self._on_filter_changed)
        self.date_end.dateChanged.connect(self._on_filter_changed)

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

    def _update_chart(self, daily_data: list[dict]):
        chart = QChart()
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setMargins(QMargins(10, 10, 10, 10))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundBrush(QBrush(QColor("#141414")))
        chart.setTitle("Arus Kas")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        bar_series = QBarSeries()
        
        set_income = QBarSet("Pemasukan")
        set_income.setColor(QColor("#00aa00"))
        
        set_expense = QBarSet("Pengeluaran")
        set_expense.setColor(QColor("#aa0000"))

        categories = []
        max_abs_val = 0
        net_values = []
        for row in daily_data:
            categories.append(row["label"])
            income = row["income"]
            expense = row["expense"]
            net = row["net"]
            set_income.append(income)
            set_expense.append(expense)
            net_values.append(net)
            max_abs_val = max(max_abs_val, income, expense, abs(net))

        bar_series.append(set_income)
        bar_series.append(set_expense)
        chart.addSeries(bar_series)

        line_series = QLineSeries()
        line_series.setName("Net Cash Flow")
        line_series.setColor(QColor("#00aaff"))
        pen = line_series.pen()
        pen.setWidth(3)
        line_series.setPen(pen)
        for i, val in enumerate(net_values):
            line_series.append(i, val)
        chart.addSeries(line_series)

        axis_x = QBarCategoryAxis()
        if not categories:
            categories = ["-"]
            set_income.append(0)
            set_expense.append(0)
            line_series.append(0, 0)
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        bar_series.attachAxis(axis_x)
        line_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("Rp %i")
        axis_y.setRange(0, max(max_abs_val, 1))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bar_series.attachAxis(axis_y)
        line_series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        chart.legend().setBackgroundVisible(False)

        self.chart_view.setChart(chart)

    @staticmethod
    def _to_rupiah(value: int) -> str:
        return f"Rp {value:,.0f}"

    def _get_date_range(self) -> tuple[QDate, QDate]:
        today = QDate.currentDate()
        selected = self.cb_rentang.currentText()

        if selected == "Hari Ini":
            start_date = today
            end_date = today
        elif selected == "Minggu Ini":
            start_date = today.addDays(-(today.dayOfWeek() - 1))
            end_date = start_date.addDays(6)
        elif selected == "Bulan Ini":
            start_date = QDate(today.year(), today.month(), 1)
            end_date = start_date.addMonths(1).addDays(-1)
        else:
            start_date = self.date_start.date()
            end_date = self.date_end.date()

        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return start_date, end_date

    def _sync_date_widgets(self, start_date: QDate, end_date: QDate):
        for widget, value in ((self.date_start, start_date), (self.date_end, end_date)):
            widget.blockSignals(True)
            widget.setDate(value)
            widget.blockSignals(False)

    def _on_filter_changed(self):
        start_date, end_date = self._get_date_range()
        if self.cb_rentang.currentText() != "Custom":
            self._sync_date_widgets(start_date, end_date)
        self._load_data(start_date, end_date)

    def _load_data(self, start_date: QDate, end_date: QDate):
        date_from = start_date.toString("yyyy-MM-dd")
        date_to = end_date.toString("yyyy-MM-dd")
        filter_sql, params = self.db_manager._build_transaction_filter_clauses({
            "date_from": date_from,
            "date_to": date_to
        })

        import sqlite3
        conn = sqlite3.connect(self.db_manager.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT
                t.id AS id_transaksi,
                t.tanggal AS tanggal,
                COALESCE(t.total, 0) AS total_pemasukan,
                COALESCE(l.total_hpp, 0) AS total_pengeluaran,
                COALESCE(l.laba_bersih, 0) AS laba_bersih,
                COALESCE(l.pajak_20_persen, 0) AS pajak_20_persen
            FROM transaksi t
            LEFT JOIN laba_transaksi l ON l.id_transaksi = t.id
            WHERE 1=1 {filter_sql}
            ORDER BY datetime(t.tanggal) DESC
        """, params)
        transactions = [dict(row) for row in cursor.fetchall()]

        cursor.execute(f"""
            SELECT
                date(t.tanggal) AS tanggal,
                COALESCE(SUM(t.total), 0) AS income,
                COALESCE(SUM(l.total_hpp), 0) AS expense,
                COALESCE(SUM(l.laba_bersih), 0) AS net
            FROM transaksi t
            LEFT JOIN laba_transaksi l ON l.id_transaksi = t.id
            WHERE 1=1 {filter_sql}
            GROUP BY date(t.tanggal)
            ORDER BY date(t.tanggal)
        """, params)
        daily_rows = [dict(row) for row in cursor.fetchall()]

        cursor.execute(f"""
            SELECT COALESCE(SUM(COALESCE(l.pajak_20_persen, 0)), 0) AS total_pajak
            FROM transaksi t
            LEFT JOIN laba_transaksi l ON l.id_transaksi = t.id
            WHERE 1=1 {filter_sql}
        """, params)
        total_pajak = int(cursor.fetchone()["total_pajak"])
        conn.close()

        total_pemasukan = sum(int(row["total_pemasukan"]) for row in transactions)
        total_pengeluaran = sum(int(row["total_pengeluaran"]) for row in transactions)
        total_laba_bersih = sum(int(row["laba_bersih"]) for row in transactions)

        self.lbl_pemasukan_val.setText(self._to_rupiah(total_pemasukan))
        self.lbl_pengeluaran_val.setText(self._to_rupiah(total_pengeluaran))
        self.lbl_net_val.setText(self._to_rupiah(total_pajak))
        self.lbl_awal_val.setText(self._to_rupiah(total_laba_bersih))

        table_rows = []
        for row in transactions:
            laba = int(row["laba_bersih"])
            tipe = "Income" if laba >= 0 else "Expense"
            jumlah = int(row["total_pemasukan"]) if tipe == "Income" else -int(row["total_pengeluaran"])
            table_rows.append({
                "tanggal": row["tanggal"],
                "no_transaksi": row["id_transaksi"],
                "tipe": tipe,
                "jumlah": jumlah,
                "laba": laba
            })
        self.table_model = KasFlowTableModel(table_rows)
        self.table_view.setModel(self.table_model)

        grouped_chart_data = []
        for row in daily_rows:
            chart_date = QDate.fromString(row["tanggal"], "yyyy-MM-dd")
            label = chart_date.toString("dd/MM") if chart_date.isValid() else row["tanggal"]
            grouped_chart_data.append({
                "label": label,
                "income": int(row["income"] or 0),
                "expense": int(row["expense"] or 0),
                "net": int(row["net"] or 0),
            })
        self._update_chart(grouped_chart_data)
        
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
