from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.utils.safe_templates import get_templates

from app.database import get_db
from app.services.auth_service import create_user, delete_user, reset_user_password, update_user_details
from app.services.pdf_service import generate_leave_letter_pdf_bytes

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
templates = get_templates(BASE_DIR / "templates")


@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):

    if not request.session.get("role") == "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()
    search = request.query_params.get("search", "").strip()
    edit_username = request.query_params.get("edit", "").strip()

    if search:
        like_query = f"%{search}%"
        cursor.execute(
            """
            SELECT username, role, full_name, roll_number, department, course, year_semester
            FROM users
            WHERE username LIKE ?
               OR role LIKE ?
               OR COALESCE(full_name, '') LIKE ?
               OR COALESCE(roll_number, '') LIKE ?
               OR COALESCE(department, '') LIKE ?
               OR COALESCE(course, '') LIKE ?
               OR COALESCE(year_semester, '') LIKE ?
            ORDER BY role DESC, username ASC
            """,
            (like_query, like_query, like_query, like_query, like_query, like_query, like_query)
        )
    else:
        cursor.execute(
            """
            SELECT username, role, full_name, roll_number, department, course, year_semester
            FROM users
            ORDER BY role DESC, username ASC
            """
        )
    users = cursor.fetchall()
    notices = cursor.execute(
        """
        SELECT id, title, content, created_at, created_by
        FROM notices
        ORDER BY datetime(created_at) DESC, id DESC
        """
    ).fetchall()
    selected_user = None
    if edit_username:
        cursor.execute(
            """
            SELECT username, role, full_name, roll_number, department, course, year_semester
            FROM users
            WHERE username = ?
            """,
            (edit_username,)
        )
        selected_user = cursor.fetchone()

    msg = request.query_params.get("msg")
    return templates.TemplateResponse(request, "admin.html", {
        "users": users,
        "msg": msg,
        "search": search,
        "selected_user": selected_user,
        "notices": notices,
    })


@router.post("/admin/create-user")
def add_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    full_name: str = Form(""),
    roll_number: str = Form(""),
    department: str = Form(""),
    course: str = Form(""),
    year_semester: str = Form(""),
):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    username = username.strip()
    full_name = full_name.strip()
    roll_number = roll_number.strip()
    department = department.strip()
    course = course.strip()
    year_semester = year_semester.strip()

    if role == "student":
        required_values = [full_name, roll_number, department, course, year_semester]
        if not all(required_values):
            return RedirectResponse("/admin?msg=student_details_required", status_code=303)

    success = create_user(
        username,
        password,
        role,
        full_name,
        roll_number,
        department,
        course,
        year_semester,
    )

    if success:
        return RedirectResponse("/admin?msg=success", status_code=303)
    return RedirectResponse("/admin?msg=Username exists", status_code=303)


@router.post("/admin/update-user")
def update_user(
    request: Request,
    username: str = Form(...),
    role: str = Form(...),
    full_name: str = Form(""),
    roll_number: str = Form(""),
    department: str = Form(""),
    course: str = Form(""),
    year_semester: str = Form(""),
):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    username = username.strip()
    full_name = full_name.strip()
    roll_number = roll_number.strip()
    department = department.strip()
    course = course.strip()
    year_semester = year_semester.strip()

    if role == "student":
        required_values = [full_name, roll_number, department, course, year_semester]
        if not all(required_values):
            return RedirectResponse(
                f"/admin?msg=student_details_required&edit={quote(username)}",
                status_code=303,
            )

    updated = update_user_details(username, role, full_name, roll_number, department, course, year_semester)
    if updated:
        return RedirectResponse(
            f"/admin?msg=user_updated&edit={quote(username)}",
            status_code=303,
        )
    return RedirectResponse("/admin?msg=notfound", status_code=303)


@router.post("/admin/reset-password")
def reset_password(request: Request, username: str = Form(...), new_password: str = Form(...)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    username = username.strip()
    new_password = new_password.strip()
    if not new_password:
        return RedirectResponse(
            f"/admin?msg=password_required&edit={quote(username)}",
            status_code=303,
        )

    reset_done = reset_user_password(username, new_password)
    if reset_done:
        return RedirectResponse(
            f"/admin?msg=password_reset&edit={quote(username)}",
            status_code=303,
        )
    return RedirectResponse("/admin?msg=notfound", status_code=303)


@router.post("/admin/delete-user")
def remove_user(request: Request, username: str = Form(...)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    deleted = delete_user(username)
    if deleted:
        return RedirectResponse("/admin?msg=deleted", status_code=303)
    return RedirectResponse("/admin?msg=notfound", status_code=303)


@router.post("/admin/create-notice")
def create_notice(request: Request, title: str = Form(...), content: str = Form(...)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    title = title.strip()
    content = content.strip()
    if not title or not content:
        return RedirectResponse("/admin?msg=notice_required", status_code=303)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO notices (title, content, created_at, created_by)
        VALUES (?, ?, datetime('now'), ?)
        """,
        (title, content, request.session.get("user", "admin"))
    )
    db.commit()
    return RedirectResponse("/admin?msg=notice_created", status_code=303)


@router.post("/admin/delete-notice")
def delete_notice(request: Request, notice_id: int = Form(...)):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    if cursor.rowcount == 0:
        return RedirectResponse("/admin?msg=notice_missing", status_code=303)

    db.commit()
    return RedirectResponse("/admin?msg=notice_deleted", status_code=303)


@router.get("/admin/leaves", response_class=HTMLResponse)
def view_leaves(request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM leave_requests")
    leaves = cursor.fetchall()

    return templates.TemplateResponse(request, "admin_leaves.html", {"leaves": leaves})


@router.post("/admin/approve-leave")
def approve_leave(request: Request, id: int = Form(...)):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE leave_requests SET status='approved' WHERE id=?", (id,))
    db.commit()

    return RedirectResponse("/admin/leaves", status_code=303)


@router.post("/admin/reject-leave")
def reject_leave(request: Request, id: int = Form(...)):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE leave_requests SET status='rejected' WHERE id=?", (id,))
    db.commit()

    return RedirectResponse("/admin/leaves", status_code=303)


@router.get("/admin/download-leave/{leave_id}")
def download_leave_admin(request: Request, leave_id: int):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login", status_code=303)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM leave_requests WHERE id=?", (leave_id,))
    leave = cursor.fetchone()

    if not leave:
        return HTMLResponse("Leave not found", status_code=404)

    if str(leave[5]).strip().lower() != "approved":
        return HTMLResponse("Leave letter is available only for approved requests", status_code=403)

    cursor.execute(
        """
        SELECT full_name, roll_number, department, course, year_semester
        FROM users
        WHERE username = ?
        """,
        (leave[1],),
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
            "Content-Disposition": f"attachment; filename=admin_leave_{leave_id}.pdf"
        },
    )
