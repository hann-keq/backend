from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import oauth_register_google
from app.api.router import router
from app.api.router_get import router as get_router
from fastapi.staticfiles import StaticFiles
from app.admin import init_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup — create tables + register Google OAuth client
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    oauth_register_google()  # registers oauth.google so /login/google works
    yield
    # shutdown (optional)


app = FastAPI(
    lifespan=lifespan,
    title="PetCare API",
    description="PetCare backend API — authentication via Bearer JWT token",
    version="1.0.0",
)

# Session middleware — REQUIRED by Authlib OAuth for state/CSRF tokens
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY_GOOGLE)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(router)
app.include_router(get_router)

init_admin(app)
