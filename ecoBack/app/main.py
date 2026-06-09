from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.reports import router as reports_router
from app.api.v1.rewards import router as rewards_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.admin import router as admin_router

app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
app.include_router(reports_router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["reports"])
app.include_router(rewards_router, prefix=f"{settings.API_V1_PREFIX}/rewards", tags=["rewards"])
app.include_router(notifications_router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["notifications"])
app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])


@app.get("/health")
async def root_health():
    return {"status": "ok", "project": settings.PROJECT_NAME}
