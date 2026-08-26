from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.controllers.health_controller import router as health_router
from app.infrastructure.config.settings import get_settings

settings = get_settings()
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
