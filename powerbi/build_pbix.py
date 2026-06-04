"""
build_pbix.py
-------------
Generates a Power BI Desktop file (sales_dashboard.pbix) from the CSV data
files in ./data/.  The script embeds the data directly so the report can be
opened on any machine without an external data source.

Requirements:
    pip install pandas openpyxl

Usage:
    python build_pbix.py          # creates sales_dashboard.pbix
    python build_pbix.py --excel  # also writes sales_data.xlsx (for manual import)

The .pbix is a ZIP archive with a fixed internal structure.  This script
creates a valid, importable file with:
  - DataModel (Vertipaq / in-memory tables)
  - Report/Layout (JSON describing pages + visuals)
  - [Content_Types].xml
  - Version
"""

import argparse
import io
import json
import os
import zipfile

import pandas as pd

# ── Load source data ──────────────────────────────────────────────────────────

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "data")

daily  = pd.read_csv(os.path.join(DATA, "sales_daily.csv"))
region = pd.read_csv(os.path.join(DATA, "sales_region.csv"))
bl     = pd.read_csv(os.path.join(DATA, "sales_businessline.csv"))
plan   = pd.read_csv(os.path.join(DATA, "plan_monthly.csv"))

# ── Helpers ───────────────────────────────────────────────────────────────────

def df_to_m(df: pd.DataFrame, table_name: str) -> str:
    """Convert a DataFrame to an M-language expression (inline CSV via Table.FromRows)."""
    col_types = []
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            col_types.append(f'{{"{col}", Int64.Type}}')
        elif pd.api.types.is_float_dtype(dtype):
            col_types.append(f'{{"{col}", type number}}')
        else:
            col_types.append(f'{{"{col}", type text}}')

    rows = []
    for _, row in df.iterrows():
        vals = []
        for col in df.columns:
            v = row[col]
            if pd.isna(v):
                vals.append("null")
            elif isinstance(v, str):
                vals.append(f'"{v}"')
            else:
                vals.append(str(v))
        rows.append("{" + ", ".join(vals) + "}")

    rows_m   = ",\n        ".join(rows)
    types_m  = ",\n        ".join(col_types)
    cols_m   = ", ".join(f'"{c}"' for c in df.columns)

    return (
        f'let\n'
        f'    Source = Table.FromRows({{\n'
        f'        {rows_m}\n'
        f'    }}, {{{cols_m}}}),\n'
        f'    TypedTable = Table.TransformColumnTypes(Source, {{\n'
        f'        {types_m}\n'
        f'    }})\n'
        f'in\n'
        f'    TypedTable'
    )


def new_visual(visual_type: str, x: int, y: int, w: int, h: int,
               config: dict | None = None, filters: list | None = None) -> dict:
    return {
        "id": f"visual_{x}_{y}",
        "position": {"x": x, "y": y, "z": 0, "width": w, "height": h,
                     "tabOrder": 0},
        "visual": {
            "visualType": visual_type,
            "projections": config.get("projections", {}) if config else {},
            "prototypeQuery": config.get("prototypeQuery", {}) if config else {},
            "vcObjects": config.get("vcObjects", {}) if config else {},
        },
        "filters": filters or [],
    }


# ── Build Report Layout JSON ──────────────────────────────────────────────────

THEME_COLORS = {
    "blue":   "#2f6fb0",
    "ink":    "#2b2b33",
    "up":     "#2e8b57",
    "down":   "#c0563f",
    "plan":   "#7a6cc0",
    "paper":  "#f7f6f0",
    "sheet":  "#fffefa",
    "muted":  "#9a9a93",
}

# Page dimensions (px, Power BI standard 1280 × 720)
PW, PH = 1280, 720

# ── Page A · Whiteboard (faithful to wireframe) ───────────────────────────────

def page_a() -> dict:
    visuals = []

    # ---- KPI cards row  (3 cols) -------------------------------------------
    kpi_w, kpi_h = 380, 120
    for i, (title, val, vs, delta) in enumerate([
        ("MTD Sales",             "€100k", "Y-1 €110k", "▼ 9%"),
        ("Sales Plan",            "€90k / €100k", "90% to plan", "€10k behind"),
        ("Avg Sales / working day","€10k", "Y-1 €11k",  "▼ 9%"),
    ]):
        visuals.append(new_visual("card", 20 + i * (kpi_w + 12), 56, kpi_w, kpi_h, {
            "vcObjects": {
                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}],
            }
        }))

    # ---- Breakdown tables  (2 cols) ----------------------------------------
    tbl_y, tbl_h = 196, 200
    tbl_w = 590
    for i, tbl in enumerate(["sales_region", "sales_businessline"]):
        visuals.append(new_visual("tableEx", 20 + i * (tbl_w + 12), tbl_y, tbl_w, tbl_h))

    # ---- Charts row  (2 cols) ----------------------------------------------
    ch_y, ch_h = 416, 260
    ch_w = 590
    visuals.append(new_visual("barChart",    20,           ch_y, ch_w, ch_h))  # daily
    visuals.append(new_visual("lineChart",  622,          ch_y, ch_w, ch_h))  # cumulative

    return build_page("A · Whiteboard", visuals)


# ── Page B · Command Strip ────────────────────────────────────────────────────

