import pytest

from app.core.errors import UnauthorizedError, ValidationError
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    validate_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("TestPass123")
        assert verify_password("TestPass123", hashed)
        assert not verify_password("WrongPass123", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("TestPass123")
        h2 = hash_password("TestPass123")
        assert h1 != h2  # bcrypt salts differ


class TestPasswordValidation:
    def test_valid_password(self):
        validate_password("GoodPass1")  # should not raise

    def test_too_short(self):
        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password("Ab1")

    def test_no_uppercase(self):
        with pytest.raises(ValidationError, match="uppercase"):
            validate_password("lowercase1")

    def test_no_number(self):
        with pytest.raises(ValidationError, match="number"):
            validate_password("NoNumberHere")


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token("user-123", "org-456", "admin")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["org"] == "org-456"
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert "refresh_exp" in payload

    def test_invalid_token_raises(self):
        with pytest.raises(UnauthorizedError, match="Invalid or expired"):
            decode_token("garbage.token.here")


class TestAuthEndpoints:
    @pytest.fixture
    def register_payload(self):
        return {
            "email": "test@example.com",
            "password": "TestPass1",
            "name": "Test User",
            "organization_name": "Test Org",
        }

    @pytest.mark.skipif(True, reason="Requires database connection")
    async def test_register_and_login(self, client, register_payload):
        # Register
        resp = await client.post("/api/auth/register", json=register_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == register_payload["email"]
        assert data["role"] == "admin"

        # Login
        resp = await client.post(
            "/api/auth/login",
            json={"email": register_payload["email"], "password": register_payload["password"]},
        )
        assert resp.status_code == 200
        assert "token" in resp.json()
        assert "access_token" in resp.cookies

    @pytest.mark.skipif(True, reason="Requires database connection")
    async def test_me_unauthenticated(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    @pytest.mark.skipif(True, reason="Requires database connection")
    async def test_invalid_login(self, client):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "WrongPass1"},
        )
        assert resp.status_code == 400

    @pytest.mark.skipif(True, reason="Requires database connection")
    async def test_register_weak_password(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",
                "name": "Weak User",
                "organization_name": "Weak Org",
            },
        )
        assert resp.status_code == 400
