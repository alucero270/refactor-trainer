import base64
import json
from dataclasses import dataclass
from typing import Protocol
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from app.schemas.api import (
    GitHubAccount,
    GitHubConnectResponse,
    GitHubImportResponse,
    GitHubRepo,
    GitHubTreeItem,
)


GITHUB_REQUIRED_PERMISSIONS = ["metadata:read", "contents:read"]
GITHUB_IMPORT_CAPABILITIES = [
    "repository_browsing",
    "file_tree_browsing",
    "single_file_import",
]
MAX_IMPORT_BYTES = 256 * 1024


class GitHubConnectionError(RuntimeError):
    pass


class GitHubRequestError(RuntimeError):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


@dataclass(frozen=True)
class GitHubUser:
    login: str


@dataclass(frozen=True)
class GitHubRepoSummary:
    owner: str
    name: str


@dataclass(frozen=True)
class GitHubTreeEntry:
    path: str
    type: str


@dataclass(frozen=True)
class GitHubFileContent:
    path: str
    content: str


class GitHubClient(Protocol):
    def get_authenticated_user(self, token: str) -> GitHubUser:
        ...

    def list_user_repos(self, token: str) -> list[GitHubRepoSummary]:
        ...

    def get_default_branch(self, token: str, owner: str, repo: str) -> str:
        ...

    def list_repo_tree(
        self, token: str, owner: str, repo: str, ref: str
    ) -> list[GitHubTreeEntry]:
        ...

    def get_file_contents(
        self, token: str, owner: str, repo: str, path: str, ref: str
    ) -> GitHubFileContent:
        ...


