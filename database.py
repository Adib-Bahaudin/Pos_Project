from datetime import datetime, timedelta
import hashlib
import sqlite3
import os
from zoneinfo import ZoneInfo

import jwt

from init_database import InitDatabase


class DatabaseManager:
    """Manager untuk mengelola database dan operasi autentikasi"""

    # Konstanta
    SECRET_KEY = "kunci-rahasia-anda-yang-kuat"
    TIMEZONE = "Asia/Jakarta"
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 1
    SESSION_DURATION_MINUTES = 60
    KEY_LENGTH = 10
    FALLBACK_USER_ID = 1

    def __init__(self, db_name="db_BarokahCopy.db"):
        self.db_name = db_name

        if not os.path.exists(self.db_name):
            InitDatabase()

        self._ensure_transaction_schema()

    @staticmethod
    def hash_key(key):
        """Menghasilkan hash SHA-512 dari key"""
        pwd_hash = key
        return hashlib.sha512(pwd_hash.encode()).hexdigest()

    def _ensure_transaction_schema(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(transaksi)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {
            "subtotal": "INTEGER DEFAULT 0",
            "diskon_nominal": "INTEGER DEFAULT 0",
            "diskon_persen": "REAL DEFAULT 0",
            "pembulatan": "INTEGER DEFAULT 0",
            "metode_bayar": "TEXT DEFAULT 'Tunai'",
            "nominal_bayar": "INTEGER DEFAULT 0",
            "kembalian": "INTEGER DEFAULT 0",
            "catatan": "TEXT",
            "nama_customer": "TEXT",
            "nama_kasir": "TEXT",
        }

        for column_name, column_type in expected_columns.items():
            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE transaksi ADD COLUMN {column_name} {column_type}"
                )

        cursor.execute("SELECT id FROM customer WHERE nama = ?", ("Pelanggan Umum",))
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO customer (nama, nomer_hp, alamat)
                VALUES (?, ?, ?)
                """,
                ("Pelanggan Umum", "", ""),
            )

        conn.commit()
        conn.close()

    def register_user(self, username, key, role):
        """
        Mendaftarkan user baru ke database

        Args:
            username: Nama pengguna
            key: Kunci akses (harus 10 digit angka)
            role: Role pengguna (admin, user, dll)

        Returns:
            True jika berhasil

        Raises:
            ValueError: Jika validasi gagal atau username/key sudah terdaftar
        """
        if not key.isdigit() or len(key) != self.KEY_LENGTH:
            raise ValueError("Kunci harus Angka dan 10 Digit")

        hash_key = self.hash_key(key)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                           INSERT INTO users (username, h_key, u_role)
                           VALUES (?, ?, ?)
                           ''', (username, hash_key, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError("Nama atau Kunci Sudah Terdaftar")
        finally:
            conn.close()

    def verify_login(self, key):
        """
        Memverifikasi login user dengan key

        Args:
            key: Kunci akses user

        Returns:
            Tuple (bool, dict/str): (True, user_data) jika berhasil,
                                    (False, error_message) jika gagal
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        hash_key = self.hash_key(key)

        cursor.execute('''
                       SELECT id, nama, hash_kunci, role, failed_attempts, locked_until
                       FROM users
                       WHERE hash_kunci = ?
                       ''', (hash_key,))

        result = cursor.fetchone()

        if not result:
            conn.close()
            return self._handle_failed_login()

        user_id, username, stored_hash, role, failed_attempts, locked_until = result

        # Cek apakah akun terkunci
        if locked_until:
            is_locked, message = self._check_account_lock(cursor, user_id, locked_until)
            if is_locked:
                conn.close()
                return False, message

        # Verifikasi hash key
        if hash_key == stored_hash:
            self._reset_failed_attempts(cursor, user_id)
            conn.commit()
            conn.close()
            return True, {"user_id": user_id, "username": username, "role": role}
        else:
            conn.close()
            return self._handle_failed_login()

    def _check_account_lock(self, cursor, user_id, locked_until):
        """
        Mengecek apakah akun masih terkunci

        Returns:
            Tuple (bool, str): (True, message) jika masih terkunci,
                              (False, None) jika sudah tidak terkunci
        """
        lock_time = datetime.fromisoformat(locked_until)

        if datetime.now() < lock_time:
            return True, f"Akun Anda Terkunci hingga {lock_time.strftime('%H:%M:%S')}"
        else:
            self._reset_failed_attempts(cursor, user_id)
            return False, None

    @staticmethod
    def _reset_failed_attempts(cursor, user_id):
        """Reset percobaan login yang gagal dan unlock akun"""
        cursor.execute('''
                       UPDATE users
                       SET locked_until    = NULL,
                           failed_attempts = 0
                       WHERE id = ?
                       ''', (user_id,))

    def _handle_failed_login(self):
        """
        Menangani percobaan login yang gagal

        Returns:
            Tuple (bool, str): (False, error_message)
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        user_id = self.FALLBACK_USER_ID

        cursor.execute('''
                       SELECT failed_attempts, locked_until
                       FROM users
                       WHERE id = ?
                       ''', (user_id,))

        result = cursor.fetchone()
        failed_attempts = result[0]
        locked_until = result[1]
        failed_attempts += 1

        # Cek apakah masih terkunci
        if locked_until:
            is_locked, message = self._check_account_lock(cursor, user_id, locked_until)
            if is_locked:
                conn.close()
                return False, message
            else:
                conn.commit()
                failed_attempts = 1

        # Jika sudah mencapai batas maksimal percobaan
        if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            locked_until = datetime.now() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            cursor.execute('''
                           UPDATE users
                           SET failed_attempts = ?,
                               locked_until    = ?
                           WHERE id = ?
                           ''', (failed_attempts, locked_until.isoformat(), user_id))
            conn.commit()
            conn.close()
            return False, "Terlalu Banyak Percobaan, Akun Anda Dikunci"
        else:
            cursor.execute('''
                           UPDATE users
                           SET failed_attempts = ?
                           WHERE id = ?
                           ''', (failed_attempts, user_id))
            conn.commit()
            conn.close()
            remaining_attempts = self.MAX_FAILED_ATTEMPTS - failed_attempts
            return False, f"Key Tidak Ditemukan, Sisa Percobaan: {remaining_attempts}"

    def session_login(self, user_id, nama, role):
        """
        Membuat session login dengan JWT token

        Args:
            user_id: ID user
            nama: Nama user
            role: Role user
        """
        current_time = datetime.now(ZoneInfo(self.TIMEZONE))

        payload = {
            'userid': user_id,
            'nama': nama,
            'role': role,
            'iat': current_time.timestamp(),
            'exp': (current_time + timedelta(minutes=self.SESSION_DURATION_MINUTES)).timestamp()
        }

        token_login = jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Hapus session lama
        cursor.execute("DELETE FROM sessions")
        conn.commit()

        # Insert session baru
        cursor.execute("INSERT INTO sessions (token) VALUES (?)", (token_login,))
        conn.commit()
        conn.close()

    def verify_session(self):
        """
        Memverifikasi session yang tersimpan

        Returns:
            Tuple (bool, dict/str): (True, user_data) jika valid,
                                    (False, error_message) jika tidak valid
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT token FROM sessions WHERE id = ?", (1,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return False, "database.py : token tidak ada"

        try:
            token = result[0]
            decoded_token = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            return True, {
                "user_id": decoded_token['userid'],
                "username": decoded_token['nama'],
                "role": decoded_token['role']
            }
        except jwt.ExpiredSignatureError:
            return False, "token tidak sudah expaired"
        except jwt.InvalidTokenError:
            return False, "token tidak valid"

    def delete_session(self):
        """Menghapus semua session dari database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions")

        conn.commit()
        conn.close()

    def verify_is_valid(self, jenis, sku, nama, nama_satuan = None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if jenis == "satuan":
            cursor.execute("""
                SELECT 1 FROM produk_satuan WHERE nama_barang = ?
            """, (nama,))
            nama_barang = cursor.fetchone()

            cursor.execute("""
                SELECT 1 FROM produk_satuan WHERE sku = ? 
            """, (sku,))
            sku_barang = cursor.fetchone()

            conn.close()

            is_valid = not (nama_barang or sku_barang)
            return {
                "is_valid": is_valid,
                "nama_barang": nama_barang,
                "sku_barang": sku_barang
            }
        else:
            cursor.execute("""
                SELECT 1 FROM produk_paket WHERE sku = ?
            """, (sku,))

            sku_barang = cursor.fetchone()

            cursor.execute("""
                SELECT 1 FROM produk_paket WHERE nama_paket = ?
            """, (nama,))

            nama_barang = cursor.fetchone()

            cursor.execute("""
                SELECT 1 FROM produk_satuan WHERE nama_barang = ?
            """, (nama_satuan,))

            nama_produk = cursor.fetchone()

            is_valid = nama_produk and (not (sku_barang or nama_barang))
            return {
                "is_valid": is_valid,
                "sku_barang": sku_barang,
                "nama_barang": nama_barang,
                "nama_produk": not nama_produk
            }

    def insert_barang_baru_satuan(self, sku, nama, harga_jual, harga_beli, stok, tanggal):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO produk_satuan (sku, nama_barang, harga_jual, stok, tanggal)
            VALUES (?,?,?,?,?)
        """,(sku, nama, harga_jual, stok, tanggal))

        conn.commit()

        cursor.execute("""
            SELECT id FROM produk_satuan WHERE sku = ?
        """, (sku,))

        result = cursor.fetchone()
        id_barang = result[0]

        cursor.execute("""
            INSERT INTO harga_beli (id_satuan, harga)
            VALUES (?,?)
        """, (id_barang, harga_beli))

        conn.commit()
        conn.close()

    def insert_barang_baru_paket(self, nama, harga_jual, nama_barang, sku, coversion):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO produk_paket (sku, nama_paket, harga_jual) VALUES (?,?,?)
        """, (sku, nama, harga_jual))

        conn.commit()

        cursor.execute("""
            SELECT id FROM produk_satuan WHERE nama_barang = ?
        """, (nama_barang,))

        id_barang = cursor.fetchone()
        id_barang_ = id_barang[0]

        cursor.execute("""
            SELECT id FROM produk_paket WHERE sku = ?
        """, (sku,))

        id_paket = cursor.fetchone()
        id_paket_ = id_paket[0]

        cursor.execute("""
            INSERT INTO detail_paket (id_paket, id_produk, jumlah) VALUES (?,?,?)
        """, (id_paket_, id_barang_, coversion))

        conn.commit()
        conn.close()

    def get_produk_satuan(self, limit=1, offset=0):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                ps.sku,
                ps.nama_barang,
                ps.harga_jual,
                ps.stok AS stock,
                ps.tanggal AS tgl_masuk,
                hb.harga AS harga_beli
            FROM produk_satuan ps
            LEFT JOIN harga_beli hb ON ps.id = hb.id_satuan
            ORDER BY nama_barang ASC 
            LIMIT ? OFFSET ?
        """, (limit, offset))

        result = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return result

    def get_produk_paket(self, limit=1, offset=0):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pp.sku,
                pp.nama_paket AS nama_barang,
                pp.harga_jual,
                dp.jumlah,
                ps.nama_barang AS nama
            FROM produk_paket pp
            LEFT JOIN detail_paket dp ON pp.id = dp.id_paket
            LEFT JOIN produk_satuan ps ON ps.id = dp.id_produk
            ORDER BY nama_barang ASC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        result = [dict(r) for r in cursor.fetchall()]

        for item in result:
            nama = item.get("nama")
            jumlah = item.get("jumlah")
            item["keterangan"] = f"{nama} {jumlah} pcs"

        conn.close()
        return result

    def get_rows_produk(self, index):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if index == 0:
            cursor.execute("""
                SELECT COUNT(*) FROM produk_satuan
            """)

            result = cursor.fetchone()[0]
            return result
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM produk_paket
            """)

            result = cursor.fetchone()[0]
            return result

    def search_products(self, keyword: str, limit: int, filter_index: int = 0):
        keyword = keyword.strip()
        filter_keyword = f"%{keyword}%" if keyword else "%"

        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_parts = []
        params = []

        if filter_index in (0, 1):
            query_parts.append(
                """
                SELECT
                    sku,
                    nama_barang,
                    harga_jual,
                    stok,
                    'satuan' AS tipe
                FROM produk_satuan
                WHERE sku LIKE ? OR nama_barang LIKE ?
                """
            )
            params.extend([filter_keyword, filter_keyword])

        if filter_index in (0, 2):
            query_parts.append(
                """
                SELECT
                    sku,
                    nama_paket AS nama_barang,
                    harga_jual,
                    NULL AS stok,
                    'paket' AS tipe
                FROM produk_paket
                WHERE sku LIKE ? OR nama_paket LIKE ?
                """
            )
            params.extend([filter_keyword, filter_keyword])

        if not query_parts:
            conn.close()
            return []

        final_query = " UNION ALL ".join(query_parts) + " ORDER BY nama_barang ASC, sku ASC LIMIT ?"
        params.append(limit)
        cursor.execute(final_query, params)
        result = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return result

    def save_sale_transaction(self, payload: dict) -> int:
        items = payload.get("items") or []
        if not items:
            raise ValueError("Keranjang kosong, transaksi tidak dapat disimpan.")

        subtotal = int(payload.get("subtotal") or 0)
        diskon_nominal = max(0, int(payload.get("diskon_nominal") or 0))
        diskon_persen = float(payload.get("diskon_persen") or 0)
        pembulatan = int(payload.get("pembulatan") or 0)
        total = max(0, int(payload.get("total") or 0))
        nominal_bayar = max(0, int(payload.get("nominal_bayar") or 0))
        kembalian = int(payload.get("kembalian") or 0)
        metode_bayar = str(payload.get("metode_bayar") or "Tunai").strip() or "Tunai"
        customer_name = str(payload.get("customer_name") or "Pelanggan Umum").strip() or "Pelanggan Umum"
        cashier_name = str(payload.get("cashier_name") or "").strip()
        notes = str(payload.get("notes") or "").strip()

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            customer_id = self._get_or_create_customer(cursor, customer_name)

            cursor.execute(
                """
                INSERT INTO transaksi (
                    id_customer,
                    subtotal,
                    diskon_nominal,
                    diskon_persen,
                    pembulatan,
                    metode_bayar,
                    nominal_bayar,
                    kembalian,
                    catatan,
                    nama_customer,
                    nama_kasir,
                    total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    subtotal,
                    diskon_nominal,
                    diskon_persen,
                    pembulatan,
                    metode_bayar,
                    nominal_bayar,
                    kembalian,
                    notes,
                    customer_name,
                    cashier_name,
                    total,
                ),
            )
            transaction_id = cursor.lastrowid

            for item in items:
                product_type = str(item.get("tipe") or "").strip().lower()
                product_id = self._get_product_id_by_sku(cursor, product_type, item.get("sku"))
                qty = max(1, int(item.get("qty") or 1))
                price = max(0, int(item.get("harga_jual") or 0))

                cursor.execute(
                    """
                    INSERT INTO transaksi_detail (
                        id_transaksi,
                        jenis_produk,
                        id_produk,
                        jumlah,
                        harga
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (transaction_id, product_type, product_id, qty, price),
                )

            cursor.execute(
                """
                UPDATE transaksi
                SET subtotal = ?,
                    diskon_nominal = ?,
                    diskon_persen = ?,
                    pembulatan = ?,
                    metode_bayar = ?,
                    nominal_bayar = ?,
                    kembalian = ?,
                    catatan = ?,
                    nama_customer = ?,
                    nama_kasir = ?,
                    total = ?
                WHERE id = ?
                """,
                (
                    subtotal,
                    diskon_nominal,
                    diskon_persen,
                    pembulatan,
                    metode_bayar,
                    nominal_bayar,
                    kembalian,
                    notes,
                    customer_name,
                    cashier_name,
                    total,
                    transaction_id,
                ),
            )

            self._recalculate_profit_for_transaction(cursor, transaction_id)

            conn.commit()
            return transaction_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _get_or_create_customer(cursor, customer_name: str):
        cursor.execute("SELECT id FROM customer WHERE nama = ?", (customer_name,))
        result = cursor.fetchone()
        if result:
            return result[0]

        cursor.execute(
            """
            INSERT INTO customer (nama, nomer_hp, alamat)
            VALUES (?, ?, ?)
            """,
            (customer_name, "", ""),
        )
        return cursor.lastrowid

    @staticmethod
    def _get_product_id_by_sku(cursor, product_type: str, sku: str) -> int:
        if product_type == "satuan":
            cursor.execute("SELECT id FROM produk_satuan WHERE sku = ?", (sku,))
        elif product_type == "paket":
            cursor.execute("SELECT id FROM produk_paket WHERE sku = ?", (sku,))
        else:
            raise ValueError(f"Jenis produk tidak dikenali: {product_type}")

        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"Produk dengan SKU {sku} tidak ditemukan.")

        return int(result[0])

    def _recalculate_profit_for_transaction(self, cursor, transaction_id: int):
        cursor.execute("DELETE FROM laba_transaksi WHERE id_transaksi = ?", (transaction_id,))

        cursor.execute(
            """
            SELECT
                t.id,
                t.tanggal,
                t.total,
                COALESCE(SUM(
                    CASE
                        WHEN td.jenis_produk = 'satuan' THEN td.jumlah * COALESCE(hb.harga, 0)
                        WHEN td.jenis_produk = 'paket' THEN td.jumlah * COALESCE((
                            SELECT SUM(dp.jumlah * COALESCE(hb2.harga, 0))
                            FROM detail_paket dp
                            LEFT JOIN harga_beli hb2 ON dp.id_produk = hb2.id_satuan
                            WHERE dp.id_paket = td.id_produk
                        ), 0)
                    END
                ), 0) AS total_hpp
            FROM transaksi t
            LEFT JOIN transaksi_detail td ON t.id = td.id_transaksi
            LEFT JOIN harga_beli hb
                ON td.id_produk = hb.id_satuan AND td.jenis_produk = 'satuan'
            WHERE t.id = ?
            GROUP BY t.id, t.tanggal, t.total
            """,
            (transaction_id,),
        )
        result = cursor.fetchone()
        if result is None:
            return

        _, tanggal, total, total_hpp = result
        laba_kotor = int(total) - int(total_hpp)
        pajak = int(laba_kotor * 0.2)
        laba_bersih = laba_kotor - pajak

        cursor.execute(
            """
            INSERT INTO laba_transaksi (
                id_transaksi,
                tanggal,
                pendapatan_kotor,
                total_hpp,
                laba_kotor,
                pajak_20_persen,
                laba_bersih
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                tanggal,
                int(total),
                int(total_hpp),
                laba_kotor,
                pajak,
                laba_bersih,
            ),
        )

    def get_search_produk(self, index, keyword, limit=1, offset=0, lock=False):
        keyword = f"%{keyword}%"
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if index == 0:

            if lock:
                where = "WHERE ps.sku LIKE ?"
                params = [keyword, limit, offset]
            else:
                where = "WHERE ps.sku LIKE ? OR ps.nama_barang LIKE ?"
                params = [keyword, keyword, limit, offset]

            cursor.execute(f"""
                SELECT 
                    ps.sku,
                    ps.nama_barang,
                    ps.harga_jual,
                    ps.stok AS stock,
                    ps.tanggal AS tgl_masuk,
                    hb.harga AS harga_beli
                FROM produk_satuan ps
                LEFT JOIN harga_beli hb ON ps.id = hb.id_satuan
                {where}
                ORDER BY nama_barang ASC 
                LIMIT ? OFFSET ?
            """, params)

        else:

            if lock:
                where = "WHERE pp.sku LIKE ?"
                params = [keyword, limit, offset]
            else:
                where = "WHERE pp.sku LIKE ? OR pp.nama_paket LIKE ?"
                params = [keyword, keyword, limit, offset]

            cursor.execute(f"""
                SELECT
                    pp.sku,
                    pp.nama_paket AS nama_barang,
                    pp.harga_jual,
                    dp.jumlah,
                    ps.nama_barang AS nama
                FROM produk_paket pp
                LEFT JOIN detail_paket dp ON pp.id = dp.id_paket
                LEFT JOIN produk_satuan ps ON ps.id = dp.id_produk
                {where}
                ORDER BY nama_barang ASC
                LIMIT ? OFFSET ?
            """, params)

        result = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return result

    def get_search_row(self, index, keyword):
        keyword = f"%{keyword}%"
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if index == 0:
            cursor.execute("""
                SELECT COUNT(*) FROM produk_satuan
                WHERE sku LIKE ? OR nama_barang LIKE ?
            """, (keyword, keyword))

            result = cursor.fetchone()[0]

            conn.close()
            return result
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM produk_paket
                WHERE sku LIKE ? OR nama_paket LIKE ?
            """, (keyword, keyword))

            result = cursor.fetchone()[0]

            conn.close()
            return result

    def get_produk_for_delete(self, jenis, sku):
        """Ambil detail produk berdasarkan jenis dan SKU untuk proses hapus."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if jenis == "satuan":
            cursor.execute("""
                SELECT
                    ps.id,
                    ps.sku,
                    ps.nama_barang,
                    ps.stok,
                    ps.harga_jual,
                    hb.harga AS harga_beli
                FROM produk_satuan ps
                LEFT JOIN harga_beli hb ON hb.id_satuan = ps.id
                WHERE ps.sku = ?
            """, (sku,))
        else:
            cursor.execute("""
                SELECT
                    pp.id,
                    pp.sku,
                    pp.nama_paket AS nama_barang,
                    pp.harga_jual,
                    dp.jumlah,
                    ps.nama_barang AS nama_satuan
                FROM produk_paket pp
                LEFT JOIN detail_paket dp ON pp.id = dp.id_paket
                LEFT JOIN produk_satuan ps ON ps.id = dp.id_produk
                WHERE pp.sku = ?
            """, (sku,))

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not rows:
            return None

        if jenis == "satuan":
            return rows[0]

        item = rows[0]
        nama_satuan = item.get("nama_satuan")
        jumlah = item.get("jumlah")
        item["keterangan"] = f"{nama_satuan} {jumlah} pcs" if nama_satuan and jumlah else "-"
        return item

    def update_produk(self, jenis, sku_lama, data_baru):
        """Update produk satuan/paket berdasarkan SKU lama dengan validasi unik."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        result = {
            "updated": False,
            "error": "",
        }

        try:
            if jenis == "satuan":
                cursor.execute("SELECT id FROM produk_satuan WHERE sku = ?", (sku_lama,))
                row = cursor.fetchone()
                if not row:
                    result["error"] = "Produk tidak ditemukan"
                    conn.rollback()
                    return result

                id_satuan = row[0]

                cursor.execute(
                    "SELECT 1 FROM produk_satuan WHERE nama_barang = ? AND id != ?",
                    (data_baru["nama_barang"], id_satuan),
                )
                if cursor.fetchone():
                    result["error"] = "Nama produk sudah digunakan"
                    conn.rollback()
                    return result

                cursor.execute(
                    "SELECT 1 FROM produk_satuan WHERE sku = ? AND id != ?",
                    (data_baru["sku"], id_satuan),
                )
                if cursor.fetchone():
                    result["error"] = "SKU sudah digunakan"
                    conn.rollback()
                    return result

                cursor.execute(
                    """
                    UPDATE produk_satuan
                    SET sku         = ?,
                        nama_barang = ?,
                        harga_jual  = ?,
                        stok        = ?
                    WHERE id = ?
                    """,
                    (
                        data_baru["sku"],
                        data_baru["nama_barang"],
                        data_baru["harga_jual"],
                        data_baru["stok"],
                        id_satuan,
                    ),
                )

                cursor.execute(
                    "UPDATE harga_beli SET harga = ? WHERE id_satuan = ?",
                    (data_baru["harga_beli"], id_satuan),
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO harga_beli (id_satuan, harga) VALUES (?, ?)",
                        (id_satuan, data_baru["harga_beli"]),
                    )
            else:
                cursor.execute("SELECT id FROM produk_paket WHERE sku = ?", (sku_lama,))
                row = cursor.fetchone()
                if not row:
                    result["error"] = "Produk tidak ditemukan"
                    conn.rollback()
                    return result

                id_paket = row[0]

                cursor.execute(
                    "SELECT 1 FROM produk_paket WHERE nama_paket = ? AND id != ?",
                    (data_baru["nama_barang"], id_paket),
                )
                if cursor.fetchone():
                    result["error"] = "Nama paket sudah digunakan"
                    conn.rollback()
                    return result

                cursor.execute(
                    "SELECT 1 FROM produk_paket WHERE sku = ? AND id != ?",
                    (data_baru["sku"], id_paket),
                )
                if cursor.fetchone():
                    result["error"] = "SKU sudah digunakan"
                    conn.rollback()
                    return result

                cursor.execute(
                    "SELECT id FROM produk_satuan WHERE nama_barang = ?",
                    (data_baru["nama_satuan"],),
                )
                row_satuan = cursor.fetchone()
                if not row_satuan:
                    result["error"] = "Nama satuan tidak ditemukan"
                    conn.rollback()
                    return result

                cursor.execute(
                    """
                    UPDATE produk_paket
                    SET sku        = ?,
                        nama_paket = ?,
                        harga_jual = ?
                    WHERE id = ?
                    """,
                    (
                        data_baru["sku"],
                        data_baru["nama_barang"],
                        data_baru["harga_jual"],
                        id_paket,
                    ),
                )

                cursor.execute(
                    "DELETE FROM detail_paket WHERE id_paket = ?",
                    (id_paket,),
                )
                cursor.execute(
                    "INSERT INTO detail_paket (id_paket, id_produk, jumlah) VALUES (?,?,?)",
                    (id_paket, row_satuan[0], data_baru["jumlah"]),
                )

            conn.commit()
            result["updated"] = True
            return result
        except sqlite3.Error as error:
            conn.rollback()
            result["error"] = str(error)
            return result
        finally:
            conn.close()

    def delete_produk_bersih(self, jenis, sku):
        """
        Hapus produk satuan/paket tanpa mengubah data histori transaksi.

        Catatan:
        - Histori transaksi, laba rugi, dan tabel sejarah lain tidak disentuh.
        - Untuk produk satuan, paket yang berisi produk tersebut ikut dihapus.

        Returns:
            dict: ringkasan hasil penghapusan.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        result = {
            "deleted": False,
            "deleted_produk_paket": 0,
            "deleted_produk_satuan": 0,
            "history_untouched": True,
        }

        try:
            if jenis == "satuan":
                cursor.execute("SELECT id FROM produk_satuan WHERE sku = ?", (sku,))
                row = cursor.fetchone()
                if not row:
                    conn.rollback()
                    return result

                id_satuan = row[0]

                cursor.execute("SELECT id_paket FROM detail_paket WHERE id_produk = ?", (id_satuan,))
                paket_ids = [r[0] for r in cursor.fetchall()]

                if paket_ids:
                    placeholders = ",".join("?" for _ in paket_ids)

                    cursor.execute(f"DELETE FROM detail_paket WHERE id_paket IN ({placeholders})", paket_ids)

                    cursor.execute(f"DELETE FROM produk_paket WHERE id IN ({placeholders})", paket_ids)
                    result["deleted_produk_paket"] = cursor.rowcount

                cursor.execute("DELETE FROM detail_paket WHERE id_produk = ?", (id_satuan,))
                cursor.execute("DELETE FROM harga_beli WHERE id_satuan = ?", (id_satuan,))

                cursor.execute("DELETE FROM produk_satuan WHERE id = ?", (id_satuan,))
                result["deleted_produk_satuan"] = cursor.rowcount
                result["deleted"] = cursor.rowcount > 0
            else:
                cursor.execute("SELECT id FROM produk_paket WHERE sku = ?", (sku,))
                row = cursor.fetchone()
                if not row:
                    conn.rollback()
                    return result

                id_paket = row[0]

                cursor.execute("DELETE FROM detail_paket WHERE id_paket = ?", (id_paket,))

                cursor.execute("DELETE FROM produk_paket WHERE id = ?", (id_paket,))
                result["deleted_produk_paket"] = cursor.rowcount
                result["deleted"] = cursor.rowcount > 0

            conn.commit()
            return result
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()
