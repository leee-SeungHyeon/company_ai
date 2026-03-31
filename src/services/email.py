from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from agent.llm import get_llm

EMAIL_SYSTEM_PROMPT = """당신은 한국 비즈니스 이메일 작성 전문가입니다.
사용자의 요청에 따라 격식체(합쇼체) 비즈니스 이메일을 작성해주세요.

이메일 작성 규칙:
- 합쇼체(격식체)를 사용하세요
- 적절한 인사말로 시작하세요 (예: "안녕하십니까.")
- 핵심 내용을 명확하고 간결하게 전달하세요
- 정중한 마무리 인사로 끝내세요
- 발신자 서명란은 [이름/부서]로 표시하세요
"""


class EmailOutput(BaseModel):
    subject: str = Field(description="이메일 제목")
    body: str = Field(description="이메일 본문 (격식체, 합쇼체)")


async def write_email(request: str) -> dict:
    llm = get_llm().with_structured_output(EmailOutput)
    result = await llm.ainvoke([
        SystemMessage(content=EMAIL_SYSTEM_PROMPT),
        HumanMessage(content=request),
    ])
    return {"subject": result.subject, "body": result.body}
