import signal
import subprocess
import sys
import time

from gateway import tokens


def main():
    try:
        tokens.initialize()
    except (OSError, ValueError, KeyError) as error:
        print(tokens.state_error_message(error), file=sys.stderr)
        return 1
    print("Access token loaded. View URL: docker exec zotero-pdf2zh-next pdf2zh-admin url show", flush=True)
    processes = []
    stopping = False

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
