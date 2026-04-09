from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.auth import get_user_roles
from services.qa import answer_question

router = APIRouter()


class QARequest(BaseModel):
    query: str


class QAResponse(BaseModel):
    answer: str


@router.post("/qa", response_model=QAResponse)
async def qa_endpoint(request: QARequest, user_roles: list[str] = Depends(get_user_roles)):
    try:
        answer = await answer_question(request.query, user_roles=user_roles)
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
