"""Static server for bench/, plus /slow/<ms>/<path>: the same file, served
after a deliberate delay, to simulate a slow API call.

    python -m webfidelity.server 8765
"""

import functools
import http.server
import json
import os
import re
import sys
import threading
import time

ROOT = "bench"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        log = os.environ.get("WF_REQUEST_LOG")
        if log:
            with open(log, "a") as f:
                f.write(json.dumps({"t": time.time(), "path": self.path,
                                    "ua": self.headers.get("User-Agent", "")}) + "\n")
        m = re.match(r"/slow/(\d+)(/.*)", self.path)
        if m:
            time.sleep(min(int(m.group(1)), 10000) / 1000)
            self.path = m.group(2)
        super().do_GET()

    def log_message(self, *a):
        pass


def start(port, background=True):
    handler = functools.partial(Handler, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    if background:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    else:
        srv.serve_forever()
    return f"http://127.0.0.1:{port}/"


if __name__ == "__main__":
    start(int(sys.argv[1]) if len(sys.argv) > 1 else 8765, background=False)
