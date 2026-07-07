from pydantic import BaseModel, Field

class CallRequest(BaseModel):
    to_number: str = Field(..., description="The phone number to call in E.164 format (no +)")

class CallResponse(BaseModel):
    message: str
    call_id: str

class ErrorResponse(BaseModel):
    detail: str
