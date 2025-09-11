from typing import Any, Dict, List

from pydantic import BaseModel


class CreateConfigurationRequest(BaseModel):
    """
    Create configuration request schema
    """

    application_type: str
    config: Dict[str, Any]


class DeleteConfigRequest(BaseModel):
    """
    Delete configuration request schema
    """

    application_type: str
    config: Dict[str, Any]


class GetConfigResponse(BaseModel):
    """
    Get configuration response schema
    """

    application_type: str
    config: Dict[str, Any]
