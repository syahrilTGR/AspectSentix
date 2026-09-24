#!/usr/bin/env python3
"""Build the AspectSentix per-rating flow.

Structure: 5 rating branches (60 reviews each) x 2 LLM stages, then one
aggregator stage. Rating is isolated per branch so stage-2 output stays
within a sane token budget (~2.7K) instead of one 13K-token call.

The `NineRouterLLM` custom component is absent from the MCP registry, so
each node is deep-cloned from a working node shell over the REST API.
"""

import copy
import json
import os
import urllib.request

# Credentials come from the environment; never hardcode them in the repo.
KEY = os.environ["CUSTOM_ENDPOINT_API_KEY"]
BASE = os.environ.get("CUSTOM_ENDPOINT_URL", "http://localhost:7860/api/v1")
FLOW_ID = "0f7d6213-32a1-4f70-83ac-dce16bdbfa8f"
MSG = ["Message"]
RATINGS = ["1", "2", "3", "4", "5"]
COMBO_OPTS = ["Sak_Kapokmu", "Good", "gc/gemini-2.5-flash", "kr/qwen3-coder-next"]

FLOW_NAME = "AspectSentix_ABSA"
FLOW_DESC = (
    "ABSA untuk seller gadget UMKM: 5 cabang rating x 2 tahap LLM "
    "(ekstraksi aspek -> skoring sentimen) + 1 tahap agregasi rekomendasi"
)

# node shells we clone from (must already exist in the flow)
SHELL_FILE = "File-2bYqW"
SHELL_PT1 = "Prompt Template-3QOua"
SHELL_PT2 = "Prompt Template-HHECz"
SHELL_PT3 = "Prompt Template-1T3hl"
SHELL_LLM = "NineRouterLLM-J3nVe"
SHELL_CHAT = "ChatOutput-unu4n"


