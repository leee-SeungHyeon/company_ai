from abc import ABC, abstractmethod


class BaseReader(ABC):
    @abstractmethod
    def load(self) -> list[dict]:
        """
        문서를 읽어 dict 리스트로 반환합니다.
        각 dict: content, title, source, file_type
        """
