import sqlite3
import json

db = sqlite3.connect('safira.db')
c = db.cursor()

print("--- RECORDS containing DNA ---")
c.execute("SELECT id, library_id, meaning, source_metadata FROM records WHERE meaning LIKE '%DNA%'")
records = c.fetchall()
for r in records:
    print(r)

print("\n--- CATEGORY cat_ee79a6d8 ---")
c.execute("SELECT id, library_id, name, parent_id FROM categories WHERE id='cat_ee79a6d8'")
cat = c.fetchone()
print(cat)

print("\n--- RECORD CATEGORIES ---")
if records:
    rec_id = records[0][0]
    c.execute("SELECT category_id FROM record_categories WHERE record_id=?", (rec_id,))
    print(c.fetchall())
