from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import col, select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.logging_config import logger
from app.db.models import (
    ActionTypeEnum,
    ApplicationType,
    ApplicationTypeDocumentTypeAssociation,
    AuditLog,
    DocumentType,
    Org,
    TargetEnum,
    Usecase,
    User,
)
from app.repositories.config_repo import ConfigRepo
from app.schemas.config_schema import CreateConfigurationRequest, DeleteConfigRequest, GetConfigResponse
from app.schemas.util import EmptyResponse

OPTIONAL = "optional"
MANDATORY = "mandatory"


class ConfigService:
    """
    Config service class
    """

    _instance = None
    config_repo: ConfigRepo

    def __init__(self) -> None:
        if ConfigService._instance is not None:
            raise RuntimeError("Use get_instance to get an instance of Config Service")

        self.config_repo = ConfigRepo.get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of ConfigService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_application_type_by_code(
        self, application_type: str, db: AsyncSession
    ) -> Optional[ApplicationType]:
        """
        Get application type by code
        """
        try:
            app_type = await db.exec(
                select(ApplicationType).where(
                    ApplicationType.application_type_code == application_type
                )
            )
            if app_type:
                return app_type.first()
            return None
        except Exception as e:
            logger.error(f"Failed to get application type by code: {str(e)}")
            raise e

    async def create_application_type(
        self, application_type: str, org_id: UUID, user_id: UUID, db: AsyncSession
    ) -> ApplicationType:
        """
        Create application type
        """
        app_type = ApplicationType(
            application_type_code=application_type,
            org_id=org_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(app_type)
        await db.commit()
        await db.refresh(app_type)
        
        from app.core.config_manager import ConfigManager
        await ConfigManager.get_instance().audit_service.create_audit_log(
            db,
            AuditLog(
                change_type=ActionTypeEnum.CREATE,
                title=f"Application type '{app_type.application_type_code}' created",
                target_name=TargetEnum.APPLICATION_TYPE,
                org_id=org_id,
                actor_id=user_id,
                target_id=app_type.application_type_id,
            )
        )
        return app_type

    async def get_doc_type(
        self, doc_type: str, category: str, db: AsyncSession
    ) -> Optional[DocumentType]:
        """
        Get document type from doc_type name and category
        """
        doc_type = await db.exec(
            select(DocumentType).where(
                DocumentType.name == doc_type, DocumentType.category == category
            )
        )
        if doc_type:
            return doc_type.first()
        return None

    async def create_doc_type(
        self, doc_type: str, category: str, user: User, db: AsyncSession
    ) -> DocumentType:
        """
        Create document type
        """
        doc_type = DocumentType(
            name=doc_type,
            category=category,
            created_by=user.user_id,
            updated_by=user.user_id,
        )
        db.add(doc_type)
        await db.commit()
        await db.refresh(doc_type)
        return doc_type

    async def create_association_model(
        self,
        application_type_id: UUID,
        usecase_id: UUID,
        doc_type: str,
        category: str,
        user: User,
        is_optional: bool,
        db: AsyncSession,
    ) -> None:
        """
        Create configuration
        """

        doc_type_obj = await self.get_doc_type(doc_type, category, db)

        # create document type if not exists
        if not doc_type_obj:
            doc_type_obj = await self.create_doc_type(doc_type, category, user, db)

        # create application_type document_type association
        # config_model = self.create_config_model(application_type.application_type_id, usecase.usecase_id, doc_type_obj, user, is_optional, db)

        config = ApplicationTypeDocumentTypeAssociation(
            application_type_id=application_type_id,
            document_type_id=doc_type_obj.document_type_id,
            usecase_id=usecase_id,
            is_optional=is_optional,
            created_by=user.user_id,
            updated_by=user.user_id,
        )
        return config

    async def get_associations_for_application_type(
        self, application_type_id: UUID, usecase_id: UUID, db: AsyncSession
    ) -> List[ApplicationTypeDocumentTypeAssociation]:
        """
        Get associations for application type
        """
        associations = await db.exec(
            select(ApplicationTypeDocumentTypeAssociation).where(
                ApplicationTypeDocumentTypeAssociation.application_type_id
                == application_type_id,
                ApplicationTypeDocumentTypeAssociation.usecase_id == usecase_id,
            )
        )
        return associations.all()

    async def update_association(
        self,
        application_type: ApplicationType,
        config: CreateConfigurationRequest,
        usecase: Usecase,
        user: User,
        db: AsyncSession,
    ) -> Tuple[List, List, List]:
        """
        Update association
        """

        update_associations = []
        create_associations = []
        logs = []

        existing_associations = await self.get_associations_for_application_type(
            application_type.application_type_id, usecase.usecase_id, db
        )

        # transform existing associations to a dictionary for easier lookup
        existing_associations_dict = {
            f"{assoc.document_type.category}_$_{assoc.document_type.name}": assoc
            for assoc in existing_associations
        }

        for category, docs in config.config.items():
            category = category.lower()
            for doc in docs:
                doc_type = doc[0].lower()
                is_optional = doc[1].lower() == OPTIONAL

                # check if association exist or not
                assoc_key = f"{category}_$_{doc_type}"
                if assoc_key in existing_associations_dict:
                    # update existing association
                    assoc = existing_associations_dict[assoc_key]
                    if assoc.is_optional != is_optional:
                        assoc.is_optional = is_optional
                        update_associations.append(assoc)

                    logs.append(AuditLog(
                        change_type=ActionTypeEnum.UPDATE,
                        title=f"Association between application type '{application_type.application_type_code}' and document type '{doc_type}' in category '{category}' made {OPTIONAL if is_optional else MANDATORY}",
                        target_name=TargetEnum.CONFIG,
                        org_id=application_type.org_id,
                        actor_id=user.user_id,
                        target_id=assoc.application_type_document_type_association_id,
                    ))
                else:
                    # create new association
                    association_model = await self.create_association_model(
                        application_type.application_type_id,
                        usecase.usecase_id,
                        doc_type,
                        category,
                        user,
                        is_optional,
                        db,
                    )
                    if association_model:
                        create_associations.append(association_model)
                        logs.append(AuditLog(
                            change_type=ActionTypeEnum.CREATE,
                            title=f"Association between application type '{application_type.application_type_code}' and document type '{doc_type}' in category '{category}' created",
                            target_name=TargetEnum.CONFIG,
                            org_id=application_type.org_id,
                            actor_id=user.user_id,
                            target_id=association_model.application_type_document_type_association_id ,
                        ))

        return create_associations, update_associations, logs

    async def create_association(
        self,
        application_type: ApplicationType,
        config: CreateConfigurationRequest,
        usecase: Usecase,
        user: User,
        db: AsyncSession,
    ) -> Tuple[List[ApplicationTypeDocumentTypeAssociation], List[AuditLog]]:
        """
        Create association
        """
        # iterate over docs
        associations = []
        logs = []
        for category, docs in config.config.items():
            category = category.lower()
            for doc in docs:
                doc_type = doc[0].lower()
                is_optional = doc[1].lower() == OPTIONAL

                # create association model
                association_model = await self.create_association_model(
                    application_type.application_type_id,
                    usecase.usecase_id,
                    doc_type,
                    category,
                    user,
                    is_optional,
                    db,
                )
                if association_model:
                    associations.append(association_model)
                    logs.append(AuditLog(
                        change_type=ActionTypeEnum.CREATE,
                        title=f"Association between application type '{application_type.application_type_code}' and document type '{doc_type}' in category '{category}' created",
                        target_name=TargetEnum.CONFIG,
                        org_id=application_type.org_id,
                        actor_id=user.user_id,
                        target_id=association_model.application_type_document_type_association_id ,
                    ))

        return associations, logs

    async def create_configuration(
        self,
        user: User,
        org: Org,
        usecase: Usecase,
        config_data: List[CreateConfigurationRequest],
        db: AsyncSession,
    ) -> None:
        """
        Create configuration
        """

        create_associations = []
        update_associations = []
        logs = []

        for config in config_data:
            application_type = await self.get_application_type_by_code(
                config.application_type, db
            )
            if application_type:
                create_associations_models, update_associations_models, logs_models = (
                    await self.update_association(
                        application_type, config, usecase, user, db
                    )
                )
                create_associations.extend(create_associations_models)
                update_associations.extend(update_associations_models)
                logs.extend(logs_models)
                # existing_application_types += f"{application_type.application_type_code}, "
                # continue
            else:
                application_type = await self.create_application_type(
                    config.application_type, org.org_id, user.user_id, db
                )
                associations, logs_models = await self.create_association(
                    application_type, config, usecase, user, db
                )
                create_associations.extend(associations)
                logs.extend(logs_models)

        # add associations to db
        db.add_all(create_associations)
        db.add_all(logs)
        # db.add_all(update_associations)
        await db.commit()

        return EmptyResponse(
            message="Configuration created successfully", status_code=201
        )

    async def transformed_doc_types(self, db: AsyncSession) -> List[DocumentType]:
        """
        Get transformed document types
        """
        doc_types = await db.exec(select(DocumentType))
        transformed_doc_types = {}
        for doc_type in doc_types:
            key = f"{doc_type.category}_$_{doc_type.name}"
            transformed_doc_types[key] = doc_type
        return transformed_doc_types

    async def delete_configuration(
        self,
        user: User,
        org: Org,
        usecase: Usecase,
        config_data: List[DeleteConfigRequest],
        db: AsyncSession,
    ) -> None:
        """
        Delete configuration
        """
        # get transformed document types
        transformed_doc_types = await self.transformed_doc_types(db)

        logs = []

        for config in config_data:
            application_type = await self.get_application_type_by_code(
                config.application_type, db
            )
            if not application_type:
                logger.error(f"Application type {config.application_type} does not exist")
                continue

            delete_doc_type_ids = []

            for category, docs in config.config.items():
                category = category.lower()
                for doc in docs:
                    doc_type = doc.lower()
                    key = f"{category}_$_{doc_type}"
                    if key in transformed_doc_types:
                        # delete association
                        delete_doc_type_ids.append(transformed_doc_types[key].document_type_id)
                        logs.append(AuditLog(
                            change_type=ActionTypeEnum.DELETE,
                            title=f"Association between application type '{application_type.application_type_code}' and document type '{doc_type}' in category '{category}' deleted",
                            target_name=TargetEnum.CONFIG,
                            org_id=application_type.org_id,
                            actor_id=user.user_id,
                            target_id=None,
                        ))
            
            # delete associations
            await db.exec(
                delete(ApplicationTypeDocumentTypeAssociation).where(
                    ApplicationTypeDocumentTypeAssociation.application_type_id == application_type.application_type_id,
                    ApplicationTypeDocumentTypeAssociation.usecase_id == usecase.usecase_id,
                    col(ApplicationTypeDocumentTypeAssociation.document_type_id).in_(delete_doc_type_ids),
                )
            )

            logger.info(f"Deleted associations for application type {application_type.application_type_code} and usecase {usecase.usecase_id}")
        
        db.add_all(logs)
        await db.commit()

        return EmptyResponse(
            message="Configuration deleted successfully", status_code=200
        )

    async def get_configuration(
        self,
        org: Org,
        usecase: Usecase,
        db: AsyncSession,
    ) -> List[GetConfigResponse]:
        """
        Get configuration
        """
        # get associations
        associations = await db.exec(
            select(ApplicationTypeDocumentTypeAssociation)
            .where(
                ApplicationTypeDocumentTypeAssociation.usecase_id == usecase.usecase_id
            )
        )
        associations = associations.all()

        # transform associations

        # response structure
        # [{
        #     application_type: "A1",
        #     docs: {
        #         "income" : [
        #                     ("payslip", "mandatory"),
        #                     ("bank_statement", "mandatory")
        #                 ],
        #         "id_proof": {
        #                     "passport": "optional"
        #                 }
        #     }
        # }]
        config = {}

        for assoc in associations:
            
            if not config.get(assoc.application_type.application_type_code, None):
                config[assoc.application_type.application_type_code] = {}
            if not config.get(assoc.application_type.application_type_code).get(assoc.document_type.category):
                config[assoc.application_type.application_type_code][assoc.document_type.category] = []

            config.get(
                assoc.application_type.application_type_code, {}
            ).get(
                assoc.document_type.category, []
            ).append((assoc.document_type.name, MANDATORY if not assoc.is_optional else OPTIONAL))

        return [GetConfigResponse(application_type=k, config=v) for k, v in config.items()]

