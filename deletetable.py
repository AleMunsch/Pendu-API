import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('drop table wwd')
conn.commit()
conn.close()