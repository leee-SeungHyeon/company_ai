from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.qa import answer_question

router = APIRouter()


class QARequest(BaseModel):
    query: str


class QAResponse(BaseModel):
    answer: str


@router.post("/qa", response_model=QAResponse)
async def qa_endpoint(request: QARequest):
    try:
        answer = await answer_question(request.query)
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
