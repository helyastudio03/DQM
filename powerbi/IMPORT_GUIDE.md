# Ouvrir le rapport dans Power BI Desktop

## Étape 1 — Importer les données (2 min)

1. Ouvrir **Power BI Desktop**
2. **Home → Get data → Excel workbook**
3. Sélectionner `sales_data.xlsx`
4. Cocher les 4 tables : `sales_daily` · `sales_region` · `sales_businessline` · `plan_monthly`
5. Cliquer **Load**

---

## Étape 2 — Appliquer le thème (30 sec)

1. Onglet **View → Themes → Browse for themes**
2. Sélectionner `SalesDashboard_theme.json`

---

## Étape 3 — Créer les mesures DAX

Dans le panneau **Data** (droite), clic droit sur `sales_daily` → **New measure**, puis copier-coller chaque bloc de `measures.dax`.

Mesures essentielles à créer en premier :

```dax
MTD Sales = SUM(sales_daily[Sales_Y])

MTD Sales Y-1 = SUM(sales_daily[Sales_Y1])

MTD Sales vs Y-1 % = DIVIDE([MTD Sales] - [MTD Sales Y-1], [MTD Sales Y-1], 0)

Plan Y = SUM(plan_monthly[Plan_Amount])

Attainment % = DIVIDE([MTD Sales], [Plan Y], 0)

Working Days Elapsed =
CALCULATE(COUNTROWS(sales_daily),
    sales_daily[WorkingDay] = 1,
    NOT ISBLANK(sales_daily[Sales_Y]))

Avg Sales Per Working Day = DIVIDE([MTD Sales], [Working Days Elapsed], 0)

Forecast EOM = [Avg Sales Per Working Day] * MAX(plan_monthly[Working_Days_Total])

Gap vs Pace € =
[MTD Sales] - DIVIDE([Plan Y], MAX(plan_monthly[Working_Days_Total]), 0) * [Working Days Elapsed]
```

---

## Étape 4 — Construire les 4 pages

### Page A · Whiteboard (fidèle au wireframe)

| Zone | Visual Power BI | Champs |
|---|---|---|
| KPI 1 | **Card** | `[MTD Sales]` · sous-titre `[MTD Sales vs Y-1 %]` |
| KPI 2 | **Card** + **Gauge** | `[MTD Sales]` vs `[Plan Y]` → `[Attainment %]` |
| KPI 3 | **Card** | `[Avg Sales Per Working Day]` |
| Tableau Region | **Table** | `Region · Sales_Y · Sales_Y1 · Plan_Y` + mesures variance |
| Tableau BL | **Table** | `BusinessLine · Sales_Y · Sales_Y1 · Plan_Y` + mesures variance |
| Barres daily | **Clustered bar** | Axe X = `DayIndex` · Valeur = `Sales_Y` |
| Cumulatif Y vs Y-1 | **Line chart** | Axe X = `DayIndex` · Lignes = `Sales_Y` + `Sales_Y1` |

### Page B · Command Strip

Même visuels, disposition 3 colonnes : KPIs gauche · Charts centre · Tables droite.

### Page C · Plan Tracker

| Zone | Visual | Champs |
|---|---|---|
| Jauge | **Gauge** | Valeur = `[MTD Sales]` · Max = `[Plan Y]` |
| Cumul 3 lignes | **Line chart** | `Sales_Y` + `Sales_Y1` + `[Pace Plan MTD]` |
| Mini KPIs | **Card** ×4 | MTD · Attainment % · Avg/day · Forecast EOM |
| Table tabbée | **Table** | Region puis BL (2 pages Power BI ou boutons) |

### Page D · Analyst Grid

| Zone | Visual |
|---|---|
| Barre KPI slim | **Multi-row card** — tous les KPIs en ligne |
| 2 grandes tables | **Table** Region + **Table** BL avec toutes colonnes |
| Footer sparklines | **Bar** daily · **Line** cumul · **Line** avg/day |

---

## Étape 5 — Mise en forme rapide

Pour reproduire le style "sketch" du wireframe :

- **Format pane → Border** : activé, couleur `#2b2b33`, radius `8px`
- **Background** : `#fffefa`
- **Positive values** (table) : couleur conditionnelle `#2e8b57`
- **Negative values** (table) : couleur conditionnelle `#c0563f`
- **Gauge fill** : `#2f6fb0`

---

## Résultat attendu

```
Page A  →  3 KPIs · 2 tables · 2 charts  (top-down)
Page B  →  KPI rail gauche · charts centre · tables droite
Page C  →  Jauge attainment + cumul plan vs actuel
Page D  →  Tables analysts + sparklines footer
```
