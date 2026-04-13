-- +goose Up
-- Menambahkan kolom pengaturan baru
ALTER TABLE system_config ADD COLUMN description TEXT;

-- +goose Down
-- Rollback penambahan kolom (membutuhkan SQLite versi yang mendukung drop column)
ALTER TABLE system_config DROP COLUMN description;
