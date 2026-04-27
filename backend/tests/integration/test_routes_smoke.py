import json

from app.providers.contracts import ProviderHealth
from app.providers.mock import MockProvider
from app.providers.ollama import OllamaProvider
from app.storage.memory import app_state


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

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert metrics_response.json()["counters"]["submit_code.accepted"] == 1
    assert metrics_response.json()["counters"]["candidates.listed"] == 1


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


def test_exercise_hints_and_attempt_smoke(client, monkeypatch):
    from app.api.routes import exercise_service

    monkeypatch.setattr(exercise_service.provider_service, "providers", [MockProvider()])

    submit_response = client.post(
        "/submit-code",
        json={
            "source": "paste",
            "filename": "exercise.py",
            "code": (
                "def process(data, value):\n"
                "    total = 0\n"
                "    thing = value + 1\n"
                "    return total + thing\n"
            ),
        },
    )
    candidate_id = client.get(
        "/candidates", params={"submission_id": submit_response.json()["submission_id"]}
    ).json()["candidates"][0]["id"]

    exercise_response = client.post(f"/exercise/{candidate_id}")
    assert exercise_response.status_code == 200
    assert exercise_response.json()["status"] == "generated"
    assert exercise_response.json()["title"] == "Practice improving PoorNaming"

    exercise_id = exercise_response.json()["exercise_id"]
    first_hints_response = client.get(f"/hints/{exercise_id}")
    assert first_hints_response.status_code == 200
    assert first_hints_response.json()["hints"] == [
        "Start by isolating the part of the code that shows the PoorNaming smell."
    ]

    second_hints_response = client.get(f"/hints/{exercise_id}")
    assert second_hints_response.status_code == 200
    assert second_hints_response.json()["hints"] == [
        "Start by isolating the part of the code that shows the PoorNaming smell.",
        "Extract one cohesive responsibility first, then reassess whether the main flow reads more clearly.",
    ]

    attempt_response = client.post(
        f"/submit-attempt/{exercise_id}",
        json={
            "attempt_code": (
                "def clarify_names(records, threshold):\n"
                "    running_total = 0\n"
                "    increment = threshold + 1\n"
                "    return running_total + increment\n"
            )
        },
    )
    assert attempt_response.status_code == 200
    assert attempt_response.json()["accepted"] is True
    assert attempt_response.json()["status"] == "evaluated"
    assert app_state.exercises[exercise_id]["issue_label"] == "PoorNaming"


def test_provider_routes_smoke(client, monkeypatch, provider_config_path):
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
    assert "openai-test-key" not in update_response.text
    assert update_response.json()["config"]["providers"]["openai"]["api_key"] == "**********"

    stored_config = json.loads(provider_config_path.read_text(encoding="utf-8"))
    assert stored_config["providers"]["openai"]["api_key"] == "openai-test-key"

    health_response = client.get("/provider/health")
    assert health_response.status_code == 200
    assert health_response.json()["providers"][0]["provider"] == "ollama"
    assert health_response.json()["providers"][0]["available"] is True
    assert health_response.json()["providers"][0]["failure"] is None


def test_github_routes_require_bearer_token(client):
    connect_response = client.get("/github/connect")
    assert connect_response.status_code == 200
    assert connect_response.json()["status"] == "not_connected"

    assert client.get("/github/repos").status_code == 400
    assert (
        client.get("/github/repo/tree", params={"repo_id": "octocat/hello-world"}).status_code == 400
    )
    assert (
        client.post(
            "/github/import-file",
            json={"repo_id": "octocat/hello-world", "path": "src/example.py", "ref": "main"},
        ).status_code
        == 400
    )


def test_github_routes_end_to_end_with_fake_client(client, monkeypatch):
    from app.api import routes
    from app.services.github_service import (
        GitHubFileContent,
        GitHubRepoSummary,
        GitHubService,
        GitHubTreeEntry,
    )
    from tests.unit.test_github_service import FakeGitHubClient

    fake_client = FakeGitHubClient(
        repos=[GitHubRepoSummary(owner="octocat", name="hello-world")],
        default_branch="main",
        tree=[
            GitHubTreeEntry(path="src/example.py", type="blob"),
            GitHubTreeEntry(path="README.md", type="blob"),
        ],
        file_content=GitHubFileContent(path="src/example.py", content="print('hi')\n"),
    )
    monkeypatch.setattr(routes, "github_service", GitHubService(client=fake_client))

    headers = {"Authorization": "Bearer live-token"}

    repos_response = client.get("/github/repos", headers=headers)
    assert repos_response.status_code == 200
    assert repos_response.json()["repos"] == [
        {"id": "octocat/hello-world", "owner": "octocat", "name": "hello-world"}
    ]

    tree_response = client.get(
        "/github/repo/tree",
        params={"repo_id": "octocat/hello-world", "ref": "HEAD"},
        headers=headers,
    )
    assert tree_response.status_code == 200
    assert tree_response.json()["tree"] == [{"path": "src/example.py", "type": "blob"}]

    import_response = client.post(
        "/github/import-file",
        json={"repo_id": "octocat/hello-world", "path": "src/example.py", "ref": "HEAD"},
        headers=headers,
    )
    assert import_response.status_code == 200
    assert import_response.json()["status"] == "imported"
    assert import_response.json()["content"] == "print('hi')\n"


def test_github_connect_rejects_non_bearer_authorization(client):
    response = client.get("/github/connect", headers={"Authorization": "Basic abc"})

    assert response.status_code == 400
    assert response.json()["detail"] == "GitHub connection requires an Authorization bearer token."
