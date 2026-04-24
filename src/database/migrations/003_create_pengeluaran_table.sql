-- +goose Up
CREATE TABLE pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    kategori TEXT NOT NULL,
    nominal INTEGER NOT NULL,
    metode TEXT NOT NULL,
    catatan TEXT
);

-- +goose Down
DROP TABLE pengeluaran;