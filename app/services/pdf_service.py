import os
from datetime import datetime
from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def draw_fitted_center_text(pdf, text, center_x, y, font_name, max_font_size, min_font_size, max_width):
    font_size = max_font_size
    while font_size > min_font_size and stringWidth(text, font_name, font_size) > max_width:
        font_size -= 1
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(center_x, y, text)


def wrap_text(text, font_name, font_size, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        tentative = word if not current_line else f"{current_line} {word}"
        if stringWidth(tentative, font_name, font_size) <= max_width:
            current_line = tentative
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def generate_pdf(student, full_name, roll_number, department, course, year_semester):
    os.makedirs("uploads", exist_ok=True)

    path = f"uploads/{student}_bonafide.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    issue_date = datetime.now().strftime("%d %B %Y")
    certificate_number = f"MIST/BC/{student.upper()}/{datetime.now().strftime('%Y%m%d')}"

    navy = HexColor("#0f172a")
    slate = HexColor("#334155")
    gold = HexColor("#b8891f")
    line = HexColor("#cbd5e1")
    muted = HexColor("#475569")

    c.setTitle("Bonafide Certificate")

    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.rect(34, 34, width - 68, height - 68)
    c.setStrokeColor(line)
    c.setLineWidth(1)
    c.rect(46, 46, width - 92, height - 92)

    c.setFillColor(navy)
    draw_fitted_center_text(
        c,
        "MAHAVEER INSTITUTE OF SCIENCE AND TECHNOLOGY",
        width / 2,
        height - 90,
        "Helvetica-Bold",
        20,
        14,
        width - 120,
    )

    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 110, "Official Student Certificate")

    c.setStrokeColor(gold)
    c.setLineWidth(1.2)
    c.line(96, height - 126, width - 96, height - 126)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 160, "BONAFIDE CERTIFICATE")

    c.setFillColor(muted)
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 205, f"Certificate No: {certificate_number}")
    c.drawRightString(width - 72, height - 205, f"Issue Date: {issue_date}")

    detail_left = 92
    detail_value_x = 220
    detail_top = height - 258
    detail_box_height = 155
    detail_gap = 22
    value_max_width = width - 72 - detail_value_x - 24

    c.setStrokeColor(line)
    c.roundRect(72, height - 400, width - 144, detail_box_height, 14, stroke=1, fill=0)

    detail_y = detail_top
    details = [
        ("Student Username", student),
        ("Full Name", full_name),
        ("Roll Number", roll_number),
        ("Department", department),
        ("Course", course),
        ("Year / Semester", year_semester),
    ]

    for label, value in details:
        c.setFillColor(slate)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(detail_left, detail_y, f"{label}:")
        c.setFillColor(navy)
        c.setFont("Helvetica", 11)
        wrapped_values = wrap_text(str(value), "Helvetica", 11, value_max_width)
        value_y = detail_y
        for line_text in wrapped_values:
            c.drawString(detail_value_x, value_y, line_text)
            value_y -= 14
        detail_y -= max(detail_gap, 14 * len(wrapped_values) + 6)

    c.setFillColor(navy)
    c.setFont("Helvetica", 12)
    body_text = (
        f"This is to certify that Mr./Ms. {full_name}, bearing Roll Number {roll_number}, "
        f"is a bona fide student of {course}, Department of {department}, studying in "
        f"{year_semester} at Mahaveer Institute of Science and Technology. This certificate "
        f"is issued upon the student's request for academic purposes."
    )

    body_y = height - 455
    for line_text in wrap_text(body_text, "Helvetica", 12, width - 150):
        c.drawString(72, body_y, line_text)
        body_y -= 24

    c.setFillColor(muted)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 118, "This is a system-generated bonafide certificate.")

    c.setStrokeColor(slate)
    c.line(width - 210, 150, width - 72, 150)
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width - 182, 132, "Authorized Signatory")
    c.setFont("Helvetica", 10)
    c.drawString(width - 175, 116, "Academic Office")

    c.save()
    return path


