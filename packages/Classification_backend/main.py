"""
Main entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager
import os
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config_manager import ConfigManager
from app.core.exception_handler import AppException, Exceptionhandler
from app.core.logging_config import logger
from app.core.util import UPLOAD_DIR
from app.routes.classification_router import router as classification_router
from app.routes.config_router import router as config_router
from app.routes.org_router import router as org_router
from app.routes.usecase_router import router as usecase_router
from app.routes.audit_router import router as audit_router
from app.routes.user_router import router as user_router


@asynccontextmanager
async def lifecycle(app: FastAPI):
    """
    Application lifespan context manager.
    """
    config = ConfigManager.get_instance()
    try:
        # code to run before startup
        await config.startup()
        yield
        # code to run after startup
    except Exception:
        logger.critical("Application failed during startup", exc_info=True)
    finally:
        # code to run during shutdown
        await config.shutdown()


os.makedirs(UPLOAD_DIR, exist_ok=True)
app = FastAPI(lifespan=lifecycle)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, Exceptionhandler.app_exception_handler)
app.add_exception_handler(Exception, Exceptionhandler.generic_exception_handler)


@app.get("/health")
def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(classification_router)
api_router.include_router(config_router)
api_router.include_router(org_router)
api_router.include_router(usecase_router)
api_router.include_router(user_router)
api_router.include_router(audit_router)

app.include_router(api_router)
