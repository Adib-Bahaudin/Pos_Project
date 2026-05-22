-- +goose Up
-- Membuat tabel pengeluaran untuk user yang menginstal dari versi awal
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    kategori TEXT NOT NULL,
    nominal INTEGER NOT NULL,
    metode TEXT NOT NULL,
    catatan TEXT
);

-- +goose Down
DROP TABLE pengeluaran;