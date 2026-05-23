"""
swap_testing.py

Script untuk melakukan swap antara mode Testing dan Production.
Modifikasi yang dilakukan:
  - main.py:
      L308: Menghapus '#' → mengaktifkan baris production
      L309: Menambahkan '#' → menonaktifkan baris testing
  - config.py:
      L12: Menambahkan '# ' → menonaktifkan baris testing
      L13: Menghapus '# ' → mengaktifkan baris production
"""

import os
from pathlib import Path


def modify_line(lines: list[str], line_number: int, action: str) -> None:
    """
    Memodifikasi satu baris dalam list lines.

    Args:
        lines: List dari baris-baris file.
        line_number: Nomor baris (1-indexed).
        action: 'uncomment' untuk menghapus '#', 'comment' untuk menambahkan '#'.
    """
    idx = line_number - 1

    if idx < 0 or idx >= len(lines):
        print(f"  [ERROR] Baris {line_number} di luar jangkauan (total: {len(lines)} baris)")
        return

    original = lines[idx]

    if action == "uncomment":
        if '#' in original:
            pos = original.index('#')
            if pos + 1 < len(original) and original[pos + 1] == ' ':
                new_line = original[:pos] + original[pos + 2:]
            else:
                new_line = original[:pos] + original[pos + 1:]
            lines[idx] = new_line
            print(f"  [OK] Baris {line_number}: Menghapus '#'")
            print(f"        Sebelum : {original.rstrip()}")
            print(f"        Sesudah : {new_line.rstrip()}")
        else:
            print(f"  [SKIP] Baris {line_number}: Tidak ada '#' untuk dihapus")

    elif action == "comment":
        stripped = original.lstrip()
        if stripped.startswith('#'):
            print(f"  [SKIP] Baris {line_number}: Sudah di-comment")
            return
        leading_spaces = original[:len(original) - len(stripped)]
        new_line = leading_spaces + '#' + stripped
        lines[idx] = new_line
        print(f"  [OK] Baris {line_number}: Menambahkan '#'")
        print(f"        Sebelum : {original.rstrip()}")
        print(f"        Sesudah : {new_line.rstrip()}")


def process_file(file_path: str, modifications: list[tuple[int, str]]) -> None:
    """
    Membaca file, menerapkan modifikasi, dan menyimpan kembali.

    Args:
        file_path: Path ke file yang akan dimodifikasi.
        modifications: List dari tuple (line_number, action).
    """
    print(f"\n{'='*60}")
    print(f"Memproses: {file_path}")
    print(f"{'='*60}")

    if not os.path.exists(file_path):
        print(f"  [ERROR] File tidak ditemukan: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_number, action in modifications:
        modify_line(lines, line_number, action)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"  [SAVED] File berhasil disimpan.")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent

    main_py = str(project_root / "main.py")
    config_py = str(project_root / "config.py")

    print("=" * 60)
    print("  SWAP TESTING → PRODUCTION")
    print("=" * 60)

    # Modifikasi main.py
    # L308: uncomment (hapus '#') → aktifkan baris production
    # L309: comment (tambah '#') → nonaktifkan baris testing
    process_file(main_py, [
        (308, "uncomment"),
        (309, "comment"),
    ])

    # Modifikasi config.py
    # L12: comment (tambah '# ') → nonaktifkan baris testing
    # L13: uncomment (hapus '# ') → aktifkan baris production
    process_file(config_py, [
        (12, "comment"),
        (13, "uncomment"),
    ])

    print(f"\n{'='*60}")
    print("  SELESAI! Mode telah di-swap ke PRODUCTION.")
    print("=" * 60)


if __name__ == "__main__":
    main()
