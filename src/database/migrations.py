import os
import re
import sqlite3
import shutil
from threading import Lock

from src.utils.logger import get_logger

logger = get_logger("migrations")

class MigrationManager:
    def __init__(self, db_path: str, migrations_dir: str):
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.lock = Lock()
        
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
            
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
            except sqlite3.Error as e:
                logger.error(f"Error initializing schema_version table: {e}")

    _MAX_BACKUPS = 2

    def _backup_database(self):
        """Backup database sebelum menjalankan migrasi apa pun.
        
        Format nama file: {name}_backup_{counter:03d}{ext}
        Contoh: pos_backup_001.db, pos_backup_002.db
        
        Hanya menyimpan maksimal 2 file backup. Jika sudah ada 2,
        file backup paling lama akan dihapus sebelum membuat yang baru.
        """
        if not os.path.exists(self.db_path):
            return

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

        next_counter = (existing_backups[-1][0] + 1) if existing_backups else 1

        while len(existing_backups) >= self._MAX_BACKUPS:
            _, oldest_file = existing_backups.pop(0)
            oldest_path = os.path.join(db_dir, oldest_file)
            try:
                os.remove(oldest_path)
                logger.info(f"Deleted oldest backup: {oldest_path}")
            except OSError as e:
                logger.error(f"Failed to delete old backup {oldest_path}: {e}")

        backup_filename = f"{name}_backup_{next_counter:03d}{ext}"
        backup_path = os.path.join(db_dir, backup_filename)

        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
        except IOError as e:
            logger.error(f"Failed to backup database: {e}")
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
                return [row[0] for row in results]
        except sqlite3.Error as e:
            logger.error(f"Error checking applied migrations: {e}")
            return []
            
    def _get_last_applied_migration(self):
        """Mendapatkan migrasi terakhir yang di-apply."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version, script_name FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                return result
        except sqlite3.Error as e:
            logger.error(f"Error fetching last applied migration: {e}")
            return None

    def migrate(self):
        """Mencari dan menjalankan skrip migrasi yang berstatus pending secara berurutan."""
        with self.lock:
            files = [f for f in os.listdir(self.migrations_dir) if f.endswith('.sql')]
            files.sort()
            
            applied_versions = self._get_applied_migrations()
            pending_migrations = []
            
            for file in files:
                try:
                    version = int(file.split('_')[0])
                    if version not in applied_versions:
                        pending_migrations.append((version, file))
                except ValueError:
                    logger.warning(f"Skipping file {file}: Prefix is not a valid integer.")
                    
            if not pending_migrations:
                logger.info("Database is up to date.")
                return

            logger.info(f"Found {len(pending_migrations)} pending migrations.")
            self._backup_database()

            for version, script_name in pending_migrations:
                filepath = os.path.join(self.migrations_dir, script_name)
                up_script, _ = self._parse_migration_file(filepath)
                
                if not up_script:
                    logger.warning(f"No 'Up' script found in {script_name}. Skipping execution but logging it.")

                logger.info(f"Applying migration: {script_name}...")
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
                except sqlite3.Error as e:
                    logger.error(f"Failed to apply migration {script_name}: {e}")
                    logger.error("Aborting further migrations.")
                    break

    def rollback(self):
        """Membaca skrip migrasi terakhir yang diaplikasikan, dan menjalankan blok Down."""
        with self.lock:
            last_migration = self._get_last_applied_migration()
            if not last_migration:
                logger.info("No migrations to rollback.")
                return

            version, script_name = last_migration
            filepath = os.path.join(self.migrations_dir, script_name)
            
            if not os.path.exists(filepath):
                logger.error(f"Migration file {script_name} not found for rollback.")
                return

            _, down_script = self._parse_migration_file(filepath)
            
            if not down_script:
                logger.warning(f"No 'Down' script found in {script_name}.")

            logger.info(f"Rolling back migration: {script_name}...")
            
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    if down_script:
                        cursor.executescript(down_script)
                    
                    cursor.execute("DELETE FROM schema_version WHERE version = ?", (version,))
                    conn.commit()
                    logger.info(f"Successfully rolled back {script_name}.")
            except sqlite3.Error as e:
                logger.error(f"Failed to rollback migration {script_name}: {e}")
