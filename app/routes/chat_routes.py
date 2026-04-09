from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.utils.safe_templates import get_templates
from urllib.parse import quote
from app.services.intent_service import detect_intent, extract_leave_details
from app.services.leave_service import apply_leave
from app.services.bonafide_service import generate_bonafide

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
templates = get_templates(BASE_DIR / "templates")


@router.post("/chat")
def chat(request: Request, message: str = Form(...)):

    username = request.session.get("user")

    intent = detect_intent(message)

    if intent == "leave":
        leave_details = extract_leave_details(message)

        apply_leave(
            username,
            leave_details["reason"],
            leave_details["start_date"],
            leave_details["end_date"],
            raw_message=leave_details["raw_message"],
            leave_category=leave_details["leave_category"],
            time_slot=leave_details["time_slot"],
        )

        return RedirectResponse(
            "/student?msg=Leave applied successfully",
            status_code=303
        )

    elif intent == "bonafide":
        _file_path, message_text = generate_bonafide(username)

        return RedirectResponse(
            f"/student?msg={quote(message_text)}",
            status_code=303
        )

    return RedirectResponse(
        "/student?msg=Sorry, I didn't understand",
        status_code=303
    )
