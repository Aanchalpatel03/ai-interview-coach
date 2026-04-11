import secrets
import time
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

STATE_TTL_SECONDS = 600
_oauth_states: dict[str, tuple[str, float]] = {}


@dataclass(frozen=True)
class OAuthProviderConfig:
    name: str
    client_id: str | None
    client_secret: str | None
    authorize_url: str
    token_url: str
    scope: str


PROVIDERS = {
    "google": OAuthProviderConfig(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scope="openid email profile",
    ),
    "github": OAuthProviderConfig(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        scope="read:user user:email",
    ),
}


def _cleanup_states() -> None:
    now = time.time()
    expired_states = [state for state, (_, expires_at) in _oauth_states.items() if expires_at <= now]
    for state in expired_states:
        _oauth_states.pop(state, None)


def get_provider(provider: str) -> OAuthProviderConfig:
    config = PROVIDERS.get(provider.lower())
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported OAuth provider")
    if not config.client_id or not config.client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{config.name.title()} OAuth is not configured on the server",
        )
    return config


def get_callback_url(provider: str) -> str:
    return f"{settings.backend_base_url}{settings.api_v1_str}/auth/oauth/{provider}/callback"


def get_frontend_callback_url(*, token: str | None = None, error: str | None = None) -> str:
    query = urlencode({key: value for key, value in {"token": token, "error": error}.items() if value})
    return f"{settings.frontend_url}/auth/oauth-callback{f'?{query}' if query else ''}"


def build_oauth_start_url(provider: str) -> str:
    config = get_provider(provider)
    _cleanup_states()
    state = secrets.token_urlsafe(24)
    _oauth_states[state] = (config.name, time.time() + STATE_TTL_SECONDS)
    query = urlencode(
        {
            "client_id": config.client_id,
            "redirect_uri": get_callback_url(config.name),
            "response_type": "code",
            "scope": config.scope,
            "state": state,
            **({"access_type": "offline", "prompt": "consent"} if config.name == "google" else {}),
        }
    )
    return f"{config.authorize_url}?{query}"


def validate_state(provider: str, state: str) -> None:
    _cleanup_states()
    stored = _oauth_states.pop(state, None)
    if not stored or stored[0] != provider.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")


async def exchange_code_for_profile(provider: str, code: str) -> dict[str, str]:
    config = get_provider(provider)
    async with httpx.AsyncClient(timeout=20) as client:
        if config.name == "google":
            token_response = await client.post(
                config.token_url,
                data={
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": get_callback_url(config.name),
                },
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
            profile_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_response.raise_for_status()
            profile = profile_response.json()
            email = profile.get("email")
            name = profile.get("name") or email
        else:
            token_response = await client.post(
                config.token_url,
                headers={"Accept": "application/json"},
                data={
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "code": code,
                    "redirect_uri": get_callback_url(config.name),
                },
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
            profile_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            profile_response.raise_for_status()
            profile = profile_response.json()
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            emails_response.raise_for_status()
            email = next((item["email"] for item in emails_response.json() if item.get("primary")), None)
            name = profile.get("name") or profile.get("login") or email

    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No verified email returned by provider")

    return {"email": email, "name": name or email}
