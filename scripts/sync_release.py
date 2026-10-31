#!/usr/bin/env python3
"""检查 wu155867/moviepilot-fnos-lite 的最新 GitHub Release。

若版本比 data/apps.json 新，则更新 apps.json（version / updated）。
退出码：0 = 无变化或已同步；同时打印提示。
详情页的更新日志与「当前」徽章是人工内容，需要手动补充。
"""
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "wu155867/moviepilot-fnos-lite"


def main():
    token = os.environ.get("GH_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases/latest", headers=headers
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        rel = json.load(r)

    tag = rel.get("tag_name", "")
    if not re.match(r"^v1\.\d+\.\d+", tag):
        print(f"skip: latest tag {tag!r} 不在 v1.x 范围内")
        return

    version = tag.lstrip("v")
    published = (rel.get("published_at") or "")[:10]

    apps_path = ROOT / "data" / "apps.json"
    data = json.loads(apps_path.read_text(encoding="utf-8"))
    app = data["apps"][0]

    if app.get("version") == version:
        print(f"up to date: v{version}")
        return

    old = app.get("version")
    app["version"] = version
    app["updated"] = published
    apps_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"synced: v{old} -> v{version} ({published})")
    print("NOTE: apps/moviepilot-fnos-lite.html 的更新日志与「当前」徽章需手动补充。")


if __name__ == "__main__":
    main()
