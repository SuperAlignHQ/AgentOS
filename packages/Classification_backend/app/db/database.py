import ssl
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.config import get_settings
from app.core.logging_config import logger


settings = get_settings()

class Database:
    def __init__(self) -> None:
        
        try:
            # ssl_context = ssl.create_default_context(
            #     cafile="./app/db/ca.pem"
            # )
            # ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=True,
                pool_size=settings.POOL_SIZE,
                max_overflow=settings.MAX_OVERFLOW,
                pool_timeout=settings.POOL_TIMEOUT,
                future=True,
                # connect_args={"ssl": ssl_context}
            )
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            logger.info("Database engine created successfully")

        except Exception as e:
            logger.critical("Failed to create database engine", str(e), exc_info=True)
            raise e

    async def get_session(self):
        """Dependency Injection for FastAPI routes"""

        try:
            async with self.session_factory() as session:
                yield session
        except SQLAlchemyError as e:
            logger.error("Database session error occurred.", str(e), exc_info=True)
            raise e
        except Exception as e:
            logger.exception("Unexpected error in database session")
            raise e
