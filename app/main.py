from fastapi import FastAPI,APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import router
from app.api.router_get import router as get_router
from app.api.router_midtrans import router as midtrans_router
# from app.admin import init_admin

# Jinja2Templates is at app/core/templates.py — imported by routers directly, no circular import


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup — create all tables from ORM models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown (optional)


app = FastAPI(
    lifespan=lifespan,
    title="PetCare API",
    description="PetCare backend API — authentication via Bearer JWT token",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware — MUST be on app before SQLAdmin mounts /admin,
# so the parent app's middleware handles the session cookie for
# /admin/* paths uniformly (no separate session store on admin.app).
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY_GOOGLE,
    session_cookie="session",
    same_site="lax",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(router)
app.include_router(get_router)
app.include_router(midtrans_router)

# # Init admin — no separate SessionMiddleware on admin.app
# init_admin(app)
