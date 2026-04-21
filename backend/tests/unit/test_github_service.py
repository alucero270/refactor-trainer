import pytest

from app.services.github_service import (
    GitHubFileContent,
    GitHubRepository,
    GitHubRepositoryRef,
    GitHubService,
    GitHubToken,
    GitHubTreeEntry,
    GitHubUser,
    extract_bearer_token,
    redact_secret,
)


class FakeGitHubClient:
    def __init__(self) -> None:
        self.tokens: list[str] = []

    def get_authenticated_user(self, token: GitHubToken) -> GitHubUser:
        self.tokens.append(token.get_secret_value())
        return GitHubUser(login="octocat")

    def list_repositories(self, token: GitHubToken) -> list[GitHubRepository]:
        self.tokens.append(token.get_secret_value())
        return [
            GitHubRepository(id="123", name="trainer", owner="octocat"),
            GitHubRepository(id="456", name="practice", owner="octo-org"),
        ]

    def get_repository(self, token: GitHubToken, repo_id: str) -> GitHubRepositoryRef:
        self.tokens.append(token.get_secret_value())
        assert repo_id == "123"
        return GitHubRepositoryRef(owner="octocat", name="trainer", default_branch="main")

    def list_directory(
        self, token: GitHubToken, repository: GitHubRepositoryRef, path: str, ref: str | None
    ) -> list[GitHubTreeEntry]:
        self.tokens.append(token.get_secret_value())
        assert repository == GitHubRepositoryRef(
            owner="octocat", name="trainer", default_branch="main"
        )
        assert path == "src"
        assert ref == "main"
        return [
            GitHubTreeEntry(path="src/example.py", type="blob"),
            GitHubTreeEntry(path="src/nested", type="tree"),
        ]

    def get_file_content(
        self, token: GitHubToken, repository: GitHubRepositoryRef, path: str, ref: str | None
    ) -> GitHubFileContent:
        self.tokens.append(token.get_secret_value())
        assert repository == GitHubRepositoryRef(
            owner="octocat", name="trainer", default_branch="main"
        )
        assert path == "src/example.py"
        assert ref == "main"
        return GitHubFileContent(
            path="src/example.py",
            content="def process(data, value):\n    thing = value + 1\n    return thing\n",
        )


def test_connection_status_without_token_describes_targeted_import_only():
    response = GitHubService(client=FakeGitHubClient()).connection_status(None)

    assert response.status == "not_connected"
    assert response.auth_mode == "bearer_token"
    assert response.required_permissions == ["metadata:read", "contents:read"]
    assert response.capabilities == [
        "repository_browsing",
        "file_tree_browsing",
        "single_file_import",
    ]
    assert "pull" not in " ".join(response.capabilities).lower()
    assert "branch" not in " ".join(response.capabilities).lower()


def test_connection_status_validates_token_without_returning_secret():
    fake_client = FakeGitHubClient()

    response = GitHubService(client=fake_client).connection_status(
        GitHubToken.from_raw("github-secret-token")
    )

    assert fake_client.tokens == ["github-secret-token"]
    assert response.status == "connected"
    assert response.account is not None
    assert response.account.login == "octocat"
    assert "github-secret-token" not in response.model_dump_json()


def test_list_repositories_maps_client_results():
    fake_client = FakeGitHubClient()

    response = GitHubService(client=fake_client).list_repositories(
        GitHubToken.from_raw("github-secret-token")
    )

    assert fake_client.tokens == ["github-secret-token"]
    assert response.model_dump() == {
        "repos": [
            {"id": "123", "name": "trainer", "owner": "octocat"},
            {"id": "456", "name": "practice", "owner": "octo-org"},
        ]
    }
    assert "github-secret-token" not in response.model_dump_json()


def test_list_tree_maps_directory_entries_without_content():
    fake_client = FakeGitHubClient()

    response = GitHubService(client=fake_client).list_tree(
        token=GitHubToken.from_raw("github-secret-token"),
        repo_id="123",
        path="src",
        ref="main",
    )

    assert fake_client.tokens == ["github-secret-token", "github-secret-token"]
    assert response.model_dump() == {
        "repo_id": "123",
        "tree": [
            {"path": "src/example.py", "type": "blob"},
            {"path": "src/nested", "type": "tree"},
        ],
    }
    assert "content" not in response.model_dump_json()
    assert "github-secret-token" not in response.model_dump_json()


def test_fetch_file_delegates_to_single_selected_file_content():
    fake_client = FakeGitHubClient()

    response = GitHubService(client=fake_client).fetch_file(
        token=GitHubToken.from_raw("github-secret-token"),
        repo_id="123",
        path="src/example.py",
        ref="main",
    )

    assert fake_client.tokens == ["github-secret-token", "github-secret-token"]
    assert response == GitHubFileContent(
        path="src/example.py",
        content="def process(data, value):\n    thing = value + 1\n    return thing\n",
    )


def test_extract_bearer_token_accepts_authorization_header():
    token = extract_bearer_token("Bearer github-secret-token")

    assert token is not None
    assert token.get_secret_value() == "github-secret-token"


@pytest.mark.parametrize("authorization", ["Basic abc", "Bearer ", "token"])
def test_extract_bearer_token_rejects_unsupported_headers(authorization):
    with pytest.raises(ValueError, match="Authorization bearer token"):
        extract_bearer_token(authorization)


def test_github_token_masks_string_representations_and_redacts_text():
    token = GitHubToken.from_raw("github-secret-token")

    assert "github-secret-token" not in repr(token)
    assert "github-secret-token" not in str(token)
    assert token.redact("upstream echoed github-secret-token") == "upstream echoed [redacted]"
    assert redact_secret("upstream echoed github-secret-token", token) == "upstream echoed [redacted]"
