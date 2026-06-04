"""
inject_layout.py  v2
--------------------
Injecte les 4 pages du Sales Dashboard dans un .pbix existant.
Seul Report/Layout est remplacé — le DataModel n'est pas touché.

Usage:
    python inject_layout.py <source.pbix>
    → produit sales_dashboard_final.pbix
"""

import json, sys, shutil, zipfile, os, uuid

# ── helpers ──────────────────────────────────────────────────────────────────

def uid():
    return uuid.uuid4().hex[:20]

def vc(vtype, x, y, w, h, title="", tab=0):
    """
    Crée un visual container au format exact attendu par Power BI Desktop.
    x/y/w/h sont à la racine ; tout le reste passe dans 'config' (JSON string).
    """
    name = uid()
    cfg = {
        "name": name,
        "layouts": [{
            "id": 0,
            "position": {
                "x": float(x), "y": float(y), "z": 0.0,
                "width": float(w), "height": float(h),
                "tabOrder": tab
            }
        }],
        "singleVisual": {
            "visualType": vtype,
            "projections": {},
            "prototypeQuery": {
                "Version": 2,
                "From": [],
                "Select": [],
                "OrderBy": []
            },
            "columnProperties": {},
            "vcObjects": {
                "background": [{
                    "properties": {
                        "show":         {"expr": {"Literal": {"Value": "true"}}},
                        "color":        {"solid": {"color": "#ffffff"}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }],
                "border": [{
                    "properties": {
                        "show":   {"expr": {"Literal": {"Value": "true"}}},
                        "color":  {"solid": {"color": "#2b2b33"}},
                        "radius": {"expr": {"Literal": {"Value": "8D"}}}
                    }
                }],
            }
        }
    }

    if title:
        cfg["singleVisual"]["vcObjects"]["title"] = [{
            "properties": {
                "show":      {"expr": {"Literal": {"Value": "true"}}},
                "text":      {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontSize":  {"expr": {"Literal": {"Value": "11D"}}},
                "fontColor": {"solid": {"color": "#5a5a62"}}
            }
        }]

    return {
        "x": float(x),
        "y": float(y),
        "z": 0.0,
        "width":  float(w),
        "height": float(h),
        "config":  json.dumps(cfg, ensure_ascii=False),
        "filters": "[]"
    }


def build_page(display_name, visuals, ordinal=0, width=1280, height=720):
    cfg = {
        "defaultDrillFilterOtherVisuals": True,
        "vcObjects": {
            "background": [{"properties": {
                "show":         {"expr": {"Literal": {"Value": "true"}}},
                "color":        {"solid": {"color": "#fffefa"}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}],
            "outspace": [{"properties": {
                "color":        {"solid": {"color": "#f7f6f0"}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        }
    }
    return {
        "name":             uid(),
        "displayName":      display_name,
        "filters":          "[]",
        "ordinal":          ordinal,
        "visualContainers": visuals,
        "config":           json.dumps(cfg, ensure_ascii=False),
        "displayOption":    1,
        "width":            width,
        "height":           height
    }


# ── Page A · Whiteboard ──────────────────────────────────────────────────────

def page_a():
    v = []
    kpi_titles = ["MTD Sales", "Sales Plan (vs Plan Y)", "Avg Sales / Working Day"]
    for i, t in enumerate(kpi_titles):
        v.append(vc("card", 16 + i * 416, 30, 400, 120, t, tab=i))
    v.append(vc("tableEx",  16, 165, 618, 210, "by Region",        tab=3))
    v.append(vc("tableEx", 648, 165, 618, 210, "by Business Line", tab=4))
    v.append(vc("barChart",  16, 390, 618, 295, "Sales per Day",             tab=5))
    v.append(vc("lineChart", 648, 390, 618, 295, "Cumulative MTD — Y vs Y-1", tab=6))
    return build_page("A · Whiteboard", v, ordinal=0)


# ── Page B · Command Strip ────────────────────────────────────────────────────

def page_b():
    v = []
    for i, t in enumerate(["MTD Sales", "Plan Attainment", "Avg / Day"]):
        v.append(vc("card", 14, 30 + i * 138, 218, 124, t, tab=i))
    v.append(vc("lineChart", 244,  30, 638, 250, "Cumulative MTD — Y vs Y-1", tab=3))
    v.append(vc("barChart",  244, 294, 638, 196, "Sales per Day",             tab=4))
    v.append(vc("tableEx",   896,  30, 372, 220, "by Region",                 tab=5))
    v.append(vc("tableEx",   896, 264, 372, 226, "by Business Line",          tab=6))
    return build_page("B · Command Strip", v, ordinal=1)


# ── Page C · Plan Tracker ─────────────────────────────────────────────────────

def page_c():
    v = []
    v.append(vc("gauge",     14,  30, 340, 240, "Attainment to Plan",                       tab=0))
    v.append(vc("lineChart", 368,  30, 898, 240, "Cumulative MTD — Actual vs Plan vs Y-1",   tab=1))
    for i, t in enumerate(["MTD Sales", "Attainment %", "Avg / Day", "Forecast EOM"]):
        v.append(vc("card", 14 + i * 317, 284, 305, 100, t, tab=2+i))
    v.append(vc("tableEx",  14,  398, 930, 292, "Breakdown by Region / Business Line", tab=6))
    v.append(vc("barChart", 958, 398, 310, 292, "Sales per Day",                       tab=7))
    return build_page("C · Plan Tracker", v, ordinal=2)


# ── Page D · Analyst Grid ─────────────────────────────────────────────────────

def page_d():
    v = []
    v.append(vc("multiRowCard", 14,  22, 1252,  80, "KPIs",             tab=0))
    v.append(vc("tableEx",      14, 116,  622, 310, "by Region",        tab=1))
    v.append(vc("tableEx",     648, 116,  622, 310, "by Business Line", tab=2))
    for i, (t, vt) in enumerate(zip(
        ["Sales per Day", "Cumulative MTD", "Avg / Working Day"],
        ["barChart", "lineChart", "lineChart"]
    )):
        v.append(vc(vt, 14 + i * 420, 440, 408, 256, t, tab=3+i))
    return build_page("D · Analyst Grid", v, ordinal=3)


# ── Injection ─────────────────────────────────────────────────────────────────

def inject(src_pbix: str, dst_pbix: str):
    # Lire le layout d'origine pour conserver resourcePackages + config racine
    with zipfile.ZipFile(src_pbix, "r") as zin:
        raw = zin.read("Report/Layout").decode("utf-16-le")
        layout = json.loads(raw)

    pages = [page_a(), page_b(), page_c(), page_d()]
    layout["sections"] = pages

    new_layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")

    # Réécrire le ZIP en conservant exactement les mêmes paramètres de compression
    tmp = dst_pbix + ".tmp"
    with zipfile.ZipFile(src_pbix, "r") as zin, \
         zipfile.ZipFile(tmp, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "Report/Layout":
                # Même type de compression que l'original
                out_info = zipfile.ZipInfo(item.filename)
                out_info.compress_type = item.compress_type
                zout.writestr(out_info, new_layout_bytes)
            else:
                out_info = zipfile.ZipInfo(item.filename)
                out_info.compress_type = item.compress_type
                zout.writestr(out_info, data)

    os.replace(tmp, dst_pbix)

    total_vc = sum(len(p["visualContainers"]) for p in pages)
    print(f"✓  {dst_pbix}")
    print(f"   4 pages · {total_vc} visuels")
    print(f"   DataModel : intact ({os.path.getsize(src_pbix)} → {os.path.getsize(dst_pbix)} bytes)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "test.pbix"
    dst = "sales_dashboard_final.pbix"
    inject(src, dst)
