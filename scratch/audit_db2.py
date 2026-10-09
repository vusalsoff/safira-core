import sqlite3
db = sqlite3.connect('safira.db')
c = db.cursor()
print(c.execute("SELECT category_id FROM record_categories WHERE record_id='rec_11567374'").fetchall())
