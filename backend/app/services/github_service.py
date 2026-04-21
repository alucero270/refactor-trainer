from dataclasses import dataclass
import json
from typing import Protocol
from urllib import parse as urllib_parse
from urllib import error as urllib_error
from urllib import request as urllib_request

from app.schemas.api import (
    GitHubAccount,
    GitHubConnectResponse,
    GitHubRepo,
    GitHubRepoTreeResponse,
    GitHubReposResponse,
    GitHubTreeItem,
)


GITHUB_REQUIRED_PERMISSIONS = ["metadata:read", "contents:read"]
GITHUB_IMPORT_CAPABILITIES = [
    "repository_browsing",
    "file_tree_browsing",
    "single_file_import",
]


class GitHubConnectionError(RuntimeError):
    pass


class GitHubApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True)
class GitHubUser:
    login: str


@dataclass(frozen=True)
class GitHubRepository:
    id: str
    name: str
    owner: str


@dataclass(frozen=True)
class GitHubRepositoryRef:
    owner: str
    name: str
    default_branch: str


@dataclass(frozen=True)
class GitHubTreeEntry:
    path: str
    type: str


class GitHubClient(Protocol):
    def get_authenticated_user(self, token: str) -> GitHubUser:
        ...

    def list_repositories(self, token: str) -> list[GitHubRepository]:
        ...

    def get_repository(self, token: str, repo_id: str) -> GitHubRepositoryRef:
        ...

    def list_directory(
        self, token: str, repository: GitHubRepositoryRef, path: str, ref: str | None
    ) -> list[GitHubTreeEntry]:
        ...


class GitHubApiClient:
    def __init__(self, base_url: str = "https://api.github.com") -> None:
        self.base_url = base_url.rstrip("/")

    def get_authenticated_user(self, token: str) -> GitHubUser:
        data = self._request_json(token, "/user")
        login = str(data.get("login", "")).strip()
        if not login:
            raise GitHubConnectionError("GitHub connection response was missing the account login.")
        return GitHubUser(login=login)

    def list_repositories(self, token: str) -> list[GitHubRepository]:
        data = self._request_json(
            token,
            "/user/repos",
            {
                "affiliation": "owner,collaborator,organization_member",
                "per_page": "100",
                "sort": "updated",
            },
        )
        if not isinstance(data, list):
            raise GitHubApiError(502, "GitHub repository listing returned an unexpected response.")

        repositories: list[GitHubRepository] = []
        for item in data:
            owner = item.get("owner", {}).get("login", "")
            repositories.append(
                GitHubRepository(
                    id=str(item.get("id", "")).strip(),
                    name=str(item.get("name", "")).strip(),
                    owner=str(owner).strip(),
                )
            )
        return [repo for repo in repositories if repo.id and repo.name and repo.owner]

    def get_repository(self, token: str, repo_id: str) -> GitHubRepositoryRef:
        data = self._request_json(token, f"/repositories/{urllib_parse.quote(repo_id)}")
        owner = str(data.get("owner", {}).get("login", "")).strip()
        name = str(data.get("name", "")).strip()
        default_branch = str(data.get("default_branch", "")).strip()
        if not owner or not name:
            raise GitHubApiError(404, "GitHub repository was not found.")
        return GitHubRepositoryRef(
            owner=owner,
            name=name,
            default_branch=default_branch or "HEAD",
        )

    def list_directory(
        self, token: str, repository: GitHubRepositoryRef, path: str, ref: str | None
    ) -> list[GitHubTreeEntry]:
        clean_path = path.strip("/")
        encoded_path = "/".join(
            urllib_parse.quote(part) for part in clean_path.split("/") if part
        )
        endpoint = f"/repos/{repository.owner}/{repository.name}/contents"
        if encoded_path:
            endpoint = f"{endpoint}/{encoded_path}"

        data = self._request_json(token, endpoint, {"ref": ref or repository.default_branch})
        if not isinstance(data, list):
            raise GitHubApiError(400, "GitHub tree browsing requires a directory path.")

        entries: list[GitHubTreeEntry] = []
        for item in data:
            item_type = item.get("type")
            if item_type == "file":
                tree_type = "blob"
            elif item_type == "dir":
                tree_type = "tree"
            else:
                continue
            entries.append(
                GitHubTreeEntry(
                    path=str(item.get("path", "")).strip(),
                    type=tree_type,
                )
            )
        return [entry for entry in entries if entry.path]

    def _request_json(
        self, token: str, endpoint: str, query: dict[str, str] | None = None
    ) -> object:
        url = f"{self.base_url}{endpoint}"
        if query:
            url = f"{url}?{urllib_parse.urlencode(query)}"

        request = urllib_request.Request(url, headers=self._headers(token))
        try:
            with urllib_request.urlopen(request, timeout=10) as response:
                payload = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise GitHubConnectionError("GitHub connection could not be authorized.") from exc
            if exc.code == 404:
                raise GitHubApiError(404, "GitHub resource was not found.") from exc
            raise GitHubConnectionError("GitHub connection check failed.") from exc
        except urllib_error.URLError as exc:
            raise GitHubConnectionError("GitHub connection check failed.") from exc

        return json.loads(payload)

    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "refactor-trainer-mvp",
            "X-GitHub-Api-Version": "2022-11-28",
        }


class GitHubService:
    def __init__(self, client: GitHubClient | None = None) -> None:
        self.client = client or GitHubApiClient()

    def connection_status(self, token: str | None) -> GitHubConnectResponse:
        if not token:
            return GitHubConnectResponse(
                status="not_connected",
                auth_mode="bearer_token",
                required_permissions=GITHUB_REQUIRED_PERMISSIONS,
                capabilities=GITHUB_IMPORT_CAPABILITIES,
                message="Provide a GitHub bearer token to enable targeted single-file import.",
            )

        user = self.client.get_authenticated_user(token)
        return GitHubConnectResponse(
            status="connected",
            auth_mode="bearer_token",
            required_permissions=GITHUB_REQUIRED_PERMISSIONS,
            capabilities=GITHUB_IMPORT_CAPABILITIES,
            account=GitHubAccount(login=user.login),
            message="GitHub targeted import is enabled for repository browsing and single-file import.",
        )

    def list_repositories(self, token: str) -> GitHubReposResponse:
        repos = [
            GitHubRepo(id=repo.id, name=repo.name, owner=repo.owner)
            for repo in self.client.list_repositories(token)
        ]
        return GitHubReposResponse(repos=repos)

    def list_tree(
        self, token: str, repo_id: str, path: str = "", ref: str | None = None
    ) -> GitHubRepoTreeResponse:
        repository = self.client.get_repository(token, repo_id)
        entries = self.client.list_directory(token, repository, path, ref)
        return GitHubRepoTreeResponse(
            repo_id=repo_id,
            tree=[GitHubTreeItem(path=entry.path, type=entry.type) for entry in entries],
        )


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None or not authorization.strip():
        return None

    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise ValueError("GitHub connection requires an Authorization bearer token.")

    return value.strip()
