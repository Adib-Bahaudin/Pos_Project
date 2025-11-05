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

    @staticmethod
    def hash_key(key):
        """Menghasilkan hash SHA-512 dari key"""
        pwd_hash = key
        return hashlib.sha512(pwd_hash.encode()).hexdigest()

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
            return False, "database.py : token tidak sudah expaired"
        except jwt.InvalidTokenError:
            return False, "database.py : token tidak sudah tidak valid"

    def delete_session(self):
        """Menghapus semua session dari database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions")

        conn.commit()
        conn.close()