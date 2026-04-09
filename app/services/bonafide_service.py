from app.database import get_db
from app.services.pdf_service import generate_pdf

def generate_bonafide(student):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT username, full_name, roll_number, department, course, year_semester
        FROM users
        WHERE username = ? AND role = 'student'
        """,
        (student,),
    )
    user = cursor.fetchone()

    if not user:
        return None, "Student record not found."

    required_values = {
        "full name": user["full_name"],
        "roll number": user["roll_number"],
        "department": user["department"],
        "course": user["course"],
        "year / semester": user["year_semester"],
    }
    missing_fields = [label for label, value in required_values.items() if not value]
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        return None, f"Bonafide details are missing in admin records: {missing_text}."

    path = generate_pdf(
        user["username"],
        user["full_name"],
        user["roll_number"],
        user["department"],
        user["course"],
        user["year_semester"],
    )
    return path, "Bonafide generated successfully."
