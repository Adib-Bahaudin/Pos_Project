from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtCore import QSizeF, QMarginsF

class NotaPrinter:
    def __init__(self, printer_name=None):
        self.printer_name = printer_name

    def print_receipt(self, data):
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        if self.printer_name:
            printer.setPrinterName(self.printer_name)
        else:
            # Debug Only
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName("test_nota.pdf")
        
        page_size = QPageSize(QSizeF(58, 200), QPageSize.Unit.Millimeter)
        printer.setPageSize(page_size)
        printer.setPageMargins(QMarginsF(2, 2, 2, 2), QPageLayout.Unit.Millimeter)
        
        doc = QTextDocument()
        
        doc.setPageSize(printer.pageRect(QPrinter.Unit.Point).size())
        doc.setDocumentMargin(0)
        
        header_data = data.get('header', {})
        items = data.get('items', [])
        
        html = """
        <html>
        <head>
        <style>
            body {
                font-family: 'Courier New', Courier, monospace;
                font-size: 5pt;
                color: black;
                margin: 0;
            }
            .center { text-align: center; }
            .bold { font-weight: bold; }
            hr { 
                border-top: 1px dashed black; 
                border-bottom: none; 
                margin: 5px 0; 
            }
        </style>
        </head>
        <body>
            <div class="center bold" style="font-size: 8pt;">STORE HEADER</div>
            <div class="center">Alamat Toko<br>Telp: 08123456789</div>
            <hr>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr><td width="35%">Nomer</td><td width="5%">:</td><td width="60%">""" + str(header_data.get('id', '')) + """</td></tr>
                <tr><td width="35%">Tanggal</td><td width="5%">:</td><td width="60%">""" + str(header_data.get('tanggal', '')) + """</td></tr>
                <tr><td width="35%">Kasir</td><td width="5%">:</td><td width="60%">""" + str(header_data.get('nama_kasir', '')) + """</td></tr>
                <tr><td width="35%">Customer</td><td width="5%">:</td><td width="60%">""" + str(header_data.get('nama_customer', '')) + """</td></tr>
                <tr><td width="35%">Metode</td><td width="5%">:</td><td width="60%">""" + str(header_data.get('metode_bayar', '')) + """</td></tr>
            </table>
            <hr>
            <table width="100%" cellpadding="0" cellspacing="0">
        """
        
        for item in items:
            nama = item.get("nama_barang", "")
            qty = int(item.get("jumlah", 0))
            harga = int(item.get("harga", 0))
            subtotal = qty * harga
            
            html += f"""
                <tr>
                    <td colspan="2" align="left">{nama}</td>
                </tr>
                <tr>
                    <td width="60%" align="left">{qty} x {harga:,}</td>
                    <td width="40%" align="right">{subtotal:,}</td>
                </tr>
            """
            
        html += """
            </table>
            <hr>
            <table width="100%" cellpadding="0" cellspacing="0">
        """
        
        diskon = int(header_data.get('diskon_nominal') or 0)
        biaya = int(header_data.get('pembulatan') or 0)
        total = int(header_data.get('total') or 0)
        
        if diskon > 0:
            html += f"""
                <tr>
                    <td width="50%" align="left">Diskon</td>
                    <td width="50%" align="right">- {diskon:,}</td>
                </tr>
            """
            
        if biaya > 0:
            html += f"""
                <tr>
                    <td width="50%" align="left">Biaya Lain</td>
                    <td width="50%" align="right">{biaya:,}</td>
                </tr>
            """
            
        html += f"""
                <tr>
                    <td width="50%" align="left" class="bold">Total</td>
                    <td width="50%" align="right" class="bold">{total:,}</td>
                </tr>
            </table>
            <hr>
            <div class="center">Terima Kasih Atas<br>Kunjungan Anda</div>
        </body>
        </html>
        """
        
        doc.setHtml(html)
        doc.print_(printer)