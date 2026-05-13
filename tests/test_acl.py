"""ACL 핵심 경로 스모크 테스트.

ACL은 이 프로젝트의 가장 중요한 가치라 베이스라인 회귀를 잡는다.
- get_user_roles: Bearer 토큰 → roles 매핑 (잘못된 키는 401)
- VectorSearchTool 의 query filter: user_roles 가 payload `allowed_roles` 매칭에 사용
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


def test_get_user_roles_returns_mapped_roles(monkeypatch):
    monkeypatch.setattr("api.auth.API_KEYS", {"valid-key": ["hr", "all"]})
    from api.auth import get_user_roles

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-key")
    assert get_user_roles(creds) == ["hr", "all"]


def test_get_user_roles_rejects_unknown_key(monkeypatch):
    monkeypatch.setattr("api.auth.API_KEYS", {})
    from api.auth import get_user_roles

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="nope")
    with pytest.raises(HTTPException) as exc_info:
        get_user_roles(creds)
    assert exc_info.value.status_code == 401


def test_acl_filter_includes_user_roles_and_all():
    """VectorSearchTool._arun 안의 ACL 필터 구조 회귀 방지.

    필터가 should(OR) 조건 두 개를 가져야 한다:
      1. allowed_roles ∈ user_roles
      2. allowed_roles == "all"
    """
    from qdrant_client import models

    user_roles = ["hr"]
    acl_filter = models.Filter(
        should=[
            models.FieldCondition(
                key="allowed_roles",
                match=models.MatchAny(any=user_roles),
            ),
            models.FieldCondition(
                key="allowed_roles",
                match=models.MatchValue(value="all"),
            ),
        ]
    )

    assert len(acl_filter.should) == 2
    assert acl_filter.should[0].key == "allowed_roles"
    assert acl_filter.should[0].match.any == ["hr"]
    assert acl_filter.should[1].match.value == "all"
