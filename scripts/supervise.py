import json
import signal
import subprocess
import sys
import time
import urllib.request

from gateway import tokens


def announce_ready():
    """Print the current entry only after the authenticated upstream is healthy."""
    try:
        token = tokens.current()
        with urllib.request.urlopen(
            f"http://127.0.0.1:8890/access/{token}/health", timeout=1
        ) as response:
            if json.load(response).get("status") != "ok":
                return False
    except (OSError, ValueError, KeyError):
        return False
    try:
        entry = tokens.public_url(token)
    except ValueError:
        entry = tokens.public_url(token, "")
    print(
        "\n服务已就绪 / Service ready\n"
        f"安全入口 / Access entry: {entry}\n"
        "仅有 /access/ 路径时，将其接到 NAS 地址或反代域名后。\n"
        "If only an /access/ path is shown, append it to your NAS address or proxy domain.\n"
        "查看 / Show: pdf2zh-admin url show\n"
        "更换 / Reset: pdf2zh-admin token reset\n"
        "以上命令在容器终端执行；分享日志前请遮蔽安全入口。\n"
        "Run these commands in the container console; redact the entry before sharing logs.\n",
        flush=True,
    )
    return True


def main():
    try:
        tokens.initialize()
    except (OSError, ValueError, KeyError) as error:
        print(tokens.state_error_message(error), file=sys.stderr)
        return 1
    print("Access token loaded. View URL: docker exec zotero-pdf2zh-next pdf2zh-admin url show", flush=True)
    processes = []
    stopping = False
    announced = False
    next_readiness_check = 0.0

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        processes.append(subprocess.Popen([sys.executable, "/app/scripts/run_upstream.py"], start_new_session=True))
        processes.append(subprocess.Popen([
            sys.executable, "-m", "uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "8890",
            "--no-access-log", "--no-proxy-headers", "--log-level", "warning",
        ], start_new_session=True))
        while not stopping:
            for process in processes:
                if process.poll() is not None:
                    print("A service process exited; stopping container.", file=sys.stderr)
                    return 1
            if not announced and time.monotonic() >= next_readiness_check:
                announced = announce_ready()
                next_readiness_check = time.monotonic() + 2
            time.sleep(0.5)
        return 0
    finally:
        # Signal whole groups so translation subprocesses do not survive container shutdown.
        import os
        for process in processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        deadline = time.monotonic() + 20
        for process in processes:
            try:
                process.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()


if __name__ == "__main__":
    sys.exit(main())
