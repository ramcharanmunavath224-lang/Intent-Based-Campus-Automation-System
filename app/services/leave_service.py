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

def update_leave_status(leave_id, status):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status=? WHERE id=?",
        (status, leave_id)
    )
    if cursor.rowcount == 0:
        return False

    db.commit()
    return True


def approve_leave(leave_id):
    return update_leave_status(leave_id, "approved")


def reject_leave(leave_id):
    return update_leave_status(leave_id, "rejected")

def get_all_leaves():
    db = get_db()
    cursor = db.cursor()
    return cursor.execute(
        "SELECT * FROM leave_requests ORDER BY id DESC"
    ).fetchall()
