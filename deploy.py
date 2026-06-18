"""
Refresh the SHOPPA Fund hub and push it to GitHub Pages (shoppafund.github.io).

Regenerates the commodity cockpit (most recent session), copies the latest app
HTML into the hub, fires the rotation alerts, then commits & pushes. Run daily
(Windows Task Scheduler / cron) to keep the live site current.

  python deploy.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone

LP = r"C:\SHOPPA\Liquidity Print Map"
SITE = r"C:\SHOPPA\shoppafund-site"


def most_recent_weekday():
    d = datetime.now(timezone.utc) - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def run(cmd, cwd, check=True):
    print(">", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check)


def main():
    last = most_recent_weekday()
    # 1) regenerate cockpit for the latest session
    run(["python", "commodity_cockpit.py", "--last", last], LP)
    shutil.copy(os.path.join(LP, "commodity_cockpit.html"),
                os.path.join(SITE, "cockpit", "index.html"))
    # 2) refresh the report + flow chart (best-effort)
    for src, dst in [("commodities_report.html", ("report", "index.html"))]:
        s = os.path.join(LP, src)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(SITE, *dst))
    # 3) rotation alerts (pings Discord if DISCORD_WEBHOOK_URL is set)
    run(["python", "cockpit_alerts.py"], LP, check=False)
    # 4) commit & push
    run(["git", "add", "-A"], SITE)
    r = subprocess.run(["git", "-c", "user.email=dev@shoppa.local", "-c", "user.name=SHOPPA",
                        "commit", "-m", f"auto: refresh {last}"], cwd=SITE)
    if r.returncode == 0:
        run(["git", "push", "origin", "main"], SITE)
        print(f"\nLive: https://shoppafund.github.io/  (refreshed {last})")
    else:
        print("nothing changed since last deploy")


if __name__ == "__main__":
    main()
