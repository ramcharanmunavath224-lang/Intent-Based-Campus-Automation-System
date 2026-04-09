from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from app.utils.safe_templates import get_templates

from app.models import init_db

# ✅ Clean router imports
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.chat_routes import router as chat_router
from starlette.middleware.sessions import SessionMiddleware
from app.routes.student_routes import router as student_router

app = FastAPI(title="Intent-Based Campus Automation")

app.add_middleware(SessionMiddleware, secret_key="mysecretkey123")

# ✅ Static & templates - use absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
# use safe templates helper (centralized)
templates = get_templates(os.path.join(BASE_DIR, "templates"))

# ✅ Initialize DB
init_db()

# ✅ Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(student_router)
