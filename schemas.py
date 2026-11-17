from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class StandardResponse(BaseModel):
    status: str
    token: Optional[str] = None
    message: Optional[str] = None

class OnboardTokenResponse(BaseModel):
    token: str
    expires_in: int

class UploadPayload(BaseModel):
    userID: str
    uploadType: str
    uploadTime: str
    claudeKey: Optional[str] = None
    claudeModel: Optional[str] = None
    data: Optional[List[Any]] = None

class OnboardPayload(BaseModel):
    userID: str
    uploadType: str
    uploadTime: str
