from app.database import get_db
from app.utils.security import hash_password, verify_password


# 🔐 LOGIN (SECURE)
def authenticate_user(username, password):
    db = get_db()
    cursor = db.cursor()

    print("LOGIN ATTEMPT:", username, password)
    cursor.execute(
        "SELECT * FROM users")
    print("ALL USERS:", cursor.fetchall())
    
    cursor.execute(
        "SELECT username, password, role FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user:
        stored_password = user[1]
        print("INPUT PASSWORD:", password)
        print("STORED PASSWORD:", stored_password)
        if verify_password(password, stored_password):
            return {
                "username": user[0],
                "role": user[2]
            }

    return None

# ➕ CREATE USER (ADMIN)
def create_user(
    username,
    password,
    role="student",
    full_name="",
    roll_number="",
    department="",
    course="",
    year_semester="",
):
    db = get_db()
    cursor = db.cursor()

    # ✅ CHECK IF USER ALREADY EXISTS
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()

    if existing:
        return False  # stop if duplicate

    # ✅ HASH PASSWORD
    hashed_pw = hash_password(password)

    # ✅ INSERT USER
    cursor.execute(
        """
        INSERT INTO users (
            username, password, role, full_name, roll_number, department, course, year_semester
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (username, hashed_pw, role, full_name, roll_number, department, course, year_semester)
    )

    db.commit()
    return True


 #  DELETE USER (ADMIN)
def delete_user(username):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    if cursor.rowcount == 0:
        return False # No user deleted      
    db.commit()
    return True


def update_user_details(username, role, full_name, roll_number, department, course, year_semester):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE users
        SET role = ?, full_name = ?, roll_number = ?, department = ?, course = ?, year_semester = ?
        WHERE username = ?
        """,
        (role, full_name, roll_number, department, course, year_semester, username)
    )
    if cursor.rowcount == 0:
        return False

    db.commit()
    return True


def reset_user_password(username, new_password):
    db = get_db()
    cursor = db.cursor()
    hashed_pw = hash_password(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hashed_pw, username)
    )
    if cursor.rowcount == 0:
        return False

    db.commit()
    return True
