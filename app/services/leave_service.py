from app.database import get_db

def apply_leave(username, reason, start_date, end_date, raw_message="", leave_category="general", time_slot="full_day"):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO leave_requests (
            username, reason, start_date, end_date, status, raw_message, leave_category, time_slot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (username, reason, start_date, end_date, "pending", raw_message, leave_category, time_slot)
    )

    db.commit()

def approve_leave(leave_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='approved' WHERE id=?",
        (leave_id,)
    )
    db.commit()

def get_all_leaves():
    db = get_db()
    cursor = db.cursor()
    return cursor.execute("SELECT * FROM leave_requests").fetchall()
