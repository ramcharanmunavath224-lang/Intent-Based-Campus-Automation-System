import sqlite3

conn = sqlite3.connect("campus.db")
cursor = conn.cursor()

cursor.execute("UPDATE users SET role='admin' WHERE username='dinesh'")

conn.commit()
conn.close()

print("✅ Role updated to admin successfully")