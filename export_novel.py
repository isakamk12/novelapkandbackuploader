import os
import sqlite3
from pathlib import Path
import re

def sanitize_filename(name):
    # Windowsで使えない文字を_に置換
    return re.sub(r'[\\/:*?"<>|]', "_", name)

def export_backup_to_txt(db_path, output_dir="novel_export"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 作品一覧
    cursor.execute("SELECT _id, title FROM book_table ORDER BY order_num;")
    books = cursor.fetchall()

    base = Path(output_dir)
    base.mkdir(exist_ok=True)

    for book_id, book_title in books:
        # 作品フォルダ
        safe_book_title = sanitize_filename(book_title or f"untitled_{book_id}")
        book_folder = base / safe_book_title
        book_folder.mkdir(parents=True, exist_ok=True)

        # 子要素（章・本文）
        cursor.execute("""
            SELECT title, text_body, order_num
            FROM book_child_table
            WHERE oya_id=?
            ORDER BY order_num;
        """, (book_id,))
        children = cursor.fetchall()

        for i, (title, body, order_num) in enumerate(children, start=1):
            safe_title = sanitize_filename(title.strip() if title else f"no_title_{i}")
            filename = f"{i:03d}_{safe_title}.txt"
            filepath = book_folder / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(body or "")

    conn.close()
    print(f"Export completed → {output_dir}/")

if __name__ == "__main__":
    db_path = "2025-09-12-novel_note.backup"
    export_backup_to_txt(db_path)
