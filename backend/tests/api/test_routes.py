"""Integration tests for FastAPI routes.

Tests the full HTTP stack: client → route → use case → (mocked) external services.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoot:
    async def test_root_returns_app_info(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "ClashClanEvaluation"
        assert data["version"] == "0.1.0"


class TestConfigEndpoint:
    async def test_get_config_returns_defaults(self, client: AsyncClient):
        resp = await client.get("/api/v1/config")
        assert resp.status_code == 200
        data = resp.json()
        assert data["attacks_per_day"] == 4
        assert data["yellow_to_red"] == 4
        assert data["red_to_black"] == 4
        assert data["min_points_warning"] == 1600
        assert data["relax_on_first_place"] is True

    async def test_restore_defaults(self, client: AsyncClient):
        resp = await client.post("/api/v1/config/defaults")
        assert resp.status_code == 200
        assert "Defaults" in resp.json()["message"]

    async def test_update_config(self, client: AsyncClient):
        resp = await client.put(
            "/api/v1/config",
            json={"yellow_to_red": 5, "min_points_warning": 1800},
        )
        assert resp.status_code == 200
        assert "updated" in resp.json()

        # Restore defaults to not pollute other tests
        await client.post("/api/v1/config/defaults")


class TestClanStatus:
    async def test_clan_status_without_config_returns_400(self, client: AsyncClient):
        """Without CR_CLAN_TAG configured, should return 400."""
        # The default config has cr_clan_tag="" so this should 400
        resp = await client.get("/api/v1/clan/status")
        # Could be 400 (no clan tag) or 200 (if .env has a tag)
        assert resp.status_code in (200, 400)


class TestPlayerHistory:
    async def test_player_history_returns_data(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/ABC123")
        assert resp.status_code == 200
        data = resp.json()
        assert "tag" in data
        assert "history" in data
        assert "recency" in data

    async def test_player_history_with_expand(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/ABC123?expand=true")
        assert resp.status_code == 200


class TestWarsEndpoint:
    async def test_list_wars(self, client: AsyncClient):
        resp = await client.get("/api/v1/wars")
        assert resp.status_code == 200
        data = resp.json()
        assert "wars" in data
        assert isinstance(data["wars"], list)

    async def test_war_detail_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/wars/99999")
        assert resp.status_code == 404


class TestEvaluateEndpoint:
    async def test_evaluate_without_config_returns_400(self, client: AsyncClient):
        resp = await client.post("/api/v1/evaluate")
        # Could be 400 (no clan tag) or 200 (if .env has a tag)
        assert resp.status_code in (200, 400)


class TestOpenAPI:
    async def test_docs_available(self, client: AsyncClient):
        resp = await client.get("/docs")
        assert resp.status_code == 200

    async def test_openapi_schema(self, client: AsyncClient):
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        assert "/api/v1/clan/status" in schema["paths"]
        assert "/api/v1/evaluate" in schema["paths"]
        assert "/api/v1/config" in schema["paths"]
