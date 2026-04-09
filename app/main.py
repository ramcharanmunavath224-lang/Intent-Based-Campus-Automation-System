from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import logging
import traceback
import os
from app.utils.safe_templates import get_templates

from app.models import init_db

# ✅ Clean router imports
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.chat_routes import router as chat_router
from starlette.middleware.sessions import SessionMiddleware
from app.routes.student_routes import router as student_router

# Basic logging configuration
logging.basicConfig(
	filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'asgi.log'),
	level=logging.DEBUG,
	format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logging.getLogger('uvicorn.error').setLevel(logging.DEBUG)
logging.getLogger('uvicorn.access').setLevel(logging.DEBUG)

app = FastAPI(title="Intent-Based Campus Automation", debug=False)

app.add_middleware(SessionMiddleware, secret_key="mysecretkey123")

# ✅ Static & templates - use absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
# use safe templates helper (centralized)
templates = get_templates(os.path.join(BASE_DIR, "templates"))


# Exception-logging middleware: captures traceback + request info to file
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
	try:
		return await call_next(request)
	except Exception:
		tb = traceback.format_exc()
		logging.getLogger('asgi.error').error("Exception on %s %s:\n%s", request.method, request.url, tb)
		trace_path = os.path.join(BASE_DIR, 'asgi_traceback.log')
		with open(trace_path, 'a', encoding='utf-8') as f:
			f.write(f"URL: {request.url}\nMethod: {request.method}\n{tb}\n{'='*80}\n")
		raise

# ✅ Initialize DB
init_db()

# ✅ Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(student_router)
