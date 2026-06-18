from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api.router import router
from app.api.router_get import router as get_router
from fastapi.staticfiles import StaticFiles
from app.admin import init_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
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
