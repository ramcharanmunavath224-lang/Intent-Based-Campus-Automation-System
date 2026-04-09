from app.database import get_db
from app.utils.security import hash_password

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        full_name TEXT,
        roll_number TEXT,
        department TEXT,
        course TEXT,
        year_semester TEXT
    )
    """)

    db.commit()

    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    required_columns = {
        "full_name": "TEXT",
        "roll_number": "TEXT",
        "department": "TEXT",
        "course": "TEXT",
        "year_semester": "TEXT",
    }
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")

    db.commit()

    # Default admin user
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():

        hashed_pw = hash_password("admin123")
        cursor.execute(
            """
            INSERT INTO users (username, password, role, full_name, roll_number, department, course, year_semester)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("admin", hashed_pw, "admin", "System Administrator", "", "", "", "")
        )
        db.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        reason TEXT,           
        start_date TEXT,
        end_date TEXT,
        status TEXT,
        raw_message TEXT,
        leave_category TEXT,
        time_slot TEXT
    )""")

    db.commit()

    cursor.execute("PRAGMA table_info(leave_requests)")
    leave_columns = {row[1] for row in cursor.fetchall()}
    required_leave_columns = {
        "raw_message": "TEXT",
        "leave_category": "TEXT",
        "time_slot": "TEXT",
    }
    for column_name, column_type in required_leave_columns.items():
        if column_name not in leave_columns:
            cursor.execute(f"ALTER TABLE leave_requests ADD COLUMN {column_name} {column_type}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        created_by TEXT NOT NULL
    )
    """)

    db.commit()