class GitHubApiClient:
    def __init__(self, base_url: str = "https://api.github.com") -> None:
        self.base_url = base_url.rstrip("/")

    def get_authenticated_user(self, token: str) -> GitHubUser:
        data = self._get_json(token, "/user")
        login = str(data.get("login", "")).strip()
        if not login:
            raise GitHubConnectionError("GitHub connection response was missing the account login.")
        return GitHubUser(login=login)

    def list_user_repos(self, token: str) -> list[GitHubRepoSummary]:
        data = self._get_json(
            token,
            "/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator",
        )
        if not isinstance(data, list):
            raise GitHubRequestError(502, "GitHub repositories response was not a list.")

        repos: list[GitHubRepoSummary] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            owner_obj = entry.get("owner")
            name = entry.get("name")
            if not isinstance(owner_obj, dict) or not isinstance(name, str):
                continue
            owner_login = owner_obj.get("login")
            if not isinstance(owner_login, str) or not owner_login.strip() or not name.strip():
                continue
            repos.append(GitHubRepoSummary(owner=owner_login.strip(), name=name.strip()))
        return repos

    def get_default_branch(self, token: str, owner: str, repo: str) -> str:
        data = self._get_json(token, f"/repos/{_encode(owner)}/{_encode(repo)}")
        default_branch = data.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch.strip():
            raise GitHubRequestError(502, "GitHub repository response did not include a default branch.")
        return default_branch.strip()

    def list_repo_tree(
        self, token: str, owner: str, repo: str, ref: str
    ) -> list[GitHubTreeEntry]:
        data = self._get_json(
            token,
            f"/repos/{_encode(owner)}/{_encode(repo)}/git/trees/{_encode(ref)}?recursive=1",
        )
        tree = data.get("tree")
        if not isinstance(tree, list):
            raise GitHubRequestError(502, "GitHub tree response did not include a tree list.")

        entries: list[GitHubTreeEntry] = []
        for entry in tree:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            entry_type = entry.get("type")
            if not isinstance(path, str) or not isinstance(entry_type, str):
                continue
            entries.append(GitHubTreeEntry(path=path, type=entry_type))
        return entries

    def get_file_contents(
        self, token: str, owner: str, repo: str, path: str, ref: str
    ) -> GitHubFileContent:
        query_ref = urllib_parse.quote(ref, safe="")
        encoded_path = "/".join(_encode(segment) for segment in path.split("/") if segment)
        data = self._get_json(
            token,
            f"/repos/{_encode(owner)}/{_encode(repo)}/contents/{encoded_path}?ref={query_ref}",
        )

        if data.get("type") != "file":
            raise GitHubRequestError(400, "Only single Python file imports are supported.")

        size = data.get("size")
        if isinstance(size, int) and size > MAX_IMPORT_BYTES:
            raise GitHubRequestError(413, "Imported file exceeds the 256KB MVP limit.")

        encoding = data.get("encoding")
        raw_content = data.get("content")
        if encoding != "base64" or not isinstance(raw_content, str):
            raise GitHubRequestError(502, "GitHub file response was not base64-encoded content.")

        try:
            decoded_bytes = base64.b64decode(raw_content, validate=False)
        except ValueError as exc:
            raise GitHubRequestError(502, "GitHub file content could not be decoded.") from exc

        try:
            decoded = decoded_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GitHubRequestError(400, "Imported file is not valid UTF-8 text.") from exc

        file_path = data.get("path") if isinstance(data.get("path"), str) else path
        return GitHubFileContent(path=file_path, content=decoded)

    def _get_json(self, token: str, path: str) -> dict | list:
        request = urllib_request.Request(
            f"{self.base_url}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "refactor-trainer-mvp",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib_request.urlopen(request, timeout=15) as response:
                payload = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise GitHubConnectionError("GitHub token is not authorized for this resource.") from exc
            if exc.code == 404:
                raise GitHubRequestError(404, "GitHub resource was not found.") from exc
            raise GitHubRequestError(exc.code, f"GitHub returned HTTP {exc.code} for {path}.") from exc
        except urllib_error.URLError as exc:
            raise GitHubRequestError(502, "Could not reach GitHub.") from exc

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise GitHubRequestError(502, f"GitHub returned invalid JSON for {path}.") from exc


def _encode(segment: str) -> str:
    return urllib_parse.quote(segment, safe="")


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

    def list_repos(self, token: str) -> list[GitHubRepo]:
        summaries = self.client.list_user_repos(token)
        return [
            GitHubRepo(id=f"{summary.owner}/{summary.name}", owner=summary.owner, name=summary.name)
            for summary in summaries
        ]

    def get_tree(self, token: str, repo_id: str, ref: str) -> list[GitHubTreeItem]:
        owner, name = _parse_repo_id(repo_id)
        resolved_ref = self._resolve_ref(token, owner, name, ref)
        entries = self.client.list_repo_tree(token, owner, name, resolved_ref)
        return [
            GitHubTreeItem(path=entry.path, type=entry.type)
            for entry in entries
            if entry.type == "blob" and entry.path.lower().endswith(".py")
        ]

    def import_file(
        self, token: str, repo_id: str, path: str, ref: str
    ) -> GitHubImportResponse:
        normalized_path = path.strip().lstrip("/")
        if not normalized_path:
            raise ValueError("path is required for GitHub file import.")
        if not normalized_path.lower().endswith(".py"):
            raise ValueError("Only single-file Python imports are supported.")

        owner, name = _parse_repo_id(repo_id)
        resolved_ref = self._resolve_ref(token, owner, name, ref)
        file_content = self.client.get_file_contents(
            token, owner, name, normalized_path, resolved_ref
        )
        return GitHubImportResponse(
            repo_id=repo_id,
            path=file_content.path,
            content=file_content.content,
            status="imported",
        )

    def _resolve_ref(self, token: str, owner: str, name: str, ref: str) -> str:
        normalized = (ref or "").strip()
        if not normalized or normalized.upper() == "HEAD":
            return self.client.get_default_branch(token, owner, name)
        return normalized


def _parse_repo_id(repo_id: str) -> tuple[str, str]:
    normalized = (repo_id or "").strip()
    if "/" not in normalized:
        raise ValueError("repo_id must be in 'owner/name' form.")
    owner, _, name = normalized.partition("/")
    owner = owner.strip()
    name = name.strip()
    if not owner or not name or "/" in name:
        raise ValueError("repo_id must be in 'owner/name' form.")
    return owner, name


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None or not authorization.strip():
        return None

    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        raise ValueError("GitHub connection requires an Authorization bearer token.")

    return value.strip()


def require_bearer_token(authorization: str | None) -> str:
    token = extract_bearer_token(authorization)
    if not token:
        raise ValueError("GitHub import requires an Authorization bearer token.")
    return token