def generate_leave_letter_pdf_bytes(
    leave_id,
    student_username,
    full_name,
    roll_number,
    department,
    course,
    year_semester,
    reason,
    start_date,
    end_date,
    status,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    issue_date = datetime.now().strftime("%d %B %Y")
    letter_number = f"MIST/LEAVE/{str(student_username).upper()}/{leave_id:04d}"

    def format_display_date(value):
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").strftime("%d %B %Y")
        except ValueError:
            return str(value)

    formatted_start_date = format_display_date(start_date)
    formatted_end_date = format_display_date(end_date)
    leave_period = (
        formatted_start_date
        if str(start_date) == str(end_date)
        else f"{formatted_start_date} to {formatted_end_date}"
    )

    navy = HexColor("#0f172a")
    slate = HexColor("#334155")
    gold = HexColor("#b8891f")
    line = HexColor("#cbd5e1")
    muted = HexColor("#475569")
    approved_green = HexColor("#166534")
    pending_amber = HexColor("#92400e")
    rejected_red = HexColor("#991b1b")

    status_lower = str(status).strip().lower()
    if status_lower == "approved":
        status_color = approved_green
    elif status_lower == "rejected":
        status_color = rejected_red
    else:
        status_color = pending_amber

    c.setTitle("Leave Letter")

    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.rect(34, 34, width - 68, height - 68)
    c.setStrokeColor(line)
    c.setLineWidth(1)
    c.rect(46, 46, width - 92, height - 92)

    c.setFillColor(navy)
    draw_fitted_center_text(
        c,
        "MAHAVEER INSTITUTE OF SCIENCE AND TECHNOLOGY",
        width / 2,
        height - 90,
        "Helvetica-Bold",
        20,
        14,
        width - 120,
    )

    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 110, "Official Leave Communication")

    c.setStrokeColor(gold)
    c.setLineWidth(1.2)
    c.line(96, height - 126, width - 96, height - 126)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 160, "LEAVE APPROVAL LETTER")

    c.setFillColor(muted)
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 205, f"Letter No: {letter_number}")
    c.drawRightString(width - 72, height - 205, f"Issue Date: {issue_date}")

    detail_left = 92
    detail_value_x = 238
    detail_top = height - 246
    detail_box_height = 158
    detail_gap = 16
    value_max_width = width - 72 - detail_value_x - 24

    c.setStrokeColor(line)
    c.roundRect(72, height - 392, width - 144, detail_box_height, 14, stroke=1, fill=0)

    detail_y = detail_top
    details = [
        ("Student Username", student_username),
        ("Full Name", full_name or "-"),
        ("Roll Number", roll_number or "-"),
        ("Department", department or "-"),
        ("Course", course or "-"),
        ("Year / Semester", year_semester or "-"),
        ("Leave Period", leave_period),
    ]

    for label, value in details:
        c.setFillColor(slate)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(detail_left, detail_y, f"{label}:")
        c.setFillColor(navy)
        c.setFont("Helvetica", 11)
        wrapped_values = wrap_text(str(value), "Helvetica", 11, value_max_width)
        value_y = detail_y
        for line_text in wrapped_values:
            c.drawString(detail_value_x, value_y, line_text)
            value_y -= 14
        detail_y -= max(detail_gap, 14 * len(wrapped_values) + 4)

    c.setFillColor(slate)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(92, height - 450, "Reason for Leave:")

    body_y = height - 474
    c.setFillColor(navy)
    c.setFont("Helvetica", 12)
    for line_text in wrap_text(str(reason), "Helvetica", 12, width - 184):
        c.drawString(92, body_y, line_text)
        body_y -= 18

    body_y -= 12
    formal_text = (
        f"This is to formally certify that the leave request submitted by Mr./Ms. "
        f"{full_name or student_username} for the period from {formatted_start_date} to {formatted_end_date} "
        f"has been reviewed by the institute. The current decision recorded against this "
        f"request is {str(status).title()}."
    )
    for line_text in wrap_text(formal_text, "Helvetica", 12, width - 144):
        c.drawString(72, body_y, line_text)
        body_y -= 22

    status_box_y = 160
    c.setStrokeColor(status_color)
    c.setFillColor(status_color)
    c.roundRect(72, status_box_y, 170, 34, 10, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(88, status_box_y + 12, f"Application Status: {str(status).title()}")

    c.setFillColor(muted)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 118, "This is a system-generated leave letter issued by the academic office.")

    c.setStrokeColor(slate)
    c.line(width - 210, 150, width - 72, 150)
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width - 182, 132, "Authorized Signatory")
    c.setFont("Helvetica", 10)
    c.drawString(width - 175, 116, "Academic Office")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
