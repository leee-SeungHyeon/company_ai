from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.auth import get_user_roles
from services.qa import answer_question, stream_answer

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


@router.post("/qa/stream")
async def qa_stream_endpoint(request: QARequest, user_roles: list[str] = Depends(get_user_roles)):
    async def generator():
        async for chunk in stream_answer(request.query, user_roles=user_roles):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")
