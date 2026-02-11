from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.agents import router as agents_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bank import router as bank_router
from app.api.routes.documents import router as documents_router
from app.api.routes.emails import router as emails_router
from app.api.routes.goals import router as goals_router
from app.api.routes.health import router as health_router
from app.api.routes.journeys import router as journeys_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.perspectives import router as perspectives_router
from app.api.routes.settings import router as settings_router
from app.api.routes.vdbas import router as vdbas_router
from app.api.routes.vibes import router as vibes_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.middleware import RequestIDMiddleware
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connectivity
    async with engine.connect() as conn:
        await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(title="InCube API", version="1.0.0", lifespan=lifespan)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


# Routes
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(organizations_router, prefix="/api")
app.include_router(goals_router, prefix="/api")
app.include_router(journeys_router, prefix="/api")
app.include_router(perspectives_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(bank_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(emails_router, prefix="/api")
app.include_router(vibes_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(vdbas_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
