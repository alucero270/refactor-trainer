from app.providers.contracts import ProviderHealth
from app.providers.ollama import OllamaProvider


def test_submit_code_and_candidates_smoke(client):
    submit_response = client.post(
        "/submit-code",
        json={
            "source": "paste",
            "filename": "example.py",
            "code": (
                "def process(data, value):\n"
                "    total = 0\n"
                "    thing = value + 1\n"
                "    return total + thing\n"
            ),
        },
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["candidate_count"] == 1

    submission_id = submit_response.json()["submission_id"]
    candidates_response = client.get("/candidates", params={"submission_id": submission_id})
    assert candidates_response.status_code == 200
    assert "candidates" in candidates_response.json()
    assert candidates_response.json()["candidates"] == [
        {
            "id": "cand-poornaming-process-1",
            "title": "Clarify naming in 'process'",
            "smell": "PoorNaming",
            "summary": (
                "Function 'process' uses generic names (process, thing), "
                "which slows comprehension."
            ),
            "severity": "low",
        }
    ]


def test_submit_code_rejects_non_python_or_multi_file_shapes(client):
    invalid_extension = client.post(
        "/submit-code",
        json={"source": "upload", "filename": "example.txt", "code": "print('hello')"},
    )
    assert invalid_extension.status_code == 400
    assert invalid_extension.json()["detail"] == "Only single Python files are supported."

    nested_path = client.post(
        "/submit-code",
        json={"source": "upload", "filename": "src/example.py", "code": "print('hello')"},
    )
    assert nested_path.status_code == 400
    assert (
        nested_path.json()["detail"]
        == "submit-code accepts exactly one Python file, not a file path."
    )


def test_submit_code_rejects_invalid_python_syntax(client):
    response = client.post(
        "/submit-code",
        json={"source": "paste", "filename": "broken.py", "code": "def broken(:\n    pass\n"},
    )

    assert response.status_code == 400
    assert "Submitted code is not valid Python syntax" in response.json()["detail"]


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
