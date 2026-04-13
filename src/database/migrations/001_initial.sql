-- +goose Up
-- Membuat tabel konfigurasi aplikasi sebagai contoh awal migrasi
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT UNIQUE NOT NULL,
    key_value TEXT NOT NULL,
    updated_at TEXT DEFAULT (DATETIME('now', 'localtime'))
);

INSERT INTO system_config (key_name, key_value) VALUES ('app_name', 'BarokahCopy POS');

-- +goose Down
-- Menghapus tabel konfigurasi jika di-rollback
DROP TABLE IF EXISTS system_config;
