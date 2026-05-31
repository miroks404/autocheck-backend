from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.application.use_cases.auth_use_cases import AuthUseCases
from app.models import UserRole
from app.schemas import RegisterIn


class FakeAuthRepo:
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def get_by_email(self, email: str):
        return self._users.get(email)

    def create_user(self, full_name: str, email: str, password_hash: str, role: str):
        user = SimpleNamespace(
            id=self._next_id,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=UserRole(role),
        )
        self._users[email] = user
        self._next_id += 1
        return user


def test_register_rejects_privileged_roles():
    use_case = AuthUseCases(FakeAuthRepo())
    payload = RegisterIn(
        full_name="Root User",
        email="root@example.com",
        password="password123",
        role="admin",
    )

    with pytest.raises(HTTPException) as exc:
        use_case.register(payload)

    assert exc.value.status_code == 403


def test_register_candidate_success():
    use_case = AuthUseCases(FakeAuthRepo())
    payload = RegisterIn(
        full_name="Candidate User",
        email="candidate@example.com",
        password="password123",
        role="candidate",
    )

    result = use_case.register(payload)

    assert result["user"]["email"] == "candidate@example.com"
    assert result["user"]["role"] == "candidate"
    assert result["accessToken"]
