from PySide6.QtCore import QDate

from src.database.database import DatabaseManager

class ServicesManajemenProduk():
    def __init__(self) -> None:
        super().__init__()
        self.db = DatabaseManager()

    def payloadtambahstok(self, data: dict, text: str) -> dict:
        return {
            "date": QDate.currentDate().toString("yyyy-MM-dd"),
            "category": "Belanja Stok Produk",
            "amount": self.get_total_amount(data),
            "method": "Cash",
            "note": text,
        }

    def get_total_amount(self, data) -> int:
        total_harga = 0

        for i, j in zip(
            data['sku'],
            data['jumlah']
        ):
            result = self.db.get_search_produk(0, i, 1, 0, True)
            _data = result[0]
            harga_beli = int(_data['harga_beli'])
            total_harga = harga_beli * j

        return total_harga
        