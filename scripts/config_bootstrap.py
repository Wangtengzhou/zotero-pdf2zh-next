import shutil
import tempfile
from pathlib import Path


TEMPLATES = ("config.json.example", "config.toml.example", "venv.json.example")


def seed_config_templates(defaults=Path("/app/defaults/config"), target=Path("/app/server/config")):
    # Host-folder mounts hide image files; keep managed defaults outside the mount.
    for name in TEMPLATES:
        if not (defaults / name).is_file():
            raise FileNotFoundError(f"Missing image configuration template: {name}")
    target.mkdir(parents=True, exist_ok=True)
    for name in TEMPLATES:
        with tempfile.NamedTemporaryFile(dir=target, prefix=".template-", delete=False) as temporary:
            path = Path(temporary.name)
        try:
            shutil.copyfile(defaults / name, path)
            path.replace(target / name)
        finally:
            path.unlink(missing_ok=True)
