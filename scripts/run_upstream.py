import runpy
import sys

from scripts.config_bootstrap import seed_config_templates

sys.path.insert(0, "/app/server")
from utils import auto_update

seed_config_templates()
# Container updates are image replacements; startup must not contact notice servers.
auto_update.fetch_and_show_notices = lambda *args, **kwargs: None
sys.argv = ["/app/server/server.py", "--host=127.0.0.1", "--port=8891",
            "--enable_venv=False", "--check_update=False"]
runpy.run_path("/app/server/server.py", run_name="__main__")
