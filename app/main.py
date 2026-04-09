from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import init_db

# ✅ Clean router imports
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.chat_routes import router as chat_router
from starlette.middleware.sessions import SessionMiddleware
from app.routes.student_routes import router as student_router

app = FastAPI(title="Intent-Based Campus Automation")

app.add_middleware(SessionMiddleware, secret_key="mysecretkey123")

# ✅ Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ Initialize DB
init_db()

# ✅ Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(student_router)
