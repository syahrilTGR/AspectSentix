#!/usr/bin/env python3
"""Restore the 'code' field on every cloned node.

build_flow.py stripped template.code to slim the payload, but Langflow needs
it to instantiate nodes (especially the custom NineRouterLLM). Source code is
recovered from the pre-rebuild flow snapshot f2.json.
"""

import json
import os
import urllib.request

# Credentials come from the environment; never hardcode them in the repo.
KEY = os.environ["CUSTOM_ENDPOINT_API_KEY"]
BASE = os.environ.get("CUSTOM_ENDPOINT_URL", "http://localhost:7860/api/v1")
FLOW = "0f7d6213-32a1-4f70-83ac-dce16bdbfa8f"
SNAPSHOT = "/tmp/f2.json"   # captured before rebuild; still has original code fields


def get(path):
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"x-api-key": KEY, "Accept": "application/json", "Accept-Encoding": "identity"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def patch_flow(flow_id, payload):
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"{BASE}/flows/{flow_id}", data=data, method="PATCH",
        headers={"x-api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def main():
    snap = json.load(open(SNAPSHOT, encoding="utf-8"))
    code_by_type = {}
    for n in snap["data"]["nodes"]:
        t = n["data"].get("type")
        code = n["data"]["node"]["template"].get("code")
        if t and code:
            code_by_type[t] = code
    print("code recovered for types:", sorted(code_by_type))

    flow = get(f"/flows/{FLOW}")
    restored = missing = 0
    for n in flow["data"]["nodes"]:
        t = n["data"].get("type")
        tmpl = n["data"]["node"]["template"]
        if tmpl.get("code"):
            continue
        if t in code_by_type:
            tmpl["code"] = code_by_type[t]
            restored += 1
        else:
            missing += 1
            print(f"  !! no code source for {t} ({n['id']})")

    print(f"restored={restored} missing={missing}")
    if missing:
        raise SystemExit("refusing to save: some nodes still lack code")
    res = patch_flow(FLOW, flow)
    print("saved nodes=", len(res["data"]["nodes"]))


if __name__ == "__main__":
    main()