def get(path):
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"x-api-key": KEY, "Accept": "application/json", "Accept-Encoding": "identity"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def post_flow(flow_id, payload):
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"{BASE}/flows/{flow_id}",
        data=data,
        method="PATCH",
        headers={"x-api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"HTTP {e.code} {e.reason}\n{body[:3000]}")
        raise


def mk_edge(sid, src_name, src_type, did, dst_field):
    sh = {"dataType": src_type, "id": sid, "name": src_name, "output_types": MSG}
    th = {"fieldName": dst_field, "id": did, "inputTypes": MSG, "type": "str"}
    return {
        "animated": False,
        "className": "",
        "data": {"sourceHandle": sh, "targetHandle": th},
        "id": f"{sid}-{src_name}->{did}-{dst_field}",
        "selected": False,
        "source": sid,
        "sourceHandle": json.dumps(sh, separators=(",", ":")).replace('"', "œ"),
        "target": did,
        "targetHandle": json.dumps(th, separators=(",", ":")).replace('"', "œ"),
    }


def clone(shell, nid, x, y, template):
    """Clone a node shell whole (keeping every required data.node field),
    then override identity, position, and the configurable template."""
    n = copy.deepcopy(shell)
    n["id"] = nid
    n["position"] = {"x": x, "y": y}
    n["selected"] = False
    n["dragging"] = False
    n["data"]["id"] = nid
    n["data"]["showNode"] = True
    n["data"]["node"]["template"] = template
    return n


def dyn(name):
    """A materialized Prompt Template dynamic variable input."""
    return {"name": name, "type": "str", "value": "", "display_name": name,
            "advanced": False, "multiline": True, "input_types": MSG}


def llm_template(base, temperature, max_tokens):
    t = copy.deepcopy(base)
    t["temperature"] = {"name": "temperature", "type": "slider", "value": temperature,
                        "display_name": "Temperature", "advanced": False,
                        "info": "0.0 untuk JSON/kode, 0.7 untuk narasi."}
    t["max_tokens"] = {"name": "max_tokens", "type": "int", "value": max_tokens,
                       "display_name": "Max Tokens", "advanced": False}
    t["combo"] = {"name": "combo", "type": "str", "value": "Sak_Kapokmu",
                  "display_name": "COMBO", "options": COMBO_OPTS, "advanced": False}
    t["base_url"] = {"name": "base_url", "type": "str", "value": "http://localhost:20128/v1",
                     "display_name": "9Router Base URL", "advanced": False}
    t["input_value"] = {"name": "input_value", "type": "str", "value": "",
                        "display_name": "Input", "advanced": False}
    return t


def main():
    flow = get(f"/flows/{FLOW_ID}")
    shells = {n["id"]: n for n in flow["data"]["nodes"]}

    tpl = {}
    for key, nid in [("pt1", SHELL_PT1), ("pt2", SHELL_PT2), ("pt3", SHELL_PT3),
                     ("llm", SHELL_LLM), ("file", SHELL_FILE)]:
        t = copy.deepcopy(shells[nid]["data"]["node"]["template"])
        t.pop("code", None)
        tpl[key] = t
    tpl["pt2"].pop('"i"', None)  # stray var from an earlier brace-escaping bug

    nodes = []
    edges = []

    for r in RATINGS:
        x = (int(r) - 1) * 320

        fid, p1id, l1id, p2id, l2id = (f"File-R{r}", f"PT1-R{r}", f"LLM1-R{r}",
                                       f"PT2-R{r}", f"LLM2-R{r}")

        ft = copy.deepcopy(tpl["file"])
        ft["path"] = {"name": "path", "type": "FileInput", "display_name": "Files",
                      "value": f"aspectsentix/dataset/by_rating/reviews_rating_{r}.csv",
                      "fileTypes": ["csv"], "advanced": False}
        nodes.append(clone(shells[SHELL_FILE], fid, x, 0, ft))

        p1 = copy.deepcopy(tpl["pt1"])
        p1["text"] = dyn("text")
        nodes.append(clone(shells[SHELL_PT1], p1id, x, -170, p1))

        nodes.append(clone(shells[SHELL_LLM], l1id, x, -340, llm_template(tpl["llm"], 0.0, 2048)))

        p2 = copy.deepcopy(tpl["pt2"])
        p2["aspects"] = dyn("aspects")
        p2["reviews"] = dyn("reviews")
        nodes.append(clone(shells[SHELL_PT2], p2id, x, -510, p2))

        nodes.append(clone(shells[SHELL_LLM], l2id, x, -680, llm_template(tpl["llm"], 0.0, 2048)))

        edges += [
            mk_edge(fid, "message", "File", p1id, "text"),
            mk_edge(p1id, "prompt", "Prompt Template", l1id, "input_value"),
            mk_edge(l1id, "output", "NineRouterLLM", p2id, "aspects"),
            mk_edge(fid, "message", "File", p2id, "reviews"),
            mk_edge(p2id, "prompt", "Prompt Template", l2id, "input_value"),
        ]

    pt3id, llm3id = "PT3-Agg", "LLM3-Agg"
    p3 = copy.deepcopy(tpl["pt3"])
    p3["sentiment"] = dyn("sentiment")
    nodes.append(clone(shells[SHELL_PT3], pt3id, 1700, -510, p3))
    nodes.append(clone(shells[SHELL_LLM], llm3id, 1700, -680, llm_template(tpl["llm"], 0.7, 4096)))

    for r in RATINGS:
        edges.append(mk_edge(f"LLM2-R{r}", "output", "NineRouterLLM", pt3id, "sentiment"))
    edges.append(mk_edge(pt3id, "prompt", "Prompt Template", llm3id, "input_value"))
    edges.append(mk_edge(llm3id, "output", "NineRouterLLM", SHELL_CHAT, "input_value"))

    payload = {
        "name": FLOW_NAME,
        "description": FLOW_DESC,
        "id": flow["id"],
        "data": {
            "nodes": nodes,
            "edges": edges,
            "viewport": flow["data"].get("viewport", {"x": 0, "y": 0, "zoom": 1}),
        },
    }
    print(f"built nodes={len(nodes)} edges={len(edges)}")
    res = post_flow(flow["id"], payload)
    got = res.get("data", {})
    print(f"saved nodes={len(got.get('nodes', []))} edges={len(got.get('edges', []))}")


if __name__ == "__main__":
    main()
