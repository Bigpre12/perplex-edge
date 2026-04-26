import asyncio

from services.external_api_gateway import ExternalApiGateway


def test_gateway_ttl_cache_prevents_second_paid_call(monkeypatch):
    gateway = ExternalApiGateway()
    calls = {"n": 0}

    async def fake_budget(_provider):
        return {
            "mode": "normal",
            "used_hour": 0,
            "used_day": 0,
            "hour_limit": 100,
            "day_limit": 1000,
            "reserve_limit": 10,
        }

    class FakeResp:
        status_code = 200
        headers = {"content-type": "application/json", "x-requests-remaining": "99"}

        @staticmethod
        def json():
            return {"ok": True}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, params=None, headers=None):
            calls["n"] += 1
            return FakeResp()

    monkeypatch.setattr(gateway, "_budget_state", fake_budget)
    monkeypatch.setattr("services.external_api_gateway.httpx.AsyncClient", lambda timeout=15.0: FakeClient())

    async def run():
        r1 = await gateway.request(
            provider="theoddsapi",
            endpoint="/sports",
            url="https://example.com/sports",
            params={},
            data_class="sports",
        )
        r2 = await gateway.request(
            provider="theoddsapi",
            endpoint="/sports",
            url="https://example.com/sports",
            params={},
            data_class="sports",
        )
        assert r1 is not None and r2 is not None
        assert calls["n"] == 1

    asyncio.run(run())


def test_gateway_protection_mode_blocks_nonessential(monkeypatch):
    gateway = ExternalApiGateway()

    async def fake_budget(_provider):
        return {
            "mode": "protection",
            "used_hour": 900,
            "used_day": 9000,
            "hour_limit": 1000,
            "day_limit": 10000,
            "reserve_limit": 100,
        }

    monkeypatch.setattr(gateway, "_budget_state", fake_budget)

    async def run():
        res = await gateway.request(
            provider="theoddsapi",
            endpoint="/sports/basketball_nba/events/abc/odds",
            url="https://example.com/odds",
            params={},
            data_class="player_props",
            admin_override=False,
            live_essential=False,
        )
        assert res is None

    asyncio.run(run())
