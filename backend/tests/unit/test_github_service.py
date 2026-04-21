import pytest

from app.services.github_service import GitHubService, GitHubUser, extract_bearer_token


class FakeGitHubClient:
    def __init__(self) -> None:
        self.tokens: list[str] = []

    def get_authenticated_user(self, token: str) -> GitHubUser:
        self.tokens.append(token)
        return GitHubUser(login="octocat")


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

    response = GitHubService(client=fake_client).connection_status("github-secret-token")

    assert fake_client.tokens == ["github-secret-token"]
    assert response.status == "connected"
    assert response.account is not None
    assert response.account.login == "octocat"
    assert "github-secret-token" not in response.model_dump_json()


def test_extract_bearer_token_accepts_authorization_header():
    assert extract_bearer_token("Bearer github-secret-token") == "github-secret-token"


@pytest.mark.parametrize("authorization", ["Basic abc", "Bearer ", "token"])
def test_extract_bearer_token_rejects_unsupported_headers(authorization):
    with pytest.raises(ValueError, match="Authorization bearer token"):
        extract_bearer_token(authorization)
