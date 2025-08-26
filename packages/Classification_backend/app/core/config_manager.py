
from app.core.config import Settings, get_settings
from app.db.database import Database
from app.services.application_service import ApplicationService
from app.services.audit_service import AuditService
from app.services.config_service import ConfigService
from app.services.org_service import OrgService
from app.services.test_service import TestService
from app.core.logging_config import logger
from app.services.usecase_service import UsecaseService
from app.services.user_service import UserService


class ConfigManager:
    _instance = None
    settings = Settings
    database = Database

    def __init__(self) -> None:
        if ConfigManager._instance is not None:
            raise Exception("Use get_instance to get an instance of ConfigManager")

        self.settings = get_settings()
        self.database = Database()
        self._test_service = TestService.get_instance()
        self._application_service = ApplicationService.get_instance()
        self._config_service = ConfigService.get_instance()
        self._usecase_service = UsecaseService.get_instance()
        self._org_service = OrgService.get_instance()
        self._user_service = UserService.get_instance()
        self._audit_service = AuditService.get_instance()

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    async def startup(self):
        try:
            logger.info("Starting up services...")
            # test = TestService()

            # Initializing database
            async with self.database.engine.begin() as conn:
                from sqlmodel import SQLModel
                from app.db.models import (
                    Org,
                    OrgMember,
                    Usecase,
                    Role,
                    User,
                    Application,
                    ApplicationType,
                    Document,
                    AuditLog,
                    DocumentType
                )

                await conn.run_sync(SQLModel.metadata.create_all)
            
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.exception("Error during service startup", str(e), exc_info=False)
            raise e
    
    async def shutdown(self):
        try:
            logger.info("Shutting down services...")
            if self.database is not None:
                await self.database.engine.dispose()
            logger.info("Database connection closed.")

        except Exception as e:
            logger.exception("Error during app shutdown", str(e), exc_info=True)

    # properties

    @property
    def test_service(self) -> TestService:
        return self._test_service
    
    @property
    def application_service(self) -> ApplicationService:
        return self._application_service
    
    @property
    def config_service(self) -> ConfigService:
        return self._config_service
    
    @property
    def usecase_service(self) -> UsecaseService:
        return self._usecase_service
    
    @property
    def org_service(self) -> OrgService:
        return self._org_service

    @property
    def user_service(self) -> UserService:
        return self._user_service
    
    @property
    def audit_service(self) -> AuditService:
        return self._audit_service