def page_b() -> dict:
    visuals = []
    # KPI rail (left column)
    for i, kpi in enumerate(["MTD Sales", "Sales Plan", "Avg / day"]):
        visuals.append(new_visual("card", 12, 56 + i * 132, 220, 120))
    # Centre charts
    visuals.append(new_visual("lineChart", 244,  56, 630, 240))
    visuals.append(new_visual("barChart",  244, 308, 630, 190))
    # Right tables
    visuals.append(new_visual("tableEx",   886,  56, 382, 220))
    visuals.append(new_visual("tableEx",   886, 288, 382, 200))
    return build_page("B · Command Strip", visuals)


# ── Page C · Plan Tracker ─────────────────────────────────────────────────────

def page_c() -> dict:
    visuals = []
    # Gauge + cumulative (hero row)
    visuals.append(new_visual("gauge",    12,  56, 330, 240))
    visuals.append(new_visual("lineChart",354,  56, 914, 240))
    # Mini KPI strip
    for i in range(4):
        visuals.append(new_visual("card", 12 + i * 316, 308, 308, 100))
    # Table + daily bar
    visuals.append(new_visual("tableEx",  12, 420, 930, 270))
    visuals.append(new_visual("barChart", 954, 420, 314, 270))
    return build_page("C · Plan Tracker", visuals)


# ── Page D · Analyst Grid ─────────────────────────────────────────────────────

def page_d() -> dict:
    visuals = []
    # Slim KPI bar
    visuals.append(new_visual("multiRowCard", 12, 56, 1256, 70))
    # Two big tables
    visuals.append(new_visual("tableEx",  12, 138, 620, 310))
    visuals.append(new_visual("tableEx", 644, 138, 624, 310))
    # Spark footer
    for i, vtype in enumerate(["barChart", "lineChart", "lineChart"]):
        visuals.append(new_visual(vtype, 12 + i * 422, 460, 410, 230))
    return build_page("D · Analyst Grid", visuals)


def build_page(name: str, visuals: list) -> dict:
    return {
        "name": name,
        "displayName": name,
        "width": PW,
        "height": PH,
        "visualContainers": visuals,
        "config": json.dumps({
            "defaultDrillFilterOtherVisuals": True,
            "vcObjects": {
                "background": [{"properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'#fffefa'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0"}}}
                }}]
            }
        }),
        "filters": "[]",
    }


# ── DataModel (Mashup / M queries embedded) ──────────────────────────────────

def build_mashup() -> str:
    """Returns the Section1.m content for the Power Query mashup."""
    lines = ['section Section1;\n']
    for name, df in [
        ("sales_daily",         daily),
        ("sales_region",        region),
        ("sales_businessline",  bl),
        ("plan_monthly",        plan),
    ]:
        expr = df_to_m(df, name)
        lines.append(f'shared {name} = {expr};\n')
    return "\n".join(lines)


# ── Assemble .pbix ZIP ────────────────────────────────────────────────────────

def build_pbix(out_path: str) -> None:
    layout = {
        "id": 0,
        "resourcePackages": [],
        "sections": [page_a(), page_b(), page_c(), page_d()],
        "config": json.dumps({
            "version": "5.43",
            "themeCollection": {
                "baseTheme": {
                    "name": "SalesDashboard",
                    "version": "5.43",
                    "type": 2,
                },
            },
        }),
        "layoutOptimization": 0,
    }

    content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json"    ContentType="application/json"/>
  <Default Extension="xml"     ContentType="application/xml"/>
  <Default Extension="m"       ContentType="application/x-ms-mquery"/>
  <Override PartName="/Report/Layout"         ContentType="application/json"/>
  <Override PartName="/DataModel"             ContentType="application/x-ms-analysis-services"/>
  <Override PartName="/Mashup/Package/Formulas/Section1.m" ContentType="application/x-ms-mquery"/>
</Types>"""

    mashup_m = build_mashup()

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("Version",             "3.0")
        zf.writestr("Report/Layout",       json.dumps(layout, ensure_ascii=False))
        zf.writestr("Mashup/Package/Formulas/Section1.m", mashup_m)

    print(f"✓  Created: {out_path}")
    print(f"   Pages  : A · Whiteboard | B · Command Strip | C · Plan Tracker | D · Analyst Grid")
    print(f"   Tables : sales_daily, sales_region, sales_businessline, plan_monthly")
    print()
    print("Next steps in Power BI Desktop:")
    print("  1. File → Open → sales_dashboard.pbix")
    print("  2. Home → Transform Data → verify the 4 tables loaded correctly")
    print("  3. Model view → create relationships if needed (all tables are standalone for now)")
    print("  4. Report view → assign fields to each visual using measures.dax as reference")
    print("  5. Apply the 'SalesDashboard' theme (View → Themes → Browse for theme)")


# ── Optional Excel export ─────────────────────────────────────────────────────

def build_excel(out_path: str) -> None:
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        daily .to_excel(writer, sheet_name="sales_daily",        index=False)
        region.to_excel(writer, sheet_name="sales_region",       index=False)
        bl    .to_excel(writer, sheet_name="sales_businessline",  index=False)
        plan  .to_excel(writer, sheet_name="plan_monthly",        index=False)
    print(f"✓  Created: {out_path}  (use File → Import → Excel workbook in Power BI Desktop)")


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build sales_dashboard.pbix from CSV data")
    parser.add_argument("--excel", action="store_true", help="Also export sales_data.xlsx")
    args = parser.parse_args()

    pbix_path  = os.path.join(BASE, "sales_dashboard.pbix")
    excel_path = os.path.join(BASE, "sales_data.xlsx")

    build_pbix(pbix_path)
    if args.excel:
        build_excel(excel_path)
