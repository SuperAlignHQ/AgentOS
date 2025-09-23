import json
import httpx
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import File, UploadFile, requests
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.exception_handler import (
    BadRequestException,
    ConflictException,
    DatabaseException,
    FileProcessingException,
    InternalException,
    NotFoundException,
    ValidationException,
)
from app.core.logging_config import logger
from app.core.util import transform_doc_types, validate_application_type
from app.db.models import ActionTypeEnum, Application, ApplicationStatus, ApplicationTypeDocumentTypeAssociation, AuditLog, Document, DocumentCheckStatus, DocumentType, FileFormat, Org, PolicyCheckStatus, SystemStatus, TargetEnum, UnderwriterStatus, Usecase, User
from app.repositories.application_repo import ApplicationRepo
from app.schemas.util import EmptyResponse, PaginationQuery
from app.schemas.application_schema import (
    CreateApplicationRequest,
    CreateApplicationResponse,
    GetApplicationsResponse,
    UpdateApplicationRequest,
)


class ApplicationService:
    """
    Application service class
    """

    _instance = None
    application_repo: ApplicationRepo

    def __init__(self) -> None:
        if ApplicationService._instance is not None:
            raise RuntimeError(
                "Use get_instance to get an instance of Application Service"
            )

        self.application_repo = ApplicationRepo().get_instance()

    @classmethod
    def get_instance(cls):
        """
        Get instance of ApplicationService
        """
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    async def get_all_applications(
        self, org: Org, usecase: Usecase, pagination: PaginationQuery, db: AsyncSession
    ) -> GetApplicationsResponse:
        """
        Get all applications
        """
        try:
            applications, total = await self.application_repo.get_all_applications(
                org, usecase, pagination, db
            )
            return GetApplicationsResponse.from_orm(applications=applications, total=total)
        except Exception as e:
            logger.error(f"Error in get_all_applications: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def get_application_by_underwriting_id(
        self, underwriting_id: str, db: AsyncSession
    ) -> Optional[Application]:
        """
        Get application by underwriting id
        """
        try:
            if not underwriting_id:
                raise BadRequestException("Underwriting ID is required")

            application = await db.exec(
                select(Application).where(
                    Application.underwriting_application_id == underwriting_id
                )
            )
            return application.first()
        except BadRequestException:
            raise
        except Exception as e:
            logger.error(
                f"Error in get_application_by_underwriting_id: {str(e)}", exc_info=True
            )
            raise DatabaseException(f"{str(e)}")

    async def delete_uploaded_documents(
        self, application_id: UUID, db: AsyncSession, org: Org, user: User
    ) -> None:
        """
        Delete uploaded documents for an application
        """
        try:
            if not application_id:
                raise BadRequestException("Application ID is required")

            documents = await db.exec(
                select(Document).where(Document.application_id == application_id)
            )
            documents = documents.all()
            logs = []

            for document in documents:
                await db.delete(document)
                logs.append(AuditLog(
                    change_type=ActionTypeEnum.DELETE,
                    title=f"Document: {document.document_id} deleted for application id {application_id}",
                    target_name=TargetEnum.DOCUMENT,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=document.document_id,
                ))

            await db.commit()

            db.add_all(logs)
            await db.commit()
        except BadRequestException:
            raise
        except Exception as e:
            logger.error(
                f"Error in delete_uploaded_documents: {str(e)}", exc_info=True
            )
            raise DatabaseException(f"{str(e)}")

    async def create_application(
        self,
        org: Org,
        usecase: Usecase,
        application_data: CreateApplicationRequest,
        user: User,
        db: AsyncSession,
        files: List[UploadFile],
    ) -> CreateApplicationResponse:
        """
        Create application
        """
        try:
            # Validate input data
            if not application_data.application_id:
                raise BadRequestException("Application ID is required")

            if not application_data.application_type:
                raise BadRequestException("Application type is required")

            if not files:
                raise BadRequestException("File is required")

            # Validate application data
            application_type = await validate_application_type(
                application_data.application_type, db
            )

            # Check if application already exists
            application = await self.get_application_by_underwriting_id(
                application_data.application_id, db
            )
            
            from app.core.config_manager import ConfigManager
            audit_service = ConfigManager.get_instance().audit_service
            logs = []

            if not application:
                # create application
                application = await self.application_repo.create_application(
                    org, usecase, application_data, application_type, user, db
                )

            # upload files to gcs, build document model and add unique id in filename for ocr
            # TODO: upload file to gcs

            document_model_file_map = {}
            for file in files:
                new_filename = f"{application.underwriting_application_id}_$_{file.filename}"
                document_model = Document(
                    application_id=application.application_id,
                    format=FileFormat.get_file_format(file.filename.split(".")[-1]),
                    original_file_name=file.filename,
                    url="",
                    size=file.size,
                    created_by=user.user_id,
                    updated_by=user.user_id
                )
                file.filename = new_filename
                document_model_file_map[file.filename] = document_model

            # get all document application type associations for application type
            associations = await db.exec(
                select(
                    ApplicationTypeDocumentTypeAssociation).where(
                        ApplicationTypeDocumentTypeAssociation.usecase_id == usecase.usecase_id,
                        ApplicationTypeDocumentTypeAssociation.application_type_id == application.application_type_id
                    )
                )
            associations = associations.all()

            ocr_response = await self.build_ocr_request(files, {"Application_id": application.underwriting_application_id, "Application_type": application_type.application_type_code}, usecase.usecase_id, application_type.application_type_id, associations, db)

            if not isinstance(ocr_response, dict):
                raise InternalException(ocr_response)

            if ocr_response.get("detail"):
                raise InternalException(message=ocr_response.get("detail"))

            transformed_doc_types = await transform_doc_types(db)
            
            classficiation_res = ocr_response.get("classification_results")
            processed_files = ocr_response.get("files")

            document_check_result = True
            policy_check_result = True

            if classficiation_res:
                for res in classficiation_res:
                    if not res.get("result"):
                        continue

                    doc_type = res.get("document_type")
                    doc_category = res.get("document_category")

                    key = f"{doc_category}_$_{doc_type}"
                    doc_type_model = None
                    if key in transformed_doc_types:
                        doc_type_model = transformed_doc_types[key]

                    doc_model = document_model_file_map.get(res.get("matched_filename"))
                    if doc_model:
                        doc_model.document_type_id = doc_type_model.document_type_id
                        db.add(doc_model)

                    log = AuditLog(
                        change_type=ActionTypeEnum.CREATE,
                        title="Document Created",
                        target_name=TargetEnum.DOCUMENT,
                        org_id=org.org_id,
                        actor_id=user.user_id,
                        target_id=doc_model.document_id,
                    )

                    logs.append(log)

                    doc_result = list(filter(lambda result: result["document_type"] == doc_type and result["document_category"] == doc_category, application.document_result)) if application.document_result else []

                    if doc_result:
                        doc_result[0]["result"] = res.get("result")
                        doc_result[0]["reason"] = res.get("reason")
                        flag_modified(application, "document_result")

                # calculate overall status of application

                for doc_result in application.document_result:
                    if doc_result.get("result"):
                        document_check_result = document_check_result and doc_result.get("result")
                    else:
                        document_check_result = False

                    #######-------COMMENT ABOVE CODE & KEEP BELOW CODE

                    # if not doc_result.get("optional") and doc_result.get("result"):
                    #     document_check_result = document_check_result and doc_result.get("result")
                    # elif doc_result.get("optional"):
                    #     document_check_result = document_check_result and True
                    # else:
                    #     document_check_result = False


                    #########----------------
                application.overall_document_check_status = DocumentCheckStatus.PASS if document_check_result else DocumentCheckStatus.FAIL

            policy_result = []
            if processed_files:
                for file in processed_files:
                    if file.get("policy_validation_results"):
                        policy_result.extend(list(map(lambda x: {"doc_type": file.get("document_type"), **x}, file.get("policy_validation_results"))))
                        policy_res_status = map(lambda x: True if x.get("result") == "Yes" else False, file.get("policy_validation_results"))
                        if all(policy_res_status):
                            policy_check_result = policy_check_result and True
                        else:
                            policy_check_result = False

                    # get the evaluated field values from the response
                    if file.get("evaluations"):
                        docu_model = document_model_file_map[file.get("filename")]
                        if docu_model:
                            docu_model.evaluations = file.get("evaluations")
                            docu_model.url = "/Users/jagdeepsingh/Downloads/db_schema_core_v2.png"
                

            application.overall_policy_check_status = PolicyCheckStatus.PASS if policy_check_result else PolicyCheckStatus.FAIL
            application.policy_check_result = policy_result
            application.underwriter_status = application.underwriter_status or UnderwriterStatus.NEW
            application.underwriter_review = application.underwriter_review or ""

            if document_check_result and policy_check_result:
                application.system_status = SystemStatus.APPROVED
            else:
                application.system_status = SystemStatus.DECLINED
            
            await db.commit()
            await db.refresh(application)

            # TODO: Implement file processing logic

            db.add_all(logs)
            await db.commit()

            await audit_service.create_audit_log(
                db,
                AuditLog(
                    change_type=ActionTypeEnum.CREATE,
                    title="Application Created",
                    target_name=TargetEnum.APPLICATION,
                    org_id=org.org_id,
                    actor_id=user.user_id,
                    target_id=application.application_id,
                )
            )

            return CreateApplicationResponse(
                application_id=application.underwriting_application_id,
                application_type=application.application_type.application_type_code,
                classification_overall_result=True if application.status == ApplicationStatus.APPROVED else False,
                classification_results=application.document_result,
            )

        except (BadRequestException, ConflictException, ValidationException):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in create_application: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")

    async def build_ocr_request(self, files: List[UploadFile], payload: dict, usecase_id: UUID, application_type_id: UUID, associations: List[ApplicationTypeDocumentTypeAssociation], db: AsyncSession) -> None:
        """
        Build ocr request
        """
        try:
            from app.core.config_manager import ConfigManager
            settings = ConfigManager.get_instance().settings

            # get all document types
            document_types = await db.exec(select(DocumentType))
            document_types = document_types.all()

            payload["total_list_of_documents"] = [doc_type.to_ocr_request() for doc_type in document_types]
            payload["required_documents"] = [assoc.to_ocr_request() for assoc in associations]

            # build ocr request

            client = httpx.AsyncClient()
            try:
                response = await client.post(
                    settings.OCR_CLASSIFICATION_ENDPOINT,
                    data={"payload": json.dumps(payload)},
                    files=[("files", (file.filename, file.file, file.content_type)) for file in files],
                    timeout=settings.OCR_TIMEOUT
                )
                return response.json()
            finally:
                await client.aclose()

            return {}
        except httpx.ReadTimeout:
            raise DatabaseException("Failed to build ocr request: API Timeout")
        except httpx.ConnectTimeout:
            raise DatabaseException("Failed to build ocr request: Connection Timeout")
        except httpx.TimeoutException as e:
            raise DatabaseException(f"Failed to build ocr request: Timeout Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in build_ocr_request: {str(e)}", exc_info=True)
            raise DatabaseException(f"Failed to build ocr request: {str(e)}")

    async def update_application(self, org: Org, usecase: Usecase, application_id: str, data: UpdateApplicationRequest, db: AsyncSession) -> Application:
        """Update an existing Application"""
        try:
            application = await db.exec(
                select(Application).where(
                    Application.underwriting_application_id == application_id,
                    Application.usecase_id == usecase.usecase_id
                )
            )
            application = application.first()

            if not application:
                raise NotFoundException(f"Application with id {application_id} not found")
            
            application.underwriter_status = data.underwriter_status
            application.underwriter_review = data.underwriter_review

            await db.commit()
            await db.refresh(application)

            return EmptyResponse(message="Application updated!")

        except Exception as e:
            logger.error(f"Error in update_application: {str(e)}", exc_info=True)
            raise DatabaseException(f"{str(e)}")
