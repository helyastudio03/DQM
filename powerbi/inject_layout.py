"""
inject_layout.py
----------------
Injecte les 4 pages du Sales Dashboard dans un .pbix existant
en remplaçant uniquement le Report/Layout (le DataModel n'est pas touché).

Usage:
    python inject_layout.py test.pbix
    → produit sales_dashboard_final.pbix

Chaque page contient les visuels pré-positionnés et titrés.
Il suffit d'y glisser les mesures depuis le panneau Fields.
"""

import json, sys, shutil, zipfile, os, uuid

# ── utilitaires ──────────────────────────────────────────────────────────────

def uid():
    return uuid.uuid4().hex[:20]

def make_title(text):
    return json.dumps({
        "expr": {"Literal": {"Value": f"'{text}'"}}
    })

def visual_config(title="", show_title=True):
    cfg = {
        "vcObjects": {}
    }
    if title:
        cfg["vcObjects"]["title"] = [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true" if show_title else "false"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "fontSize": {"expr": {"Literal": {"Value": "12D"}}},
                "fontColor": {"solid": {"color": "#5a5a62"}}
            }
        }]
    cfg["vcObjects"]["background"] = [{
        "properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "color": {"solid": {"color": "#ffffff"}},
            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
        }
    }]
    cfg["vcObjects"]["border"] = [{
        "properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "color": {"solid": {"color": "#2b2b33"}},
            "radius": {"expr": {"Literal": {"Value": "8D"}}}
        }
    }]
    return json.dumps(cfg)

def vc(vtype, x, y, w, h, title="", z=0, tab=0):
    """Crée un visual container minimal valide."""
    return {
        "name": uid(),
        "position": {
            "x": float(x), "y": float(y), "z": float(z),
            "width": float(w), "height": float(h),
            "tabOrder": tab
        },
        "visual": {
            "visualType": vtype,
            "projections": {},
            "prototypeQuery": {"Version": 2, "From": [], "Select": [], "OrderBy": []},
            "columnProperties": {},
            "vcObjects": {},
            "objects": {}
        },
        "filters": "[]",
        "config": visual_config(title)
    }

# ── Page A : Whiteboard ──────────────────────────────────────────────────────
# 1280×720  |  KPIs top · tables mid · charts bottom

def page_a():
    W = 1280
    visuals = []

    # KPI cards  (3 × 380w × 120h)  y=30
    kpi_titles = ["MTD Sales", "Sales Plan (vs Plan Y)", "Avg Sales / Working Day"]
    for i, t in enumerate(kpi_titles):
        visuals.append(vc("card", 16 + i * 416, 30, 400, 120, t, tab=i))

    # Tables  (2 × 600w × 210h)  y=165
    visuals.append(vc("tableEx",  16, 165, 618, 210, "by Region",        tab=3))
    visuals.append(vc("tableEx", 648, 165, 618, 210, "by Business Line", tab=4))

    # Charts  (2 × 600w × 240h)  y=390
    visuals.append(vc("barChart",   16, 390, 618, 290, "Sales per Day",              tab=5))
    visuals.append(vc("lineChart", 648, 390, 618, 290, "Cumulative MTD — Y vs Y-1",  tab=6))

    return build_page("A · Whiteboard", visuals)


# ── Page B : Command Strip ────────────────────────────────────────────────────
# KPI rail gauche (220) · Charts centre (640) · Tables droite (380)

def page_b():
    visuals = []

    # KPI rail (left 220px)
    kpi_titles = ["MTD Sales", "Plan Attainment", "Avg / Day"]
    for i, t in enumerate(kpi_titles):
        visuals.append(vc("card", 14, 30 + i * 138, 218, 124, t, tab=i))

    # Charts centre
    visuals.append(vc("lineChart", 244,  30, 638, 250, "Cumulative MTD — Y vs Y-1", tab=3))
    visuals.append(vc("barChart",  244, 294, 638, 196, "Sales per Day",             tab=4))

    # Tables droite
    visuals.append(vc("tableEx", 896,  30, 372, 220, "by Region",        tab=5))
    visuals.append(vc("tableEx", 896, 264, 372, 226, "by Business Line", tab=6))

    return build_page("B · Command Strip", visuals)


# ── Page C : Plan Tracker ─────────────────────────────────────────────────────
# Jauge + cumul héro · mini KPIs · table + daily

