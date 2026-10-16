# Maven Fuzzy Factory — Executive E-Commerce Analytics Suite

An enterprise-grade **Power BI Project (`.pbip`)** delivering end-to-end executive business intelligence for **Maven Fuzzy Factory**, an e-commerce retailer. 

The suite leverages the modern **Tabular Model Definition Language (TMDL)**, custom **HTML/SVG DAX measures**, Deneb (Vega-Lite) data visualizations, and an **Executive Light** design system inspired by Stripe and Linear analytics.

---

## 📊 Executive Summary & Report Pages

The report is structured into **7 purpose-built analytical pages**:

| # | Page Name | Core Focus & Key Visuals |
|---|---|---|
| **1** | **Storyboard** | Macro business trajectory, chapter-by-chapter storyline, dynamic metric toggles (Revenue, Orders, Margin, CVR), and historical milestone annotations. |
| **2** | **Acquisition** | Paid traffic performance (Gsearch vs. Bsearch), Brand vs. Nonbrand campaigns, Device segmentation (Mobile vs. Desktop), and Organic/Direct trends. |
| **3** | **CRO Lab** | Website conversion rate optimization, Lander A/B tests (`/home` vs. `/lander-1`), funnel drop-off analysis, bounce rate improvements, and billing page test analysis. |
| **4** | **Products** | Product line launches (Mr. Fuzzy, Love Bear, Birthday Sugar Panda, Hudson River Mini Bear), cross-sell attach rates, portfolio margin, and product return rates. |
| **5** | **Retention** | Customer repeat purchasing behavior, cohort retention heatmaps, repeat order cadence (days to second purchase), and channel attribution for repeat buyers. |
| **6** | **Financial** | Comprehensive executive P&L, gross revenue, net revenue, refund deductions, estimated shipping & product costs, contribution margin, and monthly pacing. |
| **7** | **What-If** | Interactive scenario simulator with 4-lever color-coordinated drivers: CVR Lift (Blue), Cross-Sell Attach (Amber), Refund Cut (Rose), and Benchmark Targets (Indigo) with net revenue waterfall bridge and sensitivity matrix. |

---

## 🎨 Design System: Executive Light

The suite implements a high-contrast, WCAG AAA-compliant **Executive Light** aesthetic:
- **Primary Canvas:** Clean crisp white (`#FFFFFF`) on soft slate (`#F8FAFC` / `#F1F5F9`).
- **Typography:** Segoe UI Variable / Segoe UI with tabular numerals for financial accuracy.
- **Card Styling:** 8px–12px rounded borders, subtle 1px slate borders (`#CBD5E1`), and soft ambient drop shadows (`rgba(15, 23, 42, 0.06)`).
- **Semantic Lever Palette:**
  - 🔵 **Conversion Rate (CVR):** Executive Blue (`#1D4ED8`)
  - 🟠 **Cross-Sell Attach:** Executive Amber (`#D97706`)
  - 🔴 **Refund Reduction:** Executive Rose (`#E11D48`)
  - 🟣 **Benchmark Targets:** Executive Indigo (`#4F46E5`)
  - 🟢 **Net Revenue Upside / Gain:** Executive Emerald (`#059669`)

---

## 📁 Repository Structure

