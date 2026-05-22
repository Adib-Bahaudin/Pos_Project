-- +goose Up
-- Menambahkan kolom tip_amount ke tabel transaksi
ALTER TABLE transaksi ADD COLUMN tip_amount INTEGER DEFAULT 0;

-- +goose Down
-- Rollback penambahan kolom (membutuhkan SQLite versi yang mendukung drop column)
ALTER TABLE transaksi DROP COLUMN tip_amount;
