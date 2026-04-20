from app.providers.contracts import ProviderHealth
from app.providers.ollama import OllamaProvider


def test_submit_code_and_candidates_smoke(client):
    submit_response = client.post(
        "/submit-code",
        json={"source": "paste", "filename": "example.py", "code": "def example():\n    return 1\n"},
    )
    assert submit_response.status_code == 200

    submission_id = submit_response.json()["submission_id"]
    candidates_response = client.get("/candidates", params={"submission_id": submission_id})
    assert candidates_response.status_code == 200
    assert "candidates" in candidates_response.json()


def test_exercise_hints_and_attempt_smoke(client):
    exercise_response = client.post("/exercise/cand-demo")
    assert exercise_response.status_code == 200

    exercise_id = exercise_response.json()["exercise_id"]
    hints_response = client.get(f"/hints/{exercise_id}")
    assert hints_response.status_code == 200

    attempt_response = client.post(
        f"/submit-attempt/{exercise_id}",
        json={"attempt_code": "def refactored():\n    pass\n"},
    )
    assert attempt_response.status_code == 200


def test_provider_routes_smoke(client, monkeypatch):
    def fake_ollama_health(self):
        return ProviderHealth(
            provider="ollama",
            status="ready",
            available=True,
            message="Ollama is ready with model 'llama3.2:latest'.",
        )

    monkeypatch.setattr(OllamaProvider, "healthCheck", fake_ollama_health)

    providers_response = client.get("/providers")
    assert providers_response.status_code == 200

    config_response = client.get("/provider/config")
    assert config_response.status_code == 200

    update_response = client.put(
        "/provider/config",
        json={
            "config": {
                "default_provider": "ollama",
                "configured_providers": ["ollama", "openai"],
                "providers": {
                    "ollama": {"base_url": "http://localhost:11434"},
                    "openai": {"api_key": "openai-test-key", "model": "gpt-test"},
                    "anthropic": {},
                    "mcp": {},
                },
            }
        },
    )
    assert update_response.status_code == 200

    health_response = client.get("/provider/health")
    assert health_response.status_code == 200
    assert health_response.json()["providers"][0]["provider"] == "ollama"
    assert health_response.json()["providers"][0]["available"] is True
    assert health_response.json()["providers"][0]["failure"] is None


def test_github_routes_smoke(client):
    assert client.get("/github/connect").status_code == 200
    assert client.get("/github/repos").status_code == 200
    assert client.get("/github/repo/demo/tree").status_code == 200

    import_response = client.post(
        "/github/import-file",
        json={"repo_id": "demo", "path": "src/example.py", "ref": "main"},
    )
    assert import_response.status_code == 200