```text
Maven-Fuzzy-Factory/
│
├── .gitignore                                  # Power BI local cache, user settings, temp files
├── README.md                                   # Project documentation and architecture guide
├── Maven Fuzzy Factory.pbip                    # Power BI Project entry point
│
├── Maven Fuzzy Factory.Report/                 # Power BI Report Layer
│   ├── definition/
│   │   ├── pages/                              # Visual definitions across Pages 1–7
│   │   └── report.json                         # Global theme & visual container configs
│   └── StaticResources/
│       └── RegisteredResources/               # Registered Light Executive theme
│
├── Maven Fuzzy Factory.SemanticModel/          # Power BI Semantic Model Layer (TMDL)
│   ├── definition/
│   │   ├── tables/                             # 212 measures, calculation groups, dimensions, facts
│   │   ├── expressions.tmdl                    # Parameter queries (DataSourceType, LocalFolderPath)
│   │   ├── relationships.tmdl                  # Star-schema model relationships
│   │   └── model.tmdl
│   └── diagramLayout.json                      # Visual relationship diagram layout
│
├── data/                                       # Raw datasets & schema dictionary
│   ├── maven_fuzzy_factory_data_dictionary.csv
│   ├── order_item_refunds.csv                  # Item-level refund transactions
│   ├── order_items.csv                         # Order line items and product IDs
│   ├── orders.csv                              # Primary order header records
│   ├── products.csv                            # Product catalog metadata
│   ├── website_pageviews.csv                   # Pageview event log
│   └── website_sessions.csv                    # Website session metadata & UTM attribution
│
├── docs/                                       # Project briefs & mockups
│   ├── MAVEN_FUZZY_FACTORY_POWERBI_BRIEF.md    # Comprehensive analytical specifications
│   └── maven_fuzzy_factory_powerbi_mockup.html # Interactive HTML design mockup
│
└── templates/                                  # Deneb & Theme Templates
    ├── theme.json                              # Standalone Executive Light theme JSON
    └── deneb/
        ├── deneb_dumbbell_cvr.json             # Vega-Lite dumbbell chart spec
        ├── deneb_growth_trajectory.json        # Vega-Lite growth trajectory spec
        └── deneb_revenue_cvr_combo.json        # Vega-Lite revenue & CVR dual-axis spec
```

---

## 🚀 Getting Started & Data Refresh

### Prerequisites
- **Power BI Desktop** (October 2023 release or newer).
- Ensure **Power BI Project (`.pbip`) format** is enabled in Power BI Desktop under:
  *File → Options and settings → Options → Preview features → Power BI Project (.pbip) save option*.

### How to Open
Double-click [`Maven Fuzzy Factory.pbip`](Maven%20Fuzzy%20Factory.pbip) or open it from Power BI Desktop.

### Data Connection Modes
The model includes a parameterized query in [`expressions.tmdl`](Maven%20Fuzzy%20Factory.SemanticModel/definition/expressions.tmdl) allowing flexible data loading:

1. **GitHub Online Source (Default):**
   - Automatically downloads the latest CSV data directly from this repository via GitHub raw endpoints.
   - Requires zero local file path configuration.
2. **Local Folder Source:**
   - In Power BI Desktop, navigate to *Home → Transform data → Edit parameters*.
   - Set `DataSourceType` to `Local`.
   - Set `LocalFolderPath` to your local clone path (e.g. `C:\YourPath\Maven-Fuzzy-Factory\`).

---

## 📐 Semantic Model Highlights

- **Star-Schema Architecture:** Fact tables (`orders`, `order_items`, `order_item_refunds`, `website_sessions`, `website_pageviews`) joined to shared dimensions (`Dim_Date`, `products`).
- **212 DAX Measures:** Grouped into folders:
  - `01 Core Metrics`: Orders, Gross/Net Revenue, Margin, AOV, CVR, Refunds.
  - `02 Time Intelligence`: YoY, MoM, Prior Period, 4-Week Rolling Averages.
  - `03 Acquisition & Paid`: CPC, CAC, Nonbrand Search Share, Mobile/Desktop splits.
  - `04 CRO Lab`: Landing page bounce rates, funnel stage conversion, cart billing variant lift.
  - `05 Retention & Cohorts`: Repeat buyer rates, days to repeat, cohort LTV curves.
  - `06 Executive HTML & Deneb`: Custom SVG mini-charts, pill strips, and animated HTML cards.
  - `09 Page 7 - What-If`: Dynamic scenario modeling using disconnected parameters.

---

## 📄 License
This repository is published for portfolio and business intelligence demonstration purposes.
