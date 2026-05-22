import os
import re
import sqlite3
import shutil
import time
from threading import Lock

from src.utils.logger import get_logger, log_error, log_critical

logger = get_logger("migrations")

class MigrationManager:
    def __init__(self, db_path: str, migrations_dir: str):
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.lock = Lock()

        logger.info(f"MigrationManager diinisialisasi — db_path='{self.db_path}', migrations_dir='{self.migrations_dir}'")

        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
            logger.info(f"Direktori migrasi dibuat: '{self.migrations_dir}'")

        self._init_schema_table()

    def _get_connection(self):
        """Mendapatkan koneksi ke database sqlite."""
        return sqlite3.connect(self.db_path)

    def _init_schema_table(self):
        """Membuat tabel schema_version jika belum ada."""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS schema_version (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            version INTEGER NOT NULL UNIQUE,
                            script_name TEXT NOT NULL,
                            applied_at TEXT DEFAULT (DATETIME('now','localtime'))
                        )
                    """)
                    conn.commit()
                    logger.debug("Tabel 'schema_version' siap digunakan")
            except sqlite3.Error as e:
                log_critical(e, context="inisialisasi tabel schema_version", logger=logger)

    _MAX_BACKUPS = 2

    def _backup_database(self):
        """Backup database sebelum menjalankan migrasi apa pun.
        
        Format nama file: {name}_backup_{counter:03d}{ext}
        Contoh: pos_backup_001.db, pos_backup_002.db
        
        Hanya menyimpan maksimal 2 file backup. Jika sudah ada 2,
        file backup paling lama akan dihapus sebelum membuat yang baru.
        """
        if not os.path.exists(self.db_path):
            logger.warning(f"Database tidak ditemukan di '{self.db_path}', backup dilewati")
            return

        db_size = os.path.getsize(self.db_path)
        logger.info(f"Memulai backup database '{self.db_path}' (ukuran: {db_size / 1024:.1f} KB)")

        db_dir = os.path.dirname(self.db_path)
        db_filename = os.path.basename(self.db_path)
        name, ext = os.path.splitext(db_filename)

        backup_pattern = re.compile(
            rf"^{re.escape(name)}_backup_(\d{{3}}){re.escape(ext)}$"
        )

        existing_backups = []
        if os.path.isdir(db_dir):
            for f in os.listdir(db_dir):
                match = backup_pattern.match(f)
                if match:
                    counter = int(match.group(1))
                    existing_backups.append((counter, f))

        existing_backups.sort(key=lambda x: x[0])
        logger.debug(
            f"Ditemukan {len(existing_backups)} file backup yang ada: "
            f"{[b[1] for b in existing_backups] if existing_backups else '(kosong)'}"
        )

        next_counter = (existing_backups[-1][0] + 1) if existing_backups else 1

        while len(existing_backups) >= self._MAX_BACKUPS:
            _, oldest_file = existing_backups.pop(0)
            oldest_path = os.path.join(db_dir, oldest_file)
            try:
                os.remove(oldest_path)
                logger.info(f"Backup lama dihapus (melebihi limit {self._MAX_BACKUPS}): '{oldest_path}'")
            except OSError as e:
                log_error(e, context=f"menghapus backup lama '{oldest_path}'", logger=logger)

        backup_filename = f"{name}_backup_{next_counter:03d}{ext}"
        backup_path = os.path.join(db_dir, backup_filename)

        try:
            shutil.copy2(self.db_path, backup_path)
            backup_size = os.path.getsize(backup_path)
            logger.info(
                f"Backup database berhasil dibuat: '{backup_path}' "
                f"(ukuran: {backup_size / 1024:.1f} KB, counter: {next_counter:03d})"
            )
        except IOError as e:
            log_error(e, context=f"membuat backup database ke '{backup_path}'", logger=logger)
            raise

    def _parse_migration_file(self, filepath: str):
        """Membaca script SQL dan memecahnya menjadi bagian 'Up' dan 'Down'."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('-- +goose ')
        up_script = ""
        down_script = ""

        for part in parts:
            if part.strip().lower().startswith('up'):
                up_script = part[len('Up'):].strip()
            elif part.strip().lower().startswith('down'):
                down_script = part[len('Down'):].strip()

        return up_script, down_script

    def _get_applied_migrations(self):
        """Mendapatkan daftar versi migrasi yang sudah diaplikasikan."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM schema_version ORDER BY version ASC")
                results = cursor.fetchall()
                versions = [row[0] for row in results]
                logger.debug(f"Migrasi yang sudah diterapkan: {versions if versions else '(belum ada)'}")
                return versions
        except sqlite3.Error as e:
            log_error(e, context="mengambil daftar migrasi yang sudah diterapkan", logger=logger)
            return []
            
    def _get_last_applied_migration(self):
        """Mendapatkan migrasi terakhir yang di-apply."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version, script_name FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                if result:
                    logger.debug(f"Migrasi terakhir yang diterapkan: v{result[0]} ({result[1]})")
                else:
                    logger.debug("Belum ada migrasi yang diterapkan")
                return result
        except sqlite3.Error as e:
            log_error(e, context="mengambil migrasi terakhir yang diterapkan", logger=logger)
            return None

    def migrate(self):
        """Mencari dan menjalankan skrip migrasi yang berstatus pending secara berurutan."""
        with self.lock:
            logger.info("═" * 50)
            logger.info("MEMULAI PROSES MIGRASI DATABASE")
            logger.info(f"Direktori migrasi: '{self.migrations_dir}'")

            files = [f for f in os.listdir(self.migrations_dir) if f.endswith('.sql')]
            files.sort()
            logger.debug(f"File SQL ditemukan ({len(files)}): {files}")

            applied_versions = self._get_applied_migrations()
            pending_migrations = []

            for file in files:
                try:
                    version = int(file.split('_')[0])
                    if version not in applied_versions:
                        pending_migrations.append((version, file))
                except ValueError:
                    logger.warning(f"File '{file}' dilewati: prefix bukan angka integer yang valid")

            if not pending_migrations:
                logger.info("Database sudah up-to-date, tidak ada migrasi pending")
                logger.info("═" * 50)
                return

            logger.info(
                f"Ditemukan {len(pending_migrations)} migrasi pending: "
                f"{[m[1] for m in pending_migrations]}"
            )
            self._backup_database()

            migrate_start = time.time()
            applied_count = 0
            failed_count = 0

            for version, script_name in pending_migrations:
                filepath = os.path.join(self.migrations_dir, script_name)
                up_script, _ = self._parse_migration_file(filepath)

                if not up_script:
                    logger.warning(
                        f"Blok 'Up' tidak ditemukan di '{script_name}'. "
                        f"Eksekusi SQL dilewati, tetapi versi tetap dicatat."
                    )

                logger.info(f"Menerapkan migrasi v{version}: '{script_name}'...")
                step_start = time.time()

                try:
                    with self._get_connection() as conn:
                        cursor = conn.cursor()
                        if up_script:
                            cursor.executescript(up_script)

                        cursor.execute(
                            "INSERT INTO schema_version (version, script_name) VALUES (?, ?)",
                            (version, script_name)
                        )
                        conn.commit()

                    elapsed = (time.time() - step_start) * 1000
                    applied_count += 1
                    logger.info(f"Migrasi v{version} ('{script_name}') berhasil diterapkan ({elapsed:.0f}ms)")

                except sqlite3.Error as e:
                    failed_count += 1
                    log_error(e, context=f"menerapkan migrasi v{version} ('{script_name}')", logger=logger)
                    logger.error(
                        f"Migrasi dibatalkan pada v{version}. "
                        f"Diterapkan: {applied_count}, Gagal: {failed_count}, "
                        f"Sisa: {len(pending_migrations) - applied_count - failed_count}"
                    )
                    break

            total_elapsed = time.time() - migrate_start
            logger.info(
                f"Proses migrasi selesai — "
                f"berhasil: {applied_count}, gagal: {failed_count}, "
                f"total waktu: {total_elapsed:.2f}s"
            )
            logger.info("═" * 50)

    def rollback(self):
        """Membaca skrip migrasi terakhir yang diaplikasikan, dan menjalankan blok Down."""
        with self.lock:
            logger.info("═" * 50)
            logger.info("MEMULAI PROSES ROLLBACK MIGRASI")

            last_migration = self._get_last_applied_migration()
            if not last_migration:
                logger.info("Tidak ada migrasi yang bisa di-rollback")
                logger.info("═" * 50)
                return

            version, script_name = last_migration
            filepath = os.path.join(self.migrations_dir, script_name)

            if not os.path.exists(filepath):
                logger.error(
                    f"File migrasi '{script_name}' tidak ditemukan di '{self.migrations_dir}' "
                    f"untuk rollback v{version}. Rollback dibatalkan."
                )
                logger.info("═" * 50)
                return

            _, down_script = self._parse_migration_file(filepath)

            if not down_script:
                logger.warning(
                    f"Blok 'Down' tidak ditemukan di '{script_name}'. "
                    f"Eksekusi SQL dilewati, tetapi versi tetap dihapus dari schema_version."
                )

            logger.info(f"Melakukan rollback migrasi v{version}: '{script_name}'...")
            step_start = time.time()

            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    if down_script:
                        cursor.executescript(down_script)

                    cursor.execute("DELETE FROM schema_version WHERE version = ?", (version,))
                    conn.commit()

                elapsed = (time.time() - step_start) * 1000
                logger.info(
                    f"Rollback v{version} ('{script_name}') berhasil ({elapsed:.0f}ms)"
                )
            except sqlite3.Error as e:
                log_error(e, context=f"rollback migrasi v{version} ('{script_name}')", logger=logger)

            logger.info("═" * 50)
