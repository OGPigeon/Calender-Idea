"""JWT verification against Clerk's JWKS endpoint."""
import os
import jwt

JWKS_URL = os.environ.get("CLERK_JWKS_URL", "")
_client = None


def _get_client() -> jwt.PyJWKClient:
    """Lazy-initialize the JWKS client."""
    global _client
    if _client is None:
        _client = jwt.PyJWKClient(JWKS_URL)
    return _client


def get_user_id(request) -> str | None:
    """Extract and verify the Clerk JWT from the Authorization header.

    Returns the user's Clerk ID on success, 'local' when no JWKS_URL is
    configured (dev mode), or None when the token is missing or invalid.
    """
    if not JWKS_URL:
        return "local"

    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None

    token = header[7:]
    try:
        signing_key = _get_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"])
        return payload.get("sub")
    except Exception:
        return None
