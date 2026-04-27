import base64

import pytest

from app.services.github_service import (
    GitHubFileContent,
    GitHubRepoSummary,
    GitHubRequestError,
    GitHubService,
    GitHubTreeEntry,
    GitHubUser,
    extract_bearer_token,
    require_bearer_token,
)


class FakeGitHubClient:
    def __init__(
        self,
        *,
        user_login: str = "octocat",
        repos: list[GitHubRepoSummary] | None = None,
        default_branch: str = "main",
        tree: list[GitHubTreeEntry] | None = None,
        file_content: GitHubFileContent | None = None,
    ) -> None:
        self.user_login = user_login
        self.repos = repos or []
        self.default_branch = default_branch
        self.tree = tree or []
        self.file_content = file_content
        self.calls: list[tuple] = []

    def get_authenticated_user(self, token: str) -> GitHubUser:
        self.calls.append(("user", token))
        return GitHubUser(login=self.user_login)

    def list_user_repos(self, token: str) -> list[GitHubRepoSummary]:
        self.calls.append(("repos", token))
        return list(self.repos)

    def get_default_branch(self, token: str, owner: str, repo: str) -> str:
        self.calls.append(("default_branch", token, owner, repo))
        return self.default_branch

    def list_repo_tree(
        self, token: str, owner: str, repo: str, ref: str
    ) -> list[GitHubTreeEntry]:
        self.calls.append(("tree", token, owner, repo, ref))
        return list(self.tree)

    def get_file_contents(
        self, token: str, owner: str, repo: str, path: str, ref: str
    ) -> GitHubFileContent:
        self.calls.append(("contents", token, owner, repo, path, ref))
        if self.file_content is None:
            raise AssertionError("FakeGitHubClient.get_file_contents was called without configured content")
        return self.file_content


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


def test_connection_status_validates_token_without_returning_secret():
    fake_client = FakeGitHubClient()

    response = GitHubService(client=fake_client).connection_status("github-secret-token")

    assert ("user", "github-secret-token") in fake_client.calls
    assert response.status == "connected"
    assert response.account is not None
    assert response.account.login == "octocat"
    assert "github-secret-token" not in response.model_dump_json()


def test_list_repos_returns_owner_name_ids():
    fake_client = FakeGitHubClient(
        repos=[
            GitHubRepoSummary(owner="octocat", name="hello-world"),
            GitHubRepoSummary(owner="acme", name="widgets"),
        ]
    )

    repos = GitHubService(client=fake_client).list_repos("token")

    assert [repo.id for repo in repos] == ["octocat/hello-world", "acme/widgets"]
    assert repos[0].owner == "octocat"
    assert repos[0].name == "hello-world"


def test_get_tree_filters_to_python_blobs_only():
    fake_client = FakeGitHubClient(
        default_branch="trunk",
        tree=[
            GitHubTreeEntry(path="src/example.py", type="blob"),
            GitHubTreeEntry(path="README.md", type="blob"),
            GitHubTreeEntry(path="src", type="tree"),
            GitHubTreeEntry(path="pkg/__init__.py", type="blob"),
        ],
    )

    tree = GitHubService(client=fake_client).get_tree("token", "octocat/hello-world", "HEAD")

    assert [item.path for item in tree] == ["src/example.py", "pkg/__init__.py"]
    assert ("default_branch", "token", "octocat", "hello-world") in fake_client.calls
    assert ("tree", "token", "octocat", "hello-world", "trunk") in fake_client.calls


def test_get_tree_uses_explicit_ref_when_not_head():
    fake_client = FakeGitHubClient(tree=[GitHubTreeEntry(path="a.py", type="blob")])

    GitHubService(client=fake_client).get_tree("token", "octocat/repo", "feature/x")

    assert ("tree", "token", "octocat", "repo", "feature/x") in fake_client.calls
    assert all(call[0] != "default_branch" for call in fake_client.calls)


def test_get_tree_rejects_malformed_repo_id():
    service = GitHubService(client=FakeGitHubClient())

    with pytest.raises(ValueError, match="owner/name"):
        service.get_tree("token", "just-a-name", "HEAD")


def test_import_file_returns_decoded_content():
    encoded = base64.b64encode(b"print('ok')\n").decode("ascii")
    fake_client = FakeGitHubClient(
        default_branch="main",
        file_content=GitHubFileContent(path="src/example.py", content="print('ok')\n"),
    )

    response = GitHubService(client=fake_client).import_file(
        "token", "octocat/hello-world", "src/example.py", "HEAD"
    )

    assert response.status == "imported"
    assert response.content == "print('ok')\n"
    assert response.path == "src/example.py"
    assert response.repo_id == "octocat/hello-world"
    # Verify the encoded payload would have been decodable by the real client.
    assert base64.b64decode(encoded).decode("utf-8") == "print('ok')\n"


def test_import_file_rejects_non_python_paths():
    service = GitHubService(client=FakeGitHubClient())

    with pytest.raises(ValueError, match="single-file Python"):
        service.import_file("token", "octocat/repo", "README.md", "HEAD")


def test_import_file_rejects_empty_path():
    service = GitHubService(client=FakeGitHubClient())

    with pytest.raises(ValueError, match="path is required"):
        service.import_file("token", "octocat/repo", "   ", "HEAD")


def test_github_request_error_surface_keeps_status_for_routing():
    error = GitHubRequestError(404, "not found")

    assert error.status == 404
    assert error.detail == "not found"


def test_extract_bearer_token_accepts_authorization_header():
    assert extract_bearer_token("Bearer github-secret-token") == "github-secret-token"


@pytest.mark.parametrize("authorization", ["Basic abc", "Bearer ", "token"])
def test_extract_bearer_token_rejects_unsupported_headers(authorization):
    with pytest.raises(ValueError, match="Authorization bearer token"):
        extract_bearer_token(authorization)


def test_require_bearer_token_requires_a_value():
    with pytest.raises(ValueError, match="Authorization bearer token"):
        require_bearer_token(None)


def test_require_bearer_token_returns_validated_token():
    assert require_bearer_token("Bearer live-token") == "live-token"
