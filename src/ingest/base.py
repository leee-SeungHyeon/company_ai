from abc import ABC, abstractmethod


class BaseReader(ABC):
    @abstractmethod
    def load(self) -> list[dict]:
        """
        문서를 읽어 dict 리스트로 반환합니다.
        각 dict: content, title, source, file_type, allowed_roles
        allowed_roles: 접근 가능한 역할 목록. ["all"] 이면 모든 사용자 접근 가능.
        """
