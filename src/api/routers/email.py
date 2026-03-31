from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.email import write_email

router = APIRouter()


class EmailRequest(BaseModel):
    request: str


class EmailResponse(BaseModel):
    subject: str
    body: str


@router.post("/email", response_model=EmailResponse)
async def email_endpoint(request: EmailRequest):
    try:
        result = await write_email(request.request)
        return EmailResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
