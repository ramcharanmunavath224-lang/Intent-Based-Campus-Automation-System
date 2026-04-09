from pathlib import Path
from urllib.parse import quote

from fastapi.responses import Response
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.safe_templates import get_templates

from app.database import get_db
from app.services.pdf_service import generate_leave_letter_pdf_bytes

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
templates = get_templates(BASE_DIR / "templates")
UPLOADS_DIR = BASE_DIR / "uploads"


@router.get("/student", response_class=HTMLResponse)
def student_page(request: Request):

    if request.session.get("role") != "student":
        return RedirectResponse("/login", status_code=303)

    username = request.session.get("user")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM leave_requests WHERE username=?", (username,))
    leaves = cursor.fetchall()
    cursor.execute(
        """
        SELECT id, title, content, created_at, created_by
        FROM notices
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT 6
        """
    )
    notices = cursor.fetchall()

    msg = request.query_params.get("msg")
    bonafide_path = UPLOADS_DIR / f"{username}_bonafide.pdf"
    bonafide_ready = bonafide_path.exists()

    return templates.TemplateResponse(request, "student.html", {
        "username": username,
        "leaves": leaves,
        "msg": msg,
        "bonafide_ready": bonafide_ready,
        "notices": notices,
    })
            # leaves
@router.post("/student/apply-leave")
def apply_leave(request: Request, reason: str = Form(...), start_date: str = Form(...), end_date: str = Form(...)):

    if request.session.get("role") != "student":
        return RedirectResponse("/login", status_code=303)
    
    db = get_db()
    cursor = db.cursor()    

    cursor.execute(
        """
        INSERT INTO leave_requests (
            username, reason, start_date, end_date, status, raw_message, leave_category, time_slot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (request.session["user"], reason, start_date, end_date, "pending", reason, "general", "full_day")
    )
    db.commit()

    return RedirectResponse("/student?msg=Leave applied successfully", status_code=303)
               # download leave letter
@router.get("/student/download/{leave_id}")
def download_leave_student(request: Request, leave_id: int):

    if request.session.get("role") != "student":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()

    # ✅ SECURE QUERY
    cursor.execute(
        "SELECT * FROM leave_requests WHERE id=? AND username=?",
        (leave_id, request.session["user"])
    )
    leave = cursor.fetchone()

    # ❗ IMPORTANT CHECK
    if not leave:
        return HTMLResponse("Unauthorized or Leave not found", status_code=403)

    if str(leave[5]).strip().lower() != "approved":
        return HTMLResponse("Leave letter is available only after admin approval", status_code=403)

    cursor.execute(
        """
        SELECT full_name, roll_number, department, course, year_semester
        FROM users
        WHERE username = ?
        """,
        (leave[1],)
    )
    student = cursor.fetchone()

    pdf_bytes = generate_leave_letter_pdf_bytes(
        leave_id=leave[0],
        student_username=leave[1],
        full_name=student["full_name"] if student else leave[1],
        roll_number=student["roll_number"] if student else "",
        department=student["department"] if student else "",
        course=student["course"] if student else "",
        year_semester=student["year_semester"] if student else "",
        reason=leave[2],
        start_date=leave[3],
        end_date=leave[4],
        status=leave[5],
    )


    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=leave_{leave_id}.pdf"
        }
    )

           # download_bonafide_student
@router.get("/student/download-bonafide")
def download_bonafide_student(request: Request):

    if request.session.get("role") != "student":
        return RedirectResponse("/login", status_code=303)

    username = request.session.get("user")
    bonafide_path = UPLOADS_DIR / f"{username}_bonafide.pdf"

    if not bonafide_path.exists():
        return RedirectResponse(f"/student?msg={quote('Bonafide not generated yet')}", status_code=303)

    return Response(
        content=bonafide_path.read_bytes(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={username}_bonafide.pdf"
        }
    )
