from dataclasses import dataclass
from typing import Protocol
from urllib import error as urllib_error
from urllib import request as urllib_request

from app.schemas.api import GitHubAccount, GitHubConnectResponse


GITHUB_REQUIRED_PERMISSIONS = ["metadata:read", "contents:read"]
GITHUB_IMPORT_CAPABILITIES = [
    "repository_browsing",
    "file_tree_browsing",
    "single_file_import",
]


class GitHubConnectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubUser:
    login: str


class GitHubClient(Protocol):
    def get_authenticated_user(self, token: str) -> GitHubUser:
        ...


class GitHubApiClient:
    def __init__(self, base_url: str = "https://api.github.com") -> None:
        self.base_url = base_url.rstrip("/")

    def get_authenticated_user(self, token: str) -> GitHubUser:
        request = urllib_request.Request(
            f"{self.base_url}/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "refactor-trainer-mvp",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib_request.urlopen(request, timeout=10) as response:
                payload = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise GitHubConnectionError("GitHub connection could not be authorized.") from exc
            raise GitHubConnectionError("GitHub connection check failed.") from exc
        except urllib_error.URLError as exc:
            raise GitHubConnectionError("GitHub connection check failed.") from exc

        import json

        data = json.loads(payload)
        login = str(data.get("login", "")).strip()
        if not login:
            raise GitHubConnectionError("GitHub connection response was missing the account login.")
        return GitHubUser(login=login)


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


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None or not authorization.strip():
        return None

    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise ValueError("GitHub connection requires an Authorization bearer token.")

    return value.strip()
