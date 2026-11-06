import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def load_local_env():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def normalize_origin(value):
    value = (value or "").strip()
    if not value:
        return ""

    parts = urlsplit(value)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        return ""
    if parts.path not in {"", "/"} or parts.query or parts.fragment or parts.username or parts.password:
        return ""

    hostname = parts.hostname.lower()
    if ":" in hostname:
        hostname = f"[{hostname}]"
    port = parts.port
    if port and not (
        (parts.scheme.lower() == "https" and port == 443)
        or (parts.scheme.lower() == "http" and port == 80)
    ):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    return urlunsplit((parts.scheme.lower(), netloc, "", "", ""))


def load_allowed_origins(raw=None):
    if raw is None:
        load_local_env()
        raw = os.getenv("CORS_ORIGINS", "")

    raw = raw.strip()
    if not raw or raw == "*":
        raise RuntimeError(
            "Set CORS_ORIGINS to your frontend origin, for example https://your-app.vercel.app"
        )

    origins = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "*" in item:
            raise RuntimeError("CORS_ORIGINS must list exact frontend origins.")
        origin = normalize_origin(item)
        if not origin:
            raise RuntimeError("CORS_ORIGINS contains an invalid origin.")
        if origin not in origins:
            origins.append(origin)

    if not origins:
        raise RuntimeError("Set CORS_ORIGINS to your frontend origin.")

    return tuple(origins)


def origin_is_allowed(origin_header, allowed):
    origin = normalize_origin(origin_header)
    return bool(origin) and origin in allowed
