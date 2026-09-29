import fcntl
import errno
import json
import os
import re
import secrets
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit


def state_dir():
    return Path(os.environ.get("GATEWAY_STATE_DIR", "/app/gateway/state"))


def state_error_message(error):
    location = state_dir()
    if isinstance(error, OSError):
        reason = errno.errorcode.get(error.errno, "IO_ERROR")
        return (
            f"Cannot access token state at {location}: {reason}. "
            f"Process UID/GID={os.geteuid()}:{os.getegid()}. "
            "Check that the mount is read-write and its directory and existing "
            "auth.json/.lock files are writable by this user. "
            "For host-folder mounts, fix host ownership/ACLs before retrying; "
            "token reset cannot repair mount permissions."
        )
    return (
        f"Invalid token state at {location}/auth.json. "
        "Restore a valid backup or explicitly run pdf2zh-admin token reset "
        "as the service user after checking mount permissions."
    )


@contextmanager
def locked(directory, exclusive=False):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(directory / ".lock", os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield


def read_unlocked(directory):
    data = json.loads((directory / "auth.json").read_text())
    if not isinstance(data, dict):
        raise ValueError("Invalid token state")
    value = data.get("token")
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", value):
        raise ValueError("Invalid token state; restore the file or explicitly reset it")
    return value


def write_unlocked(directory, token):
    descriptor, temporary = tempfile.mkstemp(prefix=".auth-", dir=directory)
    try:
        with os.fdopen(descriptor, "w") as output:
            json.dump({"token": token}, output)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, directory / "auth.json")
        dir_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize(directory=None):
    directory = directory or state_dir()
    with locked(directory, exclusive=True):
        if (directory / "auth.json").exists():
            return read_unlocked(directory)
        token = secrets.token_urlsafe(32)
        write_unlocked(directory, token)
        return token


def current(directory=None):
    directory = directory or state_dir()
    with locked(directory):
        return read_unlocked(directory)


def reset(directory=None):
    directory = directory or state_dir()
    with locked(directory, exclusive=True):
        token = secrets.token_urlsafe(32)
        write_unlocked(directory, token)
        return token


def public_base(value=None):
    value = (os.environ.get("PUBLIC_BASE_URL", "") if value is None else value).strip().rstrip("/")
    if not value:
        return ""
    parts = urlsplit(value)
    if (parts.scheme not in ("http", "https") or not parts.hostname or parts.username
            or parts.password or parts.path or parts.query or parts.fragment
            or any(character.isspace() for character in value)):
        raise ValueError("Use an HTTP(S) origin without credentials or a path")
    parts.port
    return value


def public_url(token, base_url=None):
    return f"{public_base(base_url)}/access/{token}"
