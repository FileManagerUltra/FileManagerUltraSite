#!/usr/bin/env python3
"""Throwaway SFTP server with fake content, for website screenshots of the SFTP pane.

Usage: demo_sftp_server.py <root-dir> [port]   (needs `pip install asyncssh`)
Login: user "demo", password "demo". The root directory is wiped and recreated.
"""
import asyncio
import shutil
import sys
import time
from pathlib import Path

import asyncssh

if len(sys.argv) < 2:
    sys.exit(__doc__)
root = Path(sys.argv[1]).resolve()
port = int(sys.argv[2]) if len(sys.argv) > 2 else 2222
if root.exists():
    shutil.rmtree(root)
NOW = time.time()


def put(rel, text, days_ago):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    t = NOW - days_ago * 86400
    import os
    os.utime(p, (t, t))


put("www/index.html", "<h1>Hello</h1>\n" * 40, 2)
put("www/style.css", "body { margin: 0 }\n" * 60, 9)
put("www/app.js", "console.log('hi');\n" * 120, 3)
put("www/uploads/readme.txt", "Uploads go here.\n", 20)
put("backups/db-2026-10-30.sql", "-- dump\n" * 4000, 5)
put("backups/db-2026-10-31.sql", "-- dump\n" * 4100, 4)
put("backups/db-2026-11-01.sql", "-- dump\n" * 4200, 3)
put("backups/db-2026-11-02.sql", "-- dump\n" * 4300, 2)
put("logs/nginx-access.log", "127.0.0.1 - - GET / 200\n" * 3000, 0.1)
put("logs/nginx-error.log", "2026/11/04 [warn] upstream slow\n" * 80, 0.2)
put("notes/deploy.md", "# Deploy\n\n1. Build\n2. Upload\n3. Reload\n", 7)


class Server(asyncssh.SSHServer):
    def begin_auth(self, username):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        return username == "demo" and password == "demo"


async def main():
    key = asyncssh.generate_private_key("ssh-ed25519")
    await asyncssh.listen(
        "127.0.0.1",
        port,
        server_host_keys=[key],
        server_factory=Server,
        sftp_factory=lambda chan: asyncssh.SFTPServer(chan, chroot=str(root)),
    )
    print(f"sftp://demo@127.0.0.1:{port}/ (password: demo), root {root}", flush=True)
    await asyncio.Event().wait()


asyncio.run(main())