def page_c():
    visuals = []

    # Hero row : gauge + cumul
    visuals.append(vc("gauge",     14,  30, 340, 240, "Attainment to Plan",                  tab=0))
    visuals.append(vc("lineChart", 368,  30, 900, 240, "Cumulative MTD — Actual vs Plan vs Y-1", tab=1))

    # Mini KPI strip
    mini_titles = ["MTD Sales", "Attainment %", "Avg / Day", "Forecast EOM"]
    for i, t in enumerate(mini_titles):
        visuals.append(vc("card", 14 + i * 317, 284, 305, 100, t, tab=2+i))

    # Table + daily bar
    visuals.append(vc("tableEx", 14,  398, 930, 292, "Breakdown (Region / Business Line)", tab=6))
    visuals.append(vc("barChart", 958, 398, 310, 292, "Sales per Day",                     tab=7))

    return build_page("C · Plan Tracker", visuals)


# ── Page D : Analyst Grid ─────────────────────────────────────────────────────
# KPI bar slim · 2 grandes tables · 3 sparklines

def page_d():
    visuals = []

    # KPI bar slim (full width)
    visuals.append(vc("multiRowCard", 14, 22, 1252, 80, "KPIs", tab=0))

    # Deux grandes tables
    visuals.append(vc("tableEx",  14, 116, 622, 310, "by Region",        tab=1))
    visuals.append(vc("tableEx", 648, 116, 622, 310, "by Business Line", tab=2))

    # Sparklines footer
    spark_titles = ["Sales per Day", "Cumulative MTD", "Avg / Working Day"]
    spark_types  = ["barChart", "lineChart", "lineChart"]
    for i, (t, vt) in enumerate(zip(spark_titles, spark_types)):
        visuals.append(vc(vt, 14 + i * 420, 440, 408, 256, t, tab=3+i))

    return build_page("D · Analyst Grid", visuals)


# ── Slicers page (optionnel, même slicers sur chaque page) ───────────────────

def add_slicers(page_visuals, base_tab=20):
    """Ajoute 3 slicers en haut à droite (Month, Region, BL) — à relier manuellement."""
    # On ne les ajoute pas pour éviter les conflits de noms de champs inconnus
    pass


# ── Builder ──────────────────────────────────────────────────────────────────

def build_page(display_name, visuals, width=1280, height=720):
    cfg = {
        "defaultDrillFilterOtherVisuals": True,
        "vcObjects": {
            "background": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "color": {"solid": {"color": "#fffefa"}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}],
            "outspace": [{"properties": {
                "color": {"solid": {"color": "#f7f6f0"}},
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }}]
        }
    }
    return {
        "name": uid(),
        "displayName": display_name,
        "filters": "[]",
        "ordinal": 0,
        "visualContainers": visuals,
        "config": json.dumps(cfg),
        "displayOption": 1,
        "width": width,
        "height": height
    }


# ── Injection ────────────────────────────────────────────────────────────────

def inject(src_pbix: str, dst_pbix: str):
    shutil.copy2(src_pbix, dst_pbix)

    pages = [page_a(), page_b(), page_c(), page_d()]
    # Renuméroter les ordinals
    for i, p in enumerate(pages):
        p["ordinal"] = i

    # Lire le layout existant pour conserver resourcePackages + config racine
    with zipfile.ZipFile(src_pbix, "r") as zin:
        raw_layout = zin.read("Report/Layout").decode("utf-16-le")
        old_layout = json.loads(raw_layout)

    old_layout["sections"] = pages

    new_layout_bytes = json.dumps(old_layout, ensure_ascii=False).encode("utf-16-le")

    # Réécrire uniquement Report/Layout dans le ZIP
    tmp = dst_pbix + ".tmp"
    with zipfile.ZipFile(src_pbix, "r") as zin, \
         zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "Report/Layout":
                zout.writestr(item, new_layout_bytes)
            else:
                zout.writestr(item, zin.read(item.filename))

    os.replace(tmp, dst_pbix)
    print(f"✓  {dst_pbix} créé")
    print(f"   4 pages · {sum(len(p['visualContainers']) for p in pages)} visuels pré-positionnés")
    print()
    print("Dans Power BI Desktop :")
    print("  1. Ouvrir sales_dashboard_final.pbix")
    print("  2. Glisser les mesures depuis le panneau Fields sur chaque visuel")
    print("  3. Appliquer le thème SalesDashboard_theme.json (Affichage → Thèmes → Parcourir)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "test.pbix"
    dst = "sales_dashboard_final.pbix"
    inject(src, dst)
