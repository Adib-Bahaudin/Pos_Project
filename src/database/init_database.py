import sqlite3

from config import DATABASE_PATH

class InitDatabase:
    def __init__(self):
        super().__init__()

        self.db_name = str(DATABASE_PATH)
        coon = sqlite3.connect(self.db_name)
        cursor = coon.cursor()

        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT UNIQUE NOT NULL,
                hash_kunci TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT "user",
                failed_attempts INTEGER DEFAULT 0,
                locked_until TEXT,
                tanggal_dibuat TEXT DEFAULT (DATETIME('now','localtime'))
            )
        """)

        cursor.execute("""
            CREATE TABLE sessions (
                id INTEGER DEFAULT 1,
                token TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE "produk_satuan" (
	            "id" INTEGER,
                "sku" TEXT NOT NULL UNIQUE,
	            "nama_barang" TEXT NOT NULL UNIQUE,
	            "harga_jual" INTEGER NOT NULL,
	            "stok" INTEGER NOT NULL DEFAULT 0,
                "tanggal" TEXT,
	            PRIMARY KEY("id" AUTOINCREMENT)
            )
        """)

        cursor.execute("""
            CREATE TABLE "produk_paket" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                nama_paket TEXT NOT NULL,
                harga_jual INTEGER NOT NULL
			)
        """)

        cursor.execute("""
            CREATE TABLE detail_paket (
                id_paket INTEGER NOT NULL,
                id_produk INTEGER NOT NULL,
                jumlah INTEGER DEFAULT 1,
                FOREIGN KEY (id_paket) REFERENCES produk_paket(id),
                FOREIGN KEY (id_produk) REFERENCES produk_satuan(id),
                PRIMARY KEY (id_paket, id_produk)
            )
        """)

        cursor.execute("""
            CREATE TABLE harga_beli (
                id_satuan INTEGER NOT NULL,
                harga INTEGER,
                FOREIGN KEY (id_satuan) REFERENCES produk_satuan(id),
                PRIMARY KEY (id_satuan)
			)
        """)

        cursor.execute("""
            CREATE TABLE "customer" (
	            "id" INTEGER,
	            "nama" TEXT NOT NULL UNIQUE,
	            "nomer_hp" TEXT,
	            "alamat" TEXT,
	            "tanggal_dibuat" TEXT NOT NULL DEFAULT (DATETIME('now','localtime')),
	            PRIMARY KEY("id" AUTOINCREMENT)
            )
        """)

        cursor.execute("""
            INSERT INTO customer (nama, nomer_hp, alamat)
            VALUES ('Pelanggan Umum', '', '')
        """)

        cursor.execute("""
            CREATE TABLE "transaksi" (
	            "id" TEXT PRIMARY KEY,
	            "id_customer" INTEGER DEFAULT 1,
                "id_kasir" INTEGER,
                "subtotal" INTEGER DEFAULT 0,
                "diskon_nominal" INTEGER DEFAULT 0,
                "diskon_persen" REAL DEFAULT 0,
                "pembulatan" INTEGER DEFAULT 0,
	            "total"	INTEGER DEFAULT 0,
                "metode_bayar" TEXT,
                "nominal_bayar" INTEGER DEFAULT 0,
                "nominal_kembali" INTEGER DEFAULT 0,
                "catatan" TEXT,
	            "tanggal" TEXT DEFAULT (DATETIME('now', 'localtime')),
                FOREIGN KEY("id_customer") REFERENCES "customer"("id"),
                FOREIGN KEY("id_kasir") REFERENCES "users"("id")
            )
        """)

        cursor.execute("""
            CREATE TABLE "transaksi_detail" (
	            "id" INTEGER,
	            "id_transaksi" TEXT NOT NULL,
	            "jenis_produk" TEXT NOT NULL CHECK("jenis_produk" IN ('satuan', 'paket')),
	            "id_produk"	INTEGER NOT NULL,
	            "jumlah" INTEGER NOT NULL DEFAULT 1,
	            "harga"	INTEGER NOT NULL DEFAULT 0,
	            "sub_total"	INTEGER GENERATED ALWAYS AS ("jumlah" * "harga") STORED,
	            PRIMARY KEY("id" AUTOINCREMENT),
	            FOREIGN KEY("id_transaksi") REFERENCES "transaksi"("id")
            )
        """)

        cursor.execute("""
            CREATE TABLE laba_transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_transaksi TEXT,
                tanggal TEXT,
                pendapatan_kotor INTEGER NOT NULL,
                total_hpp INTEGER NOT NULL,
                laba_kotor INTEGER NOT NULL,
                pajak_20_persen INTEGER NOT NULL,
                laba_bersih INTEGER NOT NULL,
                FOREIGN KEY (id_transaksi) REFERENCES transaksi (id)
            )
        """)

        cursor.execute("""
            CREATE TRIGGER handle_transaksi_detail_insert
            AFTER INSERT ON transaksi_detail
            BEGIN
                UPDATE transaksi_detail
                SET harga = (
                    CASE 
                        WHEN NEW.jenis_produk = 'satuan' THEN
                            (SELECT harga_jual FROM produk_satuan WHERE id = NEW.id_produk)
                        WHEN NEW.jenis_produk = 'paket' THEN
                            (SELECT harga_jual FROM produk_paket WHERE id = NEW.id_produk)
                    END
                    ) WHERE id = NEW.id;
                    
                UPDATE transaksi 
                SET subtotal = (
                    SELECT COALESCE(SUM(sub_total), 0) 
                    FROM transaksi_detail 
                    WHERE id_transaksi = NEW.id_transaksi
                ),
                total = (
                    SELECT COALESCE(SUM(sub_total), 0) 
                    FROM transaksi_detail 
                    WHERE id_transaksi = NEW.id_transaksi
                ) - COALESCE(diskon_nominal, 0) + COALESCE(pembulatan, 0)
                WHERE id = NEW.id_transaksi;
                    
                UPDATE produk_satuan SET stok = stok - NEW.jumlah WHERE id = NEW.id_produk AND NEW.jenis_produk = 'satuan';
                    
                UPDATE produk_satuan SET stok = stok - (
                    SELECT dp.jumlah * NEW.jumlah
                    FROM detail_paket dp
                    WHERE dp.id_paket = NEW.id_produk 
                    AND dp.id_produk = produk_satuan.id
                ) 
                WHERE id IN (
                    SELECT id_produk 
                    FROM detail_paket 
                    WHERE id_paket = NEW.id_produk
                ) AND NEW.jenis_produk = 'paket';
                    
            END;
        """)

        coon.commit()

        from src.database.database import DatabaseManager
        import os
        from dotenv import load_dotenv

        load_dotenv()

        MASTER_KEY=os.getenv("MASTER_KEY")

        engk = DatabaseManager(self.db_name)

        if MASTER_KEY:
            kunci = engk.hash_key(MASTER_KEY)

            cursor.execute("""
            INSERT INTO users (nama, hash_kunci, role) VALUES (?,?,?)
            """,("Adib", kunci, "Super_user"))

            coon.commit()
            coon.close()

        else:
            print("Master Key Tidak ditemukan di file .env")

        
