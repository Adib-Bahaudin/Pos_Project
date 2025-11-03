import sqlite3

class InitDatabase:
    def __init__(self):
        super().__init__()

        self.db_name = "db_BarokahCopy.db"
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
	            "nama_barang" TEXT NOT NULL UNIQUE,
	            "harga_jual" INTEGER NOT NULL,
	            "stok" INTEGER NOT NULL DEFAULT 0,
	            PRIMARY KEY("id" AUTOINCREMENT)
            )
        """)

        cursor.execute("""
            CREATE TABLE "produk_paket" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            CREATE TABLE "transaksi" (
	            "id" INTEGER,
	            "id_customer" INTEGER DEFAULT 1,
	            "total"	INTEGER DEFAULT 0,
	            "tanggal" INTEGER DEFAULT (DATETIME('now', 'localtime')),
	            PRIMARY KEY("id" AUTOINCREMENT)
                FOREIGN KEY("id_customer") REFERENCES "customer"("id")
            )
        """)

        cursor.execute("""
            CREATE TABLE "transaksi_detail" (
	            "id" INTEGER,
	            "id_transaksi" INTEGER NOT NULL,
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
                id_transaksi INTEGER,
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
                SET total = (
                    SELECT SUM(sub_total) 
                    FROM transaksi_detail 
                    WHERE id_transaksi = NEW.id_transaksi
                ) WHERE id = NEW.id_transaksi;
                    
                DELETE FROM laba_transaksi WHERE id_transaksi = NEW.id_transaksi;
                INSERT INTO laba_transaksi (
                    id_transaksi,
                    tanggal,
                    pendapatan_kotor,
                    total_hpp,
                    laba_kotor,
                    pajak_20_persen,
                    laba_bersih
                )
                SELECT 
                    t.id,
                    t.tanggal,
                    t.total as pendapatan_kotor,
                    COALESCE(SUM(
                        CASE
                            WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0)
                            WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0)) FROM detail_paket dp LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan WHERE dp.id_paket = td.id_produk), 0)
                        END
                    ), 0) as total_hpp,
                    t.total - COALESCE(SUM(
                        CASE
                            WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0)
                            WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0)) FROM detail_paket dp LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan WHERE dp.id_paket = td.id_produk), 0)
                        END
                    ), 0) as laba_kotor,
                    CAST((t.total - COALESCE(SUM(
                        CASE
                            WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0)
                            WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0)) FROM detail_paket dp LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan WHERE dp.id_paket = td.id_produk), 0)
                        END
                    ), 0)) * 0.2 AS INTEGER) as pajak_20_persen,
                    (t.total - COALESCE(SUM(
                        CASE
                            WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0) 
                            WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0)) FROM detail_paket dp LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan WHERE dp.id_paket = td.id_produk), 0)
                        END
                    ), 0)) - CAST((t.total - COALESCE(SUM(
                        CASE
                            WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0)
                            WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0)) FROM detail_paket dp LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan WHERE dp.id_paket = td.id_produk), 0)
                        END
                    ), 0)) * 0.2 AS INTEGER) as laba_bersih
                FROM transaksi t LEFT JOIN transaksi_detail td ON t.id = td.id_transaksi LEFT JOIN harga_beli hb ON td.id_produk = hb.id_satuan AND td.jenis_produk = 'satuan' WHERE t.id = NEW.id_transaksi GROUP BY t.id;
                    
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

        from database import DatabaseManager
        engk = DatabaseManager()
        kunci = engk.hash_key('0987654322')
        cursor.execute("""
            INSERT INTO users (nama, hash_kunci, role) VALUES (?,?,?)
        """,("Adib", kunci, "Super_user"))

        coon.commit()
        coon.close()