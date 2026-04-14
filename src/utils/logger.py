"""
logger.py
─────────
Sistem Error Handling & Logging terpusat untuk aplikasi POS.

Fitur utama:
    1. Centralized Logging — RotatingFileHandler (maks 5 MB, 3 backup)
    2. Error Tracking      — Stack traces lengkap untuk level ERROR/CRITICAL
    3. User-Friendly Msg   — Pemetaan error teknis → pesan bahasa Indonesia
    4. Crash Recovery       — Global exception handler (sys.excepthook)
                              dengan dialog QMessageBox & graceful shutdown

Penggunaan:
    from src.utils.logger import setup_logging, log_error, install_global_exception_handler

    # Di main.py, setelah QApplication dibuat:
    logger = setup_logging()
    install_global_exception_handler()
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Type

from config import APP_DATA_DIR


# ══════════════════════════════════════════════════════════════════════════════
# 1. CENTRALIZED LOGGING SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

# Konfigurasi default
LOG_DIR = os.path.join(APP_DATA_DIR, "logs")
LOG_FILE = "app.log"
LOG_MAX_BYTES = 5 * 1024 * 1024   # 5 MB per file
LOG_BACKUP_COUNT = 3              # Simpan 3 file backup
LOG_FORMAT = "[%(asctime)s] - [%(levelname)s] - [%(name)s] - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Logger utama aplikasi
_app_logger: logging.Logger | None = None


def setup_logging(
    log_dir: str = LOG_DIR,
    log_file: str = LOG_FILE,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Inisialisasi dan konfigurasi sistem logging terpusat.

    Membuat folder ``logs/`` jika belum ada, lalu mendaftarkan:
      - RotatingFileHandler → menulis ke file dengan rotasi otomatis
      - StreamHandler       → output ke console (stdout)

    Args:
        log_dir:  Path folder tempat file log disimpan.
        log_file: Nama file log.
        level:    Level minimum log yang dicatat (default: DEBUG).

    Returns:
        Instance ``logging.Logger`` utama aplikasi.
    """
    global _app_logger

    # Buat direktori log jika belum ada
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, log_file)

    # Formatter yang informatif: [TIMESTAMP] - [LEVEL] - [MODULE] - [PESAN]
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # ── File Handler (rotating) ──────────────────────────────────────────
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # ── Console Handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ── Root Logger ──────────────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Hindari duplikasi handler jika setup_logging dipanggil lebih dari sekali
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    # Logger khusus aplikasi POS
    _app_logger = logging.getLogger("POS")
    _app_logger.setLevel(level)

    _app_logger.info("=" * 60)
    _app_logger.info("Logging system berhasil diinisialisasi")
    _app_logger.info(f"Log file: {log_path}")
    _app_logger.info("=" * 60)

    return _app_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Mendapatkan logger untuk modul tertentu.

    Args:
        name: Nama modul/komponen (misal: 'database', 'ui.transaksi').
              Jika None, mengembalikan logger utama 'POS'.

    Returns:
        Instance ``logging.Logger`` dengan namespace yang sesuai.

    Contoh:
        logger = get_logger("database")
        logger.info("Koneksi berhasil")
        # Output: [2026-04-13 21:00:00] - [INFO] - [POS.database] - Koneksi berhasil
    """
    if name:
        return logging.getLogger(f"POS.{name}")
    return logging.getLogger("POS")


# ══════════════════════════════════════════════════════════════════════════════
# 2. ERROR TRACKING DENGAN STACK TRACES
# ══════════════════════════════════════════════════════════════════════════════

def log_error(
    exception: Exception,
    context: str = "",
    logger: logging.Logger | None = None,
) -> str:
    """
    Mencatat exception beserta stack trace lengkap ke log.

    Fungsi helper ini memastikan setiap error yang dicatat memiliki
    informasi yang cukup untuk debugging:
      - Tipe exception
      - Pesan error asli
      - Stack trace lengkap
      - Konteks tambahan (opsional)

    Args:
        exception: Instance exception yang akan dicatat.
        context:   Deskripsi singkat konteks terjadinya error
                   (misal: "saat menyimpan transaksi").
        logger:    Logger spesifik. Jika None, menggunakan logger utama 'POS'.

    Returns:
        Pesan user-friendly dalam bahasa Indonesia yang bisa langsung
        ditampilkan ke pengguna.

    Contoh:
        try:
            db.save_transaction(data)
        except Exception as e:
            user_msg = log_error(e, context="saat menyimpan transaksi")
            show_error_to_user(user_msg)
    """
    _logger = logger or get_logger()

    # Ambil stack trace lengkap
    tb_str = traceback.format_exception(type(exception), exception, exception.__traceback__)
    full_traceback = "".join(tb_str)

    # Format pesan log
    error_type = type(exception).__name__
    error_msg = str(exception)
    context_info = f" [{context}]" if context else ""

    _logger.error(
        f"Exception{context_info}: {error_type}: {error_msg}\n"
        f"Stack Trace:\n{full_traceback}"
    )

    # Kembalikan pesan user-friendly
    return get_user_friendly_message(exception)


def log_critical(
    exception: Exception,
    context: str = "",
    logger: logging.Logger | None = None,
) -> str:
    """
    Mencatat error level CRITICAL beserta stack trace lengkap.

    Digunakan untuk error fatal yang menyebabkan aplikasi tidak bisa
    melanjutkan operasi normal.

    Args:
        exception: Instance exception yang akan dicatat.
        context:   Deskripsi singkat konteks.
        logger:    Logger spesifik. Jika None, menggunakan logger utama 'POS'.

    Returns:
        Pesan user-friendly dalam bahasa Indonesia.
    """
    _logger = logger or get_logger()

    tb_str = traceback.format_exception(type(exception), exception, exception.__traceback__)
    full_traceback = "".join(tb_str)

    error_type = type(exception).__name__
    error_msg = str(exception)
    context_info = f" [{context}]" if context else ""

    _logger.critical(
        f"FATAL Exception{context_info}: {error_type}: {error_msg}\n"
        f"Stack Trace:\n{full_traceback}"
    )

    return get_user_friendly_message(exception)


# ══════════════════════════════════════════════════════════════════════════════
# 3. USER-FRIENDLY ERROR MESSAGES (Bahasa Indonesia)
# ══════════════════════════════════════════════════════════════════════════════

# Pemetaan nama exception → pesan bahasa Indonesia untuk end-user
_ERROR_MESSAGE_MAP: dict[str, str] = {
    # ── Database / SQLite Errors ─────────────────────────────────────────
    "OperationalError": (
        "Terjadi masalah pada koneksi database. "
        "Pastikan database tersedia dan coba lagi."
    ),
    "IntegrityError": (
        "Data yang Anda masukkan sudah ada atau melanggar aturan database. "
        "Periksa kembali data dan pastikan tidak ada duplikasi."
    ),
    "DatabaseError": (
        "Terjadi kesalahan pada database. "
        "Silakan tutup dan buka kembali aplikasi."
    ),
    "ProgrammingError": (
        "Terjadi kesalahan internal pada query database. "
        "Silakan hubungi admin untuk pengecekan."
    ),
    "DataError": (
        "Format data tidak sesuai dengan yang diharapkan database. "
        "Periksa kembali isian data Anda."
    ),
    "InterfaceError": (
        "Koneksi ke database terputus. "
        "Silakan restart aplikasi dan coba lagi."
    ),

    # ── File / I/O Errors ────────────────────────────────────────────────
    "FileNotFoundError": (
        "File yang dibutuhkan tidak ditemukan. "
        "Pastikan semua file aplikasi tersedia."
    ),
    "PermissionError": (
        "Tidak memiliki izin untuk mengakses file atau folder. "
        "Jalankan aplikasi sebagai Administrator atau periksa hak akses."
    ),
    "IsADirectoryError": (
        "Path yang dituju adalah folder, bukan file. "
        "Periksa konfigurasi path aplikasi."
    ),
    "IOError": (
        "Terjadi kesalahan saat membaca/menulis file. "
        "Pastikan disk tidak penuh dan file tidak terkunci."
    ),
    "OSError": (
        "Terjadi kesalahan pada sistem operasi. "
        "Pastikan disk tidak penuh dan tidak ada masalah perangkat keras."
    ),

    # ── Network / Connection Errors ──────────────────────────────────────
    "ConnectionError": (
        "Koneksi jaringan gagal. "
        "Periksa koneksi internet Anda dan coba lagi."
    ),
    "TimeoutError": (
        "Waktu koneksi telah habis. "
        "Periksa koneksi jaringan dan coba lagi."
    ),
    "ConnectionRefusedError": (
        "Koneksi ditolak oleh server. "
        "Pastikan server aktif dan dapat dijangkau."
    ),

    # ── Value / Type Errors ──────────────────────────────────────────────
    "ValueError": (
        "Data yang dimasukkan tidak valid. "
        "Periksa kembali format dan isian data Anda."
    ),
    "TypeError": (
        "Terjadi kesalahan tipe data internal. "
        "Silakan coba lagi atau hubungi admin."
    ),
    "KeyError": (
        "Terjadi kesalahan: data yang diperlukan tidak ditemukan. "
        "Silakan coba lagi atau hubungi admin."
    ),
    "IndexError": (
        "Terjadi kesalahan: indeks data di luar jangkauan. "
        "Silakan coba lagi atau hubungi admin."
    ),
    "AttributeError": (
        "Terjadi kesalahan internal pada komponen aplikasi. "
        "Silakan restart aplikasi atau hubungi admin."
    ),
    "ZeroDivisionError": (
        "Terjadi kesalahan: perhitungan tidak valid (pembagian dengan nol). "
        "Periksa kembali data numerik yang dimasukkan."
    ),

    # ── Import / Module Errors ───────────────────────────────────────────
    "ImportError": (
        "Modul yang dibutuhkan tidak ditemukan. "
        "Pastikan semua dependensi terinstal dengan benar."
    ),
    "ModuleNotFoundError": (
        "Modul yang dibutuhkan tidak terinstal. "
        "Hubungi admin untuk melakukan instalasi ulang."
    ),

    # ── Memory / System Errors ───────────────────────────────────────────
    "MemoryError": (
        "Memori komputer tidak cukup. "
        "Tutup aplikasi lain yang tidak terpakai dan coba lagi."
    ),
    "RecursionError": (
        "Terjadi kesalahan internal (loop tak terbatas). "
        "Silakan restart aplikasi dan hubungi admin."
    ),
    "SystemError": (
        "Terjadi kesalahan sistem internal. "
        "Silakan restart aplikasi."
    ),
    "RuntimeError": (
        "Terjadi kesalahan saat menjalankan aplikasi. "
        "Silakan coba lagi atau hubungi admin."
    ),

    # ── JWT / Auth Errors ────────────────────────────────────────────────
    "ExpiredSignatureError": (
        "Sesi login Anda telah kadaluarsa. "
        "Silakan login kembali."
    ),
    "InvalidTokenError": (
        "Token login tidak valid. "
        "Silakan login kembali."
    ),
    "DecodeError": (
        "Terjadi kesalahan saat memproses token autentikasi. "
        "Silakan login kembali."
    ),
}

# Pesan default jika tipe error tidak ada di mapping
_DEFAULT_USER_MESSAGE = (
    "Terjadi kesalahan yang tidak terduga pada aplikasi.\n"
    "Silakan coba lagi atau hubungi admin jika masalah berlanjut."
)


def get_user_friendly_message(exception: Exception) -> str:
    """
    Mengubah exception teknis menjadi pesan bahasa Indonesia yang
    mudah dipahami oleh end-user (kasir/pengguna).

    Pencarian dilakukan berdasarkan:
      1. Nama class exception yang tepat (misal: ``OperationalError``)
      2. Nama class parent/base (untuk inheritance)
      3. Pesan default jika tidak ditemukan

    Args:
        exception: Instance exception.

    Returns:
        Pesan error dalam bahasa Indonesia yang ramah pengguna.
    """
    error_type = type(exception).__name__

    # Cek langsung di mapping
    if error_type in _ERROR_MESSAGE_MAP:
        return _ERROR_MESSAGE_MAP[error_type]

    # Cek parent classes (untuk error turunan, misal sqlite3.OperationalError)
    for parent_class in type(exception).__mro__:
        parent_name = parent_class.__name__
        if parent_name in _ERROR_MESSAGE_MAP:
            return _ERROR_MESSAGE_MAP[parent_name]

    return _DEFAULT_USER_MESSAGE


# ══════════════════════════════════════════════════════════════════════════════
# 4. APPLICATION CRASH RECOVERY — GLOBAL EXCEPTION HANDLER
# ══════════════════════════════════════════════════════════════════════════════

def _global_exception_handler(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback,
) -> None:
    """
    Global exception handler yang dipasang ke ``sys.excepthook``.

    Fungsi ini menangkap semua uncaught exceptions dan:
      a. Mencatat error + stack trace ke file log (level CRITICAL).
      b. Menampilkan dialog error (QMessageBox) dengan pesan user-friendly
         dan instruksi untuk menghubungi admin.
      c. TIDAK menutup aplikasi secara paksa — aplikasi tetap berjalan
         agar user bisa menyimpan pekerjaan atau mencoba operasi lain.

    Catatan:
      - ``KeyboardInterrupt`` diabaikan agar Ctrl+C tetap berfungsi normal.
      - Jika QApplication belum tersedia, error hanya dicatat ke log.
    """
    # Abaikan KeyboardInterrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # ── Catat ke log ─────────────────────────────────────────────────────
    logger = get_logger("CrashHandler")

    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    full_traceback = "".join(tb_lines)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.critical(
        f"UNCAUGHT EXCEPTION pada {timestamp}\n"
        f"Type: {exc_type.__name__}\n"
        f"Message: {exc_value}\n"
        f"Stack Trace:\n{full_traceback}"
    )

    # ── Tampilkan dialog error ke user ───────────────────────────────────
    user_message = get_user_friendly_message(exc_value) if isinstance(exc_value, Exception) else _DEFAULT_USER_MESSAGE

    _show_crash_dialog(
        error_type=exc_type.__name__,
        user_message=user_message,
        technical_detail=str(exc_value),
    )


def _show_crash_dialog(
    error_type: str,
    user_message: str,
    technical_detail: str,
) -> None:
    """
    Menampilkan dialog error yang informatif menggunakan QMessageBox.

    Dialog ini dirancang agar:
      - Kasir/pengguna memahami apa yang terjadi (dalam bahasa Indonesia)
      - Ada instruksi jelas untuk langkah selanjutnya
      - Detail teknis disertakan (untuk admin/developer)
      - Aplikasi TIDAK ditutup paksa — user bisa menutup dialog dan
        mencoba melanjutkan pekerjaan

    Args:
        error_type:       Nama tipe exception (misal: ``OperationalError``).
        user_message:     Pesan ramah pengguna dalam bahasa Indonesia.
        technical_detail: Detail teknis mentah dari exception.
    """
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        from PySide6.QtGui import QIcon

        app = QApplication.instance()
        if app is None:
            # QApplication belum ada — tidak bisa menampilkan dialog GUI
            print(f"[CRITICAL ERROR] {error_type}: {technical_detail}", file=sys.stderr)
            return

        # Buat dialog error
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("⚠ Terjadi Kesalahan — Barokah POS")

        # Pesan utama (user-friendly)
        msg_box.setText(
            "<b style='font-size: 14px; color: #d93025;'>"
            "Terjadi Kesalahan Pada Aplikasi"
            "</b>"
        )

        # Pesan informatif (penjelasan & instruksi)
        informative_text = (
            f"{user_message}\n\n"
            f"──────────────────────────────────\n"
            f"Jika masalah ini terus terjadi:\n"
            f"  1. Catat pesan error di bawah ini\n"
            f"  2. Hubungi Admin / IT Support\n"
            f"  3. Restart aplikasi jika diperlukan\n"
            f"──────────────────────────────────"
        )
        msg_box.setInformativeText(informative_text)

        # Detail teknis (bisa di-expand oleh admin)
        detail_text = (
            f"Error Type : {error_type}\n"
            f"Detail     : {technical_detail}\n"
            f"Waktu      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Log File   : {os.path.join(LOG_DIR, LOG_FILE)}\n"
        )
        msg_box.setDetailedText(detail_text)

        # Styling dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 12px;
                min-width: 400px;
            }
            QPushButton {
                background-color: #d93025;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e04030;
            }
            QPushButton:pressed {
                background-color: #b5271e;
            }
        """)

        # Tombol: OK (tutup dialog, TIDAK menutup aplikasi)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("Mengerti")

        msg_box.exec()

    except Exception as dialog_error:
        # Jika dialog sendiri gagal, fallback ke stderr
        print(
            f"[CRITICAL ERROR] Gagal menampilkan dialog error:\n"
            f"  Original: {error_type}: {technical_detail}\n"
            f"  Dialog Error: {dialog_error}",
            file=sys.stderr,
        )


def install_global_exception_handler() -> None:
    """
    Memasang global exception handler ke ``sys.excepthook``.

    Harus dipanggil **setelah** ``QApplication`` diinisialisasi dan
    **setelah** ``setup_logging()`` dipanggil, agar:
      - Log file sudah siap menerima catatan error
      - QMessageBox bisa ditampilkan ke user

    Contoh integrasi di ``main.py``::

        app = QApplication([])
        setup_logging()
        install_global_exception_handler()
        ...
        sys.exit(app.exec())
    """
    sys.excepthook = _global_exception_handler

    logger = get_logger()
    logger.info("Global exception handler (sys.excepthook) berhasil dipasang")
