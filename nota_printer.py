from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtCore import QSizeF, QMarginsF

class NotaPrinter:
    def print_receipt(self, data):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)

        #Debug Only
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName("test_nota.pdf")
        
        # Configure HighResolution thermal printer settings
        page_size = QPageSize(QSizeF(58, 200), QPageSize.Unit.Millimeter)
        printer.setPageSize(page_size)
        printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
        
        doc = QTextDocument()
        
        header_data = data.get('header', {})
        items = data.get('items', [])
        
        html = """
        <html>
        <head>
        <style>
            body {
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                color: black;
                margin: 0;
                padding: 10px;
            }
            .center { text-align: center; }
            .right { text-align: right; }
            .bold { font-weight: bold; }
            hr { 
                border-top: 1px dashed black; 
                border-bottom: none; 
                margin: 5px 0; 
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            td { 
                padding: 2px 0; 
                vertical-align: top; 
            }
        </style>
        </head>
        <body>
            <div class="center bold" style="font-size: 11pt;">STORE HEADER</div>
            <div class="center">Alamat Toko<br>Telp: 08123456789</div>
            <hr>
            <table>
                <tr><td style="width: 40%;">ID</td><td>: """ + str(header_data.get('id', '')) + """</td></tr>
                <tr><td>Tanggal</td><td>: """ + str(header_data.get('tanggal', '')) + """</td></tr>
                <tr><td>Kasir</td><td>: """ + str(header_data.get('nama_kasir', '')) + """</td></tr>
                <tr><td>Customer</td><td>: """ + str(header_data.get('nama_customer', '')) + """</td></tr>
                <tr><td>Metode</td><td>: """ + str(header_data.get('metode_bayar', '')) + """</td></tr>
            </table>
            <hr>
            <table>
        """
        
        for item in items:
            nama = item.get("nama_barang", "")
            qty = int(item.get("jumlah", 0))
            harga = int(item.get("harga", 0))
            subtotal = qty * harga
            
            html += f"""
                <tr>
                    <td colspan="2">{nama}</td>
                </tr>
                <tr>
                    <td>{qty} x {harga:,}</td>
                    <td class="right">{subtotal:,}</td>
                </tr>
            """
            
        html += """
            </table>
            <hr>
            <table>
        """
        
        diskon = int(header_data.get('diskon_nominal') or 0)
        biaya = int(header_data.get('pembulatan') or 0)
        total = int(header_data.get('total') or 0)
        
        if diskon > 0:
            html += f"""
                <tr>
                    <td>Diskon</td>
                    <td class="right">- {diskon:,}</td>
                </tr>
            """
            
        if biaya > 0:
            html += f"""
                <tr>
                    <td>Biaya Lain</td>
                    <td class="right">{biaya:,}</td>
                </tr>
            """
            
        html += f"""
                <tr>
                    <td class="bold">Total</td>
                    <td class="right bold">{total:,}</td>
                </tr>
            </table>
            <hr>
            <div class="center">Terima Kasih Atas<br>Kunjungan Anda</div>
        </body>
        </html>
        """
        
        doc.setHtml(html)
        doc.print_(printer)
