from datetime import datetime, timedelta
import hashlib
import sqlite3
import os
from zoneinfo import ZoneInfo

import jwt

from init_database import InitDatabase

class DatabaseManager:
    def __init__(self, db_name="db_BarokahCopy.db"):

        self.db_name = db_name

        if os.path.exists(self.db_name):
            pass
        else:
            InitDatabase()

    @staticmethod
    def hash_key(key):
        pwd_hash = key
        return hashlib.sha512(pwd_hash.encode()).hexdigest()

    def register_user(self, username, key, role):
        if not key.isdigit() or len(key) != 10:
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
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        hash_key = self.hash_key(key)

        cursor.execute('''
            SELECT id, nama, hash_kunci, role, failed_attempts, locked_until
            FROM users WHERE hash_kunci = ?
        ''', (hash_key,))

        result = cursor.fetchone()

        if not result:
            conn.close()
            return self.failed_login()

        user_id, username, stored_hash, role, failed_attempts, locked_until = result

        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now() < lock_time:
                conn.close()
                return False, f"Akun Anda Terkunci hingga {lock_time.strftime('%H:%M:%S')}"
            else:
                cursor.execute('''
                    UPDATE users SET locked_until = NULL, failed_attempts = 0
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()

        if hash_key == stored_hash:
            cursor.execute('''
                UPDATE users SET locked_until = NULL, failed_attempts = 0
                WHERE id = ?
            ''', (user_id,))

            conn.commit()
            conn.close()
            return True, {"user_id": user_id, "username": username, "role": role}
        else:
            conn.close()
            return self.failed_login()

    def failed_login(self):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        id_tumbal = 1

        cursor.execute('''
            SELECT failed_attempts, locked_until FROM users WHERE id = ?
        ''', (id_tumbal,))

        result = cursor.fetchone()
        failed_attempts = result[0]
        locked_until = result[1]
        failed_attempts += 1

        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now() < lock_time:
                conn.close()
                return False, f"Akun Anda Terkunci hingga {lock_time.strftime('%H:%M:%S')}"
            else:
                cursor.execute('''
                    UPDATE users SET locked_until = NULL, failed_attempts = 0
                    WHERE id = ?
                ''', (id_tumbal,))
                conn.commit()
                failed_attempts = 1

        if failed_attempts >= 5:
            locked_until = datetime.now() + timedelta(minutes=20)
            cursor.execute('''
                           UPDATE users
                           SET failed_attempts = ?, locked_until = ? WHERE id = ?
                           ''', (failed_attempts, locked_until.isoformat(), id_tumbal))
            conn.commit()
            conn.close()
            return False, "Terlalu Banyak Percobaan, Akun Anda Dikunci"
        else:
            cursor.execute('''
                           UPDATE users SET failed_attempts = ? WHERE id = ?
                           ''', (failed_attempts, id_tumbal))
            conn.commit()
            conn.close()
            return False, f"Key Tidak Ditemukan, Sisa Percobaan: {5 - failed_attempts}"

    def session_login(self, userid, nama, role):

        secret_key = "kunci-rahasia-anda-yang-kuat"
        sekarang = datetime.now(ZoneInfo("Asia/Jakarta"))

        payload = {
            'userid': userid,
            'nama': nama,
            'role': role,
            'iat': sekarang.timestamp(),
            'exp': (sekarang + timedelta(minutes=60)).timestamp()
        }
        token_login = jwt.encode(payload,secret_key,algorithm='HS256')

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM sessions
        """)
        conn.commit()

        cursor.execute("""
            INSERT INTO sessions (token) VALUES (?)
        """,(token_login,))
        conn.commit()
        conn.close()

    def verify_session(self):

        secret_key = "kunci-rahasia-anda-yang-kuat"

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT token FROM sessions WHERE id = ?
        """,(1,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return False, "database.py : token tidak ada"

        try:
            token = result[0]
            dekode = jwt.decode(token,secret_key,algorithms=['HS256'])
            return True, {"user_id": dekode['userid'], "username": dekode['nama'], "role": dekode['role']}
        except jwt.ExpiredSignatureError:
            return False, "database.py : token tidak sudah expaired"
        except jwt.InvalidTokenError:
            return False, "database.py : token tidak sudah tidak valid"

    def delete_session(self):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM sessions
        """)

        conn.commit()
        conn.close()