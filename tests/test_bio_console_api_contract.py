"""
Contrato da Bio Console API (evolução biomimética + chat agente).

Requer PyTorch (import do motor). Sem Ollama: usa monkeypatch em _ollama_chat_request.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

pytest.importorskip("torch")

import app.bio_console_api as bc  # noqa: E402


def _fake_evolution_snapshot() -> dict:
    return {
        "performance_history_recent": [0.55, 0.6],
        "agent_biomimetic_cycles_total": 2,
        "last_biomimetic_evolution_unix": 0.0,
        "local_brain_performance": None,
        "local_brain_learning_entries": 0,
        "evolve_every_n_agent_episodes": 48,
        "evolve_cooldown_sec": 900.0,
        "evolution_worker_running": False,
        "evolution_queued": False,
        "evolution_profile": "minimal",
        "evolution_async": True,
    }


@pytest.fixture
def engine_mock() -> MagicMock:
    eng = MagicMock()
    eng.get_agent_evolution_snapshot.return_value = _fake_evolution_snapshot()
    eng.ingest_agent_biomimetic_episode.return_value = {
        "quality_score": 0.72,
        "biomimetic_feedback_recorded": True,
        "evolution_cycle_ran": False,
        "evolution_cycle_scheduled": False,
    }
    return eng


@pytest.fixture
def client(monkeypatch, engine_mock: MagicMock) -> TestClient:
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    return TestClient(bc.app)


def test_health_ok(client: TestClient):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("api") == "ok"
    assert "ollama" in body


def test_evolution_status_merges_engine_and_episodes(client: TestClient, engine_mock: MagicMock):
    r = client.get("/api/v1/evolution/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("evolution_profile") == "minimal"
    assert "agent_episodes_logged" in data
    engine_mock.get_agent_evolution_snapshot.assert_called_once()


def test_agent_episodes_empty(client: TestClient):
    r = client.get("/api/v1/agent/episodes?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data.get("total") == 0
    assert data.get("items") == []


def test_chat_agent_splits_reasoning(monkeypatch, engine_mock: MagicMock):
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)

    def fake_ollama(*_a, **_k):
        return {
            "message": {
                "content": "---RACIOCINIO---\nPasso a passo.\n---RESPOSTA---\nOlá."
            }
        }

    monkeypatch.setattr(bc, "_ollama_chat_request", fake_ollama)
    monkeypatch.setattr(bc, "_ollama_tags_reachable", lambda _url: True)

    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/chat",
        json={
            "message": "oi",
            "messages": [],
            "mode": "agent",
            "session_id": "s1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("answer") == "Olá."
    meta = body.get("metadata") or {}
    assert meta.get("mode") == "agent"
    assert "Passo a passo" in (meta.get("reasoning_trace") or "")
    bio = meta.get("biomimetic") or {}
    assert bio.get("quality_score") == 0.72
    engine_mock.ingest_agent_biomimetic_episode.assert_called_once()


def test_chat_requires_message(client: TestClient):
    r = client.post("/api/v1/chat", json={"message": "", "messages": []})
    assert r.status_code == 400


def test_tts_elevenlabs_status(client: TestClient):
    r = client.get("/api/v1/tts/elevenlabs/status")
    assert r.status_code == 200
    data = r.json()
    assert "available" in data
    assert "api_key_set" in data
    assert "default_voice_set" in data


def test_whatsapp_zapi_status(client: TestClient):
    r = client.get("/api/v1/whatsapp/zapi/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("zapi_send_configured") is False
    assert "webhook_post_url_relative" in data


def test_whatsapp_zapi_webhook_ack(client: TestClient):
    r = client.post(
        "/api/v1/whatsapp/zapi/webhook",
        json={"type": "ReceivedCallback", "fromMe": True, "phone": "5511999999999"},
    )
    assert r.status_code == 200
    assert r.json().get("received") is True


def test_obsidian_status(monkeypatch, client: TestClient):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    r = client.get("/api/v1/obsidian/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("vault_configured") is False
    assert "chokmah_folder" in data


def test_health_includes_obsidian(monkeypatch, client: TestClient):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    obs = (r.json().get("obsidian") or {})
    assert "vault_configured" in obs
    assert "chokmah_folder" in obs


def test_obsidian_note_requires_vault(monkeypatch, engine_mock: MagicMock):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={
            "relative_path": "x.md",
            "body": "conteúdo",
        },
    )
    assert r.status_code == 503


def test_obsidian_note_writes_file(tmp_path, monkeypatch, engine_mock: MagicMock):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(vault))
    monkeypatch.setenv("OBSIDIAN_CHOKMAH_RELATIVE", "CHOKMAH")
    monkeypatch.delenv("OBSIDIAN_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)

    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={
            "relative_path": "notas/teste.md",
            "title": "Título",
            "body": "Corpo **markdown**.",
            "tags": ["chokmah"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert data.get("mode") == "create"
    out = vault / "CHOKMAH" / "notas" / "teste.md"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "Título" in text
    assert "Corpo **markdown**." in text
    assert "chokmah" in text


def test_obsidian_note_rejects_traversal(tmp_path, monkeypatch, engine_mock: MagicMock):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(vault))
    monkeypatch.delenv("OBSIDIAN_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={"relative_path": "../escape.md", "body": "x"},
    )
    assert r.status_code == 400
