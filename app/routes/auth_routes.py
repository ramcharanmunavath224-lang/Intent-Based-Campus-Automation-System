from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth_service import authenticate_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ✅ root → redirect
@router.get("/")
def home():
    return RedirectResponse(url="/login")

# ✅ login page
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ login logic
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):

    user = authenticate_user(username, password)

    # 👇 ADD THESE LINES HERE
    print("LOGIN ATTEMPT:", username, password)
    print("USER RESULT:", user)

    if user:

        request.session["user"] = user["username"]
        request.session["role"] = user["role"]
        
        if user["role"] == "admin":
            return RedirectResponse("/admin", status_code=303)
        else:
            return RedirectResponse("/student", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid Credentials"}
    )