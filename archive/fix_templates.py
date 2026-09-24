#!/usr/bin/env python3
"""Fix prompt templates: remove literal braces (server mis-parses them as
dynamic variables) and reset custom_fields to the intended variables."""

import json
import os
import urllib.request

# Credentials come from the environment; never hardcode them in the repo.
KEY = os.environ["CUSTOM_ENDPOINT_API_KEY"]
BASE = os.environ.get("CUSTOM_ENDPOINT_URL", "http://localhost:7860/api/v1")
FLOW_ID = "0f7d6213-32a1-4f70-83ac-dce16bdbfa8f"

PT1 = """Anda analis ulasan e-commerce berbahasa Indonesia.
Tugas: normalisasi kata gaul/singkatan/huruf berulang, lalu tentukan ASPEK yang dibahas pada tiap ulasan.

Taksonomi tetap (JANGAN buat aspek baru):
product_quality, performance, battery, shipping, packaging, price, warranty, cs_service, authenticity

FORMAT OUTPUT: JSONL - satu objek JSON per baris, tanpa penjelasan, tanpa pagar markdown.
Setiap baris memakai kunci i (nomor baris data) dan kunci a (array nama aspek).
Bila ulasan tidak membahas aspek apa pun, kirim array a kosong.
Nomor baris data dimulai dari 1 (baris pertama CSV adalah header).

Daftar ulasan (kolom = review,rating,category):
{text}"""

PT2 = """Anda analis sentimen. Untuk SETIAP aspek pada setiap ulasan di bawah, tentukan sentimen, keyakinan, dan bukti kutipan.

Aturan:
- kunci p: positive | negative | neutral
- kunci c: 0.0-1.0 (rendah bila ulasan ambigu, sangat pendek, atau tanpa indikasi jelas)
- kunci e: kutipan singkat langsung dari ulasan (boleh dirapikan ejaannya), JANGAN mengarang
- Nilai PER ASPEK, bukan per rating keseluruhan.
- Bila daftar aspek suatu ulasan kosong, kirim array s kosong.

FORMAT OUTPUT: JSONL saja, tanpa pagar markdown, tanpa penjelasan.
Setiap baris memakai kunci i, lalu kunci s berisi array objek dengan kunci a, p, c, e.

Hasil ekstraksi aspek (JSONL):
{aspects}

Ulasan asli (kolom = review,rating,category):
{reviews}"""

PT3 = """Anda konsultan operasional UMKM gadget. Berikut hasil skoring sentimen per aspek dari 300 ulasan produk (laptop, handphone, tablet) di marketplace Indonesia.

Buat laporan untuk seller yang berisi:
1. Distribusi sentimen per aspek (jumlah positif/negatif/netral)
2. 3 kekuatan utama produk
3. 3 kelemahan terbanyak + solusi praktis untuk masing-masing
4. Daftar ulasan ber-keyakinan rendah yang perlu verifikasi manusia
5. Prioritas perbaikan minggu ini, urut dari yang paling berdampak

Gaya: Bahasa Indonesia formal, ramah, actionable. Boleh memakai bullet point.
Jangan mengulang analisis - hanya rangkum dan rekomendasikan dari data di bawah.

Data skoring (JSONL):
{sentiment}"""

SPEC = {
    "pt1": (PT1, ["text"]),
    "pt2": (PT2, ["aspects", "reviews"]),
    "pt3": (PT3, ["sentiment"]),
}


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


def dyn(name):
    return {"name": name, "type": "str", "value": "", "display_name": name,
            "advanced": False, "multiline": True, "input_types": ["Message"]}


def main():
    flow = get(f"/flows/{FLOW_ID}")
    fixed = 0
    for n in flow["data"]["nodes"]:
        if n["data"].get("type") != "Prompt Template":
            continue
        nid = n["id"]
        if nid.startswith("PT1") or nid == "Prompt Template-3QOua":
            key = "pt1"
        elif nid.startswith("PT2") or nid == "Prompt Template-HHECz":
            key = "pt2"
        elif nid.startswith("PT3") or nid == "Prompt Template-1T3hl":
            key = "pt3"
        else:
            continue

        text, vars_ = SPEC[key]
        t = n["data"]["node"]["template"]
        t["template"] = {"name": "template", "type": "prompt", "value": text,
                         "display_name": "Template", "required": False}
        # drop every dynamic var, then re-add only the intended ones
        for k in list(t):
            if k in ("_type", "code", "template", "tool_placeholder",
                     "use_double_brackets", "custom_fields"):
                continue
            t.pop(k)
        for v in vars_:
            t[v] = dyn(v)
        t["custom_fields"] = {"template": list(vars_)}
        t["use_double_brackets"] = {"name": "use_double_brackets", "type": "bool",
                                    "value": False, "display_name": "Use Double Brackets",
                                    "advanced": True}
        fixed += 1

    print(f"fixed {fixed} prompt templates")
    patch_flow(FLOW_ID, flow)

    check = get(f"/flows/{FLOW_ID}")
    for n in check["data"]["nodes"]:
        if n["data"].get("type") == "Prompt Template":
            t = n["data"]["node"]["template"]
            print(f"  {n['id']}: custom_fields={t.get('custom_fields')}")


if __name__ == "__main__":
    main()
