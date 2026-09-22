# PPAC Energy Intelligence Agent

> **Autonomous Petroleum Planning, Econometric Forecasting & Statutory Reporting for MoPNG (Government of India)**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.9.2-orange.svg)](https://google.github.io/adk-docs/)
[![A2UI Protocol](https://img.shields.io/badge/A2UI-v0.9-green.svg)](https://a2ui.org)
[![Tests](https://img.shields.io/badge/tests-20%20passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Vertex%20AI-Agent%20Runtime-4285F4.svg)]()
[![Release](https://img.shields.io/badge/Release-V1.0.0-blue.svg)](https://github.com/amandeepsinghs-cyber/ppac-energy-intelligence-agent)
[![Target Authority](https://img.shields.io/badge/MoPNG-PPAC%20India-navy.svg)](https://ppac.gov.in/)

---

## 1. Problem Statement & Value Proposition

### 1.1 High-Level Problem Statement
**India's national hydrocarbon intelligence suffers from an 18–25 day publication latency, fragmenting executive decision-making and leaving policy makers and markets blind during critical monthly macroeconomic windows.**

The Petroleum Planning & Analysis Cell (PPAC), operating under the Ministry of Petroleum & Natural Gas (MoPNG), is mandated to publish statutory market intelligence—most notably the benchmark **Monthly Ready Reckoner** and **Snapshot of India’s Oil & Gas Data**. Under the current manual operating model:
* Month-end data is delayed by **18–25 days** (e.g., the July 2026 Ready Reckoner was published on August 20, 2026; August 2026 remains unreleased into late September).
* Market and policy stakeholders must make multimillion-dollar fiscal subsidy, strategic reserve, and procurement decisions using stale data.
* **Target Operating Model**: The PPAC Energy Intelligence Agent compresses this entire timeline to **under 48 hours**—generating a mathematically verified Day-0 draft at month-end close followed by 48 hours for Human-in-the-Loop (HITL) review and statutory release.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PUBLICATION LATENCY TRANSFORMATION                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Legacy Workflow (18-25 Days Lag):                                                      │
│ Month Close ──────► Manual Collation ──────► Ad-hoc QC ──────► T+20 Days Release       │
│                                                                                        │
│ Agentic Workflow (48 Hours Target):                                                    │
│ Month Close ──► Day 0: Auto Draft (T+0) ──► 48h HITL Review ──► T+2 Days Release     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Sub-Problems Solved by the Agent & System

| # | Sub-Problem Area | Legacy Operational Bottleneck | Agentic Solution & Mechanism |
|---|---|---|---|
| **1** | **Multi-PSU Data Siloing & Ingestion Delay** | OMCs (IOCL, BPCL, HPCL) and upstream PSUs (ONGC, GAIL, OIL) submit disparate, non-standardized Excel/ERP extracts days after month close. | **Automated Sovereign Ingestion**: Medallion Data Lake (`gs://og-sovereign-ppac-data`) with automated schema validation, anomaly quarantine, and instant reconciliation across all 5 PSUs. |
| **2** | **Manual Mathematical Parity & Accounting Errors** | Analysts perform manual spreadsheet cross-tabulation across refinery throughput, net sales, blending offsets, and imports, risking parity violations. | **Automated Governance Sanity Checks**: 6 continuous validation checks (`CHK-001` through `CHK-006`) enforcing mass balance parity, throughput ceilings, and tariff rules before draft generation. |
| **3** | **Uncertain Data Provenance & Lineage Gaps** | Published numbers often lack explicit statutory footnotes, creating audit friction between DGCIS customs figures, OMC retail sales, and market Platts/Argus quotes. | **Universal Statutory Provenance Matrix**: Every metric, table, and chart carries exact institutional lineage and statutory source mapping across all 7 data domains. |
| **4** | **Static Extrapolations vs. True Seasonality** | Traditional reporting relies on simple month-on-month growth, failing to capture agricultural harvesting dips (monsoon) or Q3 festive consumption surges. | **Live 12-Month SARIMAX Econometric Engine**: Stationarity-verified econometric models fitted over 77 months of authentic PPAC series with 80%/95% confidence intervals and dynamic interactive visualization. |
| **5** | **Complex Formula Administration (ICB & APM Gas)** | Calculating weighted Indian Crude Basket (Oman/Dubai 75.6% : Brent 24.4%) and Kirit Parikh domestic gas ceiling ($7.00/MMBTU floor/ceiling rules) requires manual verification. | **Deterministic Statutory Pricing Engines**: Zero-latency algorithmic calculation of ICB, APM gas ceilings, deepwater HP-HT tariffs, and metropolitan pump price build-ups. |
| **6** | **High Executive Friction for Ad-Hoc Data Exploration** | Senior leadership (Secretary MoPNG, PPAC Director General) must request specialized analyst runs to inspect multi-year consumption or subsidy trends. | **Native Gemini Enterprise & A2UI Interface**: Conversational executive interface with interactive Material 3 KPI cards, dynamic pricing matrices, and native Vega/A2UI charts. |

---

### 1.3 Key Questions the System & Agent Answer for Leadership

The agent is designed to answer both strategic macroeconomic questions and granular operational inquiries across the hydrocarbon value chain, organized in an **incremental sovereign intelligence lifecycle**:

#### Incremental Sovereign Lifecycle (Intake ➔ Baseline ➔ Pricing ➔ Forecasting ➔ Statutory Release)
1. **Intake & Lake Audit**: *"What is the status of August 2026 PSU submissions across IOCL, BPCL, HPCL, ONGC, and GAIL in our sovereign data lake?"*
2. **Historical Baseline & Seasonality**: *"What is the 5-year historical consumption trend for High Speed Diesel and Petrol, and how does agricultural/festive seasonality impact it?"*
3. **Statutory Pricing & Formula Compliance**: *"What are the official August 2026 Indian Crude Basket benchmarks and domestic natural gas statutory price ceilings?"*
4. **Forward Econometric Forecasting (Second to Last)**: *"What is the projected 12-month SARIMAX demand trajectory for High Speed Diesel, accounting for monsoon harvesting and festival seasonality?"*
5. **Statutory Report Synthesis & Certification (Final)**: *"Compile and publish the official August 2026 PPAC Monthly Ready Reckoner"*

#### Strategic Macroeconomic & Audit Deep Dives
* **Crude Import Dependency**: *"What is India's current crude import dependency percentage, and how has our crude import bill trended over the last 12 months?"*
* **Subsidy Fiscal Exposure**: *"How much fiscal exposure is MoPNG carrying under the Pradhan Mantri Ujjwala Yojana (PMUY) LPG subsidy at current international benchmark prices?"*
* **Retail Fuel Tax Build-Up**: *"What is the retail pump price build-up at Delhi for Petrol and Diesel, and what are the Central Excise and State VAT shares?"*
* **Governance & Quarantine**: *"Are there any unresolved anomaly quarantine exceptions or mass-balance parity mismatches across refinery throughput and consumption?"*
* **Statutory Provenance Lineage**: *"What is the statutory source and provenance behind our Indian Crude Basket weighting and retail pump price build-up across major metros?"*

---

### 1.4 Strategic Value: Accelerating PPAC's Forecasting Mandate (The Agentic Value-Add)

#### The Dual Institutional Tracks at PPAC
In actual operations, PPAC manages two distinct and vital intelligence tracks:
1. **Statutory Monthly Accounting (*Monthly Ready Reckoner & Snapshot*)**: Audited, backward-looking ground-truth of the preceding month ($T-1$) across all 27 tables. This publication is intentionally 100% historical to preserve zero-liability audit standards for Parliament Questions, CAG reviews, and regulatory proceedings.
2. **Periodic Demand Estimation (*Demand & Economic Studies Division*)**: PPAC actively conducts energy modeling and formulates Original Estimates (OE) and Revised Estimates (RE) for national petroleum consumption, working through regional industry coordination committees (*PPAC DRIVE* meetings with OMCs and State Level Coordinators).

#### The Operational Bottleneck in Current Forecasting
While the forecasting mandate is already well established within PPAC, the current operational workflow relies on:
* **Manual Regional Committee Collation**: Gathering, debating, and reconciling separate demand spreadsheets across IOCL, BPCL, HPCL, and regional coordinators requires weeks of manual committee effort.
* **Static Periodic Cadence**: Projections are finalized on an annual or half-yearly basis (OE/RE cycles). They cannot dynamically recalculate mid-cycle when geopolitical disruptions swing crude prices or irregular monsoons alter agricultural diesel consumption.
* **Manual Econometric Tuning**: Analysts must manually run statistical packages, adjust seasonal parameters, and reconcile figures with historical series.

#### The Agentic AI Transformation: Instant, Standardized Econometric Intelligence
The PPAC Energy Intelligence Agent does not seek to alter the scope of the official *Monthly Ready Reckoner* gazette, nor does it preach new mandates to leadership. Instead, it serves as an **autonomous productivity accelerator** for PPAC's existing Demand & Economic Studies teams and MoPNG leadership:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                         PPAC FORECASTING AGENTIC ACCELERATION                               │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Current PPAC Operating Model:                                                               │
│ • Monthly Ready Reckoner: Strictly backward-looking historical actuals (Zero Legal Risk).   │
│ • Demand Forecasting: Manual, periodic OMC committee collation (PPAC DRIVE meetings).       │
│ • Weeks of spreadsheet reconciliation to finalize Original/Revised Estimates (OE/RE).       │
│                                                                                             │
│ Agentic AI Enhancement (Continuous Decision Support):                                       │
│ • Preserves Official Gazette: Ready Reckoner remains 100% audited actuals (No Scope Creep). │
│ • Instant Automated Modeling: Fits standardized SARIMAX models over 77-month baseline.     │
│ • Zero Modeling Labor: Generates 12-month forward trajectories with 80%/95% confidence bands│
│   in under 3 seconds without manual data science overhead.                                  │
│ • Review-Only Simplicity: Planners shift from spreadsheet building to Executive Review.     │
│ • Dynamic Sensitivity: Instantly simulates demand impacts of crude shifts & festive peaks.  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Why Leadership Appreciates This Value Proposition
1. **Zero Scope Creep on Gazetted Reports**: The official published *Monthly Ready Reckoner* report remains strictly historical actuals, protecting the Ministry from parliamentary and commercial liability.
2. **Eliminates Weeks of Manual Committee Labor**: Standardized time-series forecasting (SARIMAX) runs automatically against the curated sovereign lake. Leadership can inspect 12-month outlooks on demand without waiting for quarterly committee cycles.
3. **Executive Decision Support**: Equips the Petroleum Secretary and OMC Directors with an internal, conversational scenario-planning tool in Gemini Enterprise to optimize VLCC tanker charters, refinery turnarounds, and Strategic Petroleum Reserve (SPR) buffer management.

---

## 2. Executive Summary & Architecture Overview

This conversational walkthrough demonstrates how Gemini Enterprise serves as the unified, single-pane-of-glass solution for energy planning leadership across the 5 incremental stages of monthly hydrocarbon intelligence.

```mermaid
flowchart TD
    Turn1["Turn 1: Sovereign Lake Audit\n'What is the status of August 2026 PSU submissions?'\n👉 Renders A2UI Lake Inventory Card"]
    Turn2["Turn 2: Historical Demand Baseline\n'What is the 5-year historical consumption trend for HSD?'\n👉 Renders Native Interactive VegaChart & FY Table"]
    Turn3["Turn 3: Statutory Benchmark Pricing\n'What are official August 2026 crude benchmarks & gas ceilings?'\n👉 Renders Native Interactive VegaChart & Pricing Table"]
    Turn4["Turn 4: 12-Month SARIMAX Forecast (Second to Last)\n'Run 12-month SARIMAX demand forecast for High Speed Diesel'\n👉 Renders Native Interactive VegaChart with 95% Bounds & Projection Matrix"]
    Turn5["Turn 5: Statutory Report Synthesis (Final)\n'Compile and publish the official August 2026 PPAC Monthly Ready Reckoner'\n👉 Renders A2UI Report Release Card with Live Editable HTML Link"]

    Turn1 --> Turn2 --> Turn3 --> Turn4 --> Turn5
```

---

### Turn 1: Sovereign Data Lake & PSU Submission Audit
* **Executive Prompt**:
  > *"What is the status of August 2026 PSU submissions in our sovereign data lake?"*
* **Engine Actions**:
  - Invokes `inspect_sovereign_lake(period_id="2026-08")`.
  - Audits `gs://og-sovereign-ppac-data/` across `1_raw_inbox/`, `2_curated/`, `3_artifacts/`, and `4_quarantine/`.
  - Verifies presence of intake workbooks from IOCL, BPCL, HPCL, ONGC, and GAIL.
* **Expected Output**:
  - **Conversational Narrative**:
    > Sovereign Data Lake `gs://og-sovereign-ppac-data` status for period **2026-08**: All 5 PSU intake submissions (IOCL, BPCL, HPCL, ONGC, GAIL) have been ingested into the raw medallion inbox. Data integrity checks passed with **0 unresolved quarantine exceptions**.
  - **Gemini Enterprise A2UI Surface**:
    - **Lake Inventory Card**: Displays active UBLA status in `asia-south1` (Mumbai), object counts across Bronze/Silver/Gold/Quarantine tiers, and green status pill.

---

### Turn 2: Multi-Year Historical Demand & Seasonality Baseline
* **Executive Prompt**:
  > *"What is the 5-year historical consumption trend for High Speed Diesel and how does seasonality impact it?"*
* **Engine Actions**:
  - Invokes `query_historical_demand(product_name="HSD", years=5)`.
  - Queries curated 77-month historical series (`ppac_official_historical_consumption_2020_2026.csv`).
  - Computes fiscal year totals, CAGR, peak month, trough month, and seasonal indices.
* **Expected Output**:
  - **Conversational Narrative**:
    > **High Speed Diesel (HSD)** consumption spans **September 2021 to August 2026** (60 months), with total consumption of **437,842.0 TMT** (monthly average: **7,297.4 TMT**). The annualized growth rate (CAGR) is **+4.9%**.
    > • **Peak Month**: March 2026 (**8,726.0 TMT**) driven by pre-monsoon harvesting, infrastructure push, and financial year-end logistics.
    > • **Trough Month**: September 2021 (**5,513.0 TMT**) reflecting peak monsoon agricultural lulls and transport slowdowns.
    > • **Fiscal Year Breakdown**: FY 21-22: 44,792.0 TMT | FY 22-23: 85,897.0 TMT | FY 23-24: 89,285.0 TMT | FY 24-25: 90,660.0 TMT | FY 25-26: 94,842.0 TMT.
  - **Gemini Enterprise A2UI Surface**:
    - **Native Interactive Historical Demand Card**: Interactive A2UI `VegaChart` with dynamic data-driven Y-scaling (`[5,000, 9,500] TMT`, non-zero origin, hover tooltips, parity labels) accompanied by the 5-Year Fiscal Year Consumption Performance Table (FY22–FY27 total demand, MMT, monthly run-rate, sovereign validation).

---

### Turn 3: Market Commodity Benchmarks & Statutory Ceilings
* **Executive Prompt**:
  > *"What are the official August 2026 Indian Crude Basket benchmarks and domestic natural gas statutory price ceilings?"*
* **Engine Actions**:
  - Invokes `query_market_pricing(period_id="2026-08", focus="crude")`.
  - Executes `IndianCrudeBasketCalculator` (75.6% Oman/Dubai @ $89.98 + 24.4% Dated Brent @ $90.84 = **$90.19 / bbl** at RBI rate ₹84.15/USD).
  - Executes `NaturalGasApmEngine` (enforcing statutory **$7.00 / MMBTU** ceiling under Kirit Parikh formula, alongside Deepwater HP-HT cap at **$8.90 / MMBTU**).
* **Expected Output**:
  - **Conversational Narrative**:
    > August 2026 Statutory Benchmark Summary:
    > • **Indian Crude Basket (ICB)**: **$90.19 / bbl** (₹7,589.50 / bbl) based on 75.6% Oman & Dubai ($89.98) and 24.4% Dated Brent ($90.84). This is a sovereign national benchmark.
    > • **Domestic Gas APM**: Statutory ceiling enforced at **$7.00 / MMBTU** (vs formula unconstrained $9.00 / MMBTU). Deepwater HP-HT cap at **$8.90 / MMBTU**.
    > • *(Downstream Inquiry)*: Retail pump prices are city-specific (at Delhi: Petrol ₹102.12/L, Diesel ₹95.20/L, Subsidized LPG ₹942.00/14.2kg cylinder).
  - **Gemini Enterprise A2UI Surface**:
    - **Native Interactive Pricing Matrix Card**: Interactive A2UI `VegaChart` horizontal benchmark comparison ($/bbl and $/MMBTU with shared scaling and hover tooltips) paired with a complete statutory price build-up matrix table.

---

### Turn 4: Live 12-Month SARIMAX Econometric Forecasting (Second to Last)
* **Executive Prompt**:
  > *"Run a 12-month SARIMAX demand forecast for High Speed Diesel (HSD)."*
* **Engine Actions**:
  - Invokes `run_sarimax_forecast(product_name="High Speed Diesel (HSD)", horizon_months=12)`.
  - Fits seasonal ARIMA on historical monthly consumption from the official August 2026 baseline (7,023 TMT).
  - Projects monthly volumes through August 2027 (CAGR: +3.7% YoY Seasonally Adjusted Annual Growth, terminal volume: ~7,839 TMT/month).
  - Computes 80% and 95% Gaussian uncertainty cones and renders a native interactive A2UI `VegaChart` with full-spectrum dynamic Y-scale (`[3,800, 12,900] TMT`), shared axis resolve, and companion tabular projections matrix.
* **Expected Output**:
  - **Conversational Narrative**:
    > Fitted SARIMAX (1,1,1)x(1,1,1)₁₂ demand forecast for **High Speed Diesel (HSD)** over 12 months (Sep 2026 – Aug 2027):
    > • **Baseline**: August 2026 (**7,023.0 TMT**)
    > • **Terminal 12-Month Projected Volume**: **7,839.2 TMT** / month
    > • **Projected Seasonally Adjusted Growth**: **+3.7% YoY**
    > • **Seasonality Factors**: Models pre-monsoon harvest surge and Q3 festive haulage peak.
  - **Gemini Enterprise A2UI Surface**:
    - **Native Interactive Forecast Card**: Dynamic A2UI `VegaChart` rendering historical actuals, 12-month dotted projection line, and 80%/95% confidence bands, accompanied by the **Interactive 12-Month Monthly Projections Matrix Table** detailing forward periods, projected demand, confidence intervals, and seasonal demand regimes.

---

### Turn 5: Statutory Report Synthesis & Artifact Delivery (Final)
* **Executive Prompt**:
  > *"Compile and publish the official August 2026 PPAC Monthly Ready Reckoner"*
* **Engine Actions**:
  - Invokes `compile_statutory_report(period_id="2026-08")`.
  - Synthesizes the interactive, live-editable 15-page HTML dashboard and executive Word DOCX.
  - Incorporates official MoPNG branding: Three Lions State Emblem of India, 1:1 scaled PPAC 25-Year Jubilee emblem, uncrowded leader-line charts, and T+1 publication cadence.
  - Uploads approved artifacts to `gs://og-sovereign-ppac-data/3_artifacts/2026-08/approved/`.
* **Expected Output**:
  - **Conversational Narrative**:
    > The official August 2026 PPAC Executive Report has been successfully compiled and approved. It is available as an interactive, live-editable sovereign report at: [https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.html](https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.html)
    >
    > Key highlights from the report:
    > • Total POL consumption reached 18,606 TMT (18.61 MMT) in August 2026.
    > • HSD consumption grew +6.8% YoY to 7,023 TMT; MS expanded +8.2% YoY to 3,836 TMT.
    > • Indian Crude Basket (ICB) averaged $90.19 / bbl with RBI Reference Rate at ₹84.15 / USD.
    > • Domestic APM Natural Gas capped at statutory ceiling of $7.00 / MMBTU; HP-HT ceiling at $8.90 / MMBTU.
    > • PMUY budgetary allocation of ₹12,000 Cr successfully absorbed for targeted domestic LPG subsidies.
  - **Gemini Enterprise A2UI Surface**:
    - **Report Release Card**: Visual summary of key metrics, green governance status pill, and direct access links:
      - **Interactive In-Browser Editable HTML**: `gs://og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.html`
      - **Executive Word DOCX**: `gs://og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.docx`

---

## 3. Live Cloud Infrastructure & Deployment Coordinates

The agent is deployed to Google Cloud and accessible across the following endpoints:

| Layer | Environment & Resource ID | Access / Console Link |
|---|---|---|
| **Vertex AI Agent Runtime** | `projects/349946979746/locations/asia-south1/reasoningEngines/5487856048276504576` | [Agent Engine Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/asia-south1/agent-engines/5487856048276504576?project=og-agentic-ecosystem) |
| **Gemini Enterprise App** | `projects/349946979746/locations/global/collections/default_collection/engines/oil-and-gas-agentic-transf_1788683272432` | [Gemini Enterprise Console](https://console.cloud.google.com/gemini-enterprise/locations/global/engines/oil-and-gas-agentic-transf_1788683272432/overview/dashboard?project=og-agentic-ecosystem) |
| **GE Registered Agent** | `.../assistants/default_assistant/agents/12804055990754341026` | Invoked via native `:streamQuery` |
| **Sovereign Data Lake** | `gs://og-sovereign-ppac-data/` (`asia-south1` Mumbai) | 4-Tier Medallion storage with 90d/365d lifecycle tiering |
| **Service Account** | `service-349946979746@gcp-sa-aiplatform-re.iam.gserviceaccount.com` | Roles: Storage Object User, Vertex AI Agent User |

---

## 4. Sovereign Medallion Data Lake Topology

```
gs://og-sovereign-ppac-data/
├── 1_raw_inbox/
│   ├── psu_submissions/
│   │   ├── iocl/          # IOCL monthly sales workbooks
│   │   ├── bpcl/          # BPCL monthly sales workbooks
│   │   ├── hpcl/          # HPCL monthly sales workbooks
│   │   ├── ongc/          # ONGC crude/gas production records
│   │   └── gail/          # GAIL gas transmission & APM logs
│   ├── official_publications/
│   │   ├── snapshot_aug2026.pdf
│   │   └── icb_aug2026.pdf
│   ├── government_dispatches/
│   └── market_feeds_api/
├── 2_curated/
│   └── 2026-08/
│       └── canonical_pricing.json
├── 3_artifacts/
│   └── 2026-08/
│       ├── approved/      # Signed-off HTML & DOCX reports
│       └── charts/        # 250 DPI high-res figures
└── 4_quarantine/          # Exception & anomaly audit ledger
```

---

## 5. Architecture & Project Layout

```
ppac-energy-intelligence-agent/
├── app/
│   ├── agent.py               # Root export (app, root_agent)
│   ├── contracts.py           # A2UI messages, lake models, benchmark summaries
│   ├── fast_api_app.py        # FastAPI server with A2A & Reasoning Engine routes
│   ├── canonical/             # Domain entities (FuelConsumption, PricingBenchmark)
│   ├── ingestion/             # Excel parsers & anomaly detection engine
│   ├── pricing/               # ICB calculator & Natural Gas APM engine
│   ├── tsa/                   # SARIMAX forecaster & vector chart engine
│   ├── synthesis/             # HTML & DOCX publication compilers
│   ├── render/                # A2UI v0.9 lifecycle builders (Cards, Vega, Envelopes)
│   │   ├── a2ui_emit.py       # Multi-part createSurface + updateDataModel + updateComponents emitter
│   │   ├── a2ui_envelope.py   # Serializes <a2a_datapart_json> envelopes
│   │   ├── a2ui_lifecycle.py  # createSurface & updateComponents builders
│   │   ├── inventory_card.py  # Sovereign lake inventory surface
│   │   ├── historical_card.py # Historical demand card with fiscal year table
│   │   ├── historical_vega.py # Dynamic interactive Vega-Lite spec for historical consumption
│   │   ├── pricing_card.py    # Upstream & retail pricing matrix surface
│   │   ├── pricing_vega.py    # Dynamic interactive Vega-Lite spec for pricing benchmarks
│   │   ├── forecast_card.py   # 12m SARIMAX forecast surface with projections matrix table
│   │   ├── forecast_vega.py   # Dynamic interactive Vega-Lite spec with 95% confidence bands
│   │   └── report_card.py     # Approved statutory report release surface
│   ├── integration/           # ADK Agent, A2uiNegotiatingExecutor & Tools
│   └── app_utils/             # Process-wide session/artifact services & A2A routes
├── tests/                     # 20 passing tests across 6 Phased Gates
├── agents-cli-manifest.yaml   # Deployment manifest for Vertex AI Agent Runtime
├── pyproject.toml             # Dependencies (Google ADK, A2A SDK, statsmodels)
└── README.md
```

---

## 6. Verification Test Matrix (20/20 Passing)

Run the full automated test suite locally:
```bash
.venv/bin/pytest tests/ -v
```

```
tests/test_gate0_contracts.py::test_canonical_models_instantiation PASSED
tests/test_gate0_contracts.py::test_mock_fixtures_exist PASSED
tests/test_gate1_ingestion_and_pricing.py::test_excel_ingestion_and_anomaly_detection PASSED
tests/test_gate1_ingestion_and_pricing.py::test_indian_crude_basket_calculation PASSED
tests/test_gate1_ingestion_and_pricing.py::test_natural_gas_apm_kirit_parikh_formula PASSED
tests/test_gate2_tsa_forecasting.py::test_sarimax_demand_forecasting PASSED
tests/test_gate2_tsa_forecasting.py::test_forecast_chart_rendering PASSED
tests/test_gate3_document_assembly.py::test_zero_to_draft_document_assembly PASSED
tests/test_gate4_hitl_resolution.py::test_agent_card_contract PASSED
tests/test_gate4_hitl_resolution.py::test_end_to_end_pipeline_and_hitl_resolution PASSED
tests/test_gate4_hitl_resolution.py::test_a2a_jsonrpc_protocol_methods PASSED
tests/test_gate5_adk_a2ui_integration.py::test_inventory_card_a2ui_structure PASSED
tests/test_gate5_adk_a2ui_integration.py::test_pricing_matrix_card_a2ui_structure PASSED
tests/test_gate5_adk_a2ui_integration.py::test_focused_pricing_matrix_cards_a2ui PASSED
tests/test_gate5_adk_a2ui_integration.py::test_forecast_card_a2ui_structure PASSED
tests/test_gate5_adk_a2ui_integration.py::test_report_artifact_card_a2ui_structure PASSED
tests/test_gate5_adk_a2ui_integration.py::test_a2ui_envelope_wrapping PASSED
tests/test_gate5_adk_a2ui_integration.py::test_agent_tools_execution PASSED
tests/test_gate5_adk_a2ui_integration.py::test_callback_scrubbing_and_emission PASSED
tests/test_gate5_adk_a2ui_integration.py::test_historical_demand_tool_and_card_a2ui PASSED
```

---

## 7. Official Live Demo Prompt Sequence (Turn-by-Turn)

Copy and paste these prompts directly into Gemini Enterprise or the ADK CLI during executive demonstrations, progressing through the **incremental 5-stage sovereign intelligence lifecycle**:

### Question 1: Sovereign Data Lake Audit (Medallion Ingestion)
* **Prompt**:
  > *"What is the status of August 2026 PSU submissions in our sovereign data lake?"*
* **Tool Invoked**: `inspect_sovereign_lake(period_id="2026-08")`
* **Expected Ground-Truth Output**:
  * Audits `gs://og-sovereign-ppac-data/` in `asia-south1` (Mumbai).
  * Verifies intake files from all 5 PSUs (IOCL, BPCL, HPCL, ONGC, GAIL).
  * Confirms **0 unresolved quarantine exceptions** and displays the A2UI Lake Inventory Card.

### Question 2: 5-Year Historical Demand Baseline & Seasonality (PPAC Ground Truth)
* **Prompt**:
  > *"What is the 5-year historical consumption trend for High Speed Diesel and how does seasonality impact it?"*
* **Tool Invoked**: `query_historical_demand(product_name="HSD", years=5)`
* **Expected Ground-Truth Output**:
  * Total 60-month volume: **437,842.0 TMT** (monthly average: **7,297.4 TMT**).
  * 5-Year Annualized CAGR: **+4.9%**.
  * **Peak Month**: March 2026 (**8,726.0 TMT**) driven by pre-monsoon harvesting, road construction, and fiscal year close.
  * **Trough Month**: September 2021 (**5,513.0 TMT**) due to peak monsoon agricultural and transport slowdowns.
  * Renders the native interactive A2UI `VegaChart` with dynamic data-driven Y-scaling (`[5,000, 9,500] TMT`, non-zero origin, hover tooltips) and companion 5-Year Fiscal Year Performance Table.

### Question 3: Statutory Benchmark Pricing & Retail Pump Breakdown
* **Prompt**:
  > *"Can I see the August 2026 crude benchmarks, gas ceilings, and Delhi retail price breakdown?"*
* **Tool Invoked**: `query_market_pricing(period_id="2026-08")`
* **Expected Ground-Truth Output**:
  * **Indian Crude Basket (ICB)**: **$90.19 / bbl** (₹7,589.50 / bbl) at 75.6% Oman/Dubai ($89.98) and 24.4% Brent ($90.84), with RBI Reference Rate at ₹84.15 / USD.
  * **Domestic Gas APM**: Enforced at statutory ceiling of **$7.00 / MMBTU** under Kirit Parikh formula; deepwater HP-HT ceiling at **$8.90 / MMBTU**.
  * **Delhi Retail Pump Prices**: Petrol ₹102.12/L (VAT ₹16.59), Diesel ₹95.20/L (VAT ₹13.91), Domestic LPG ₹942.00/14.2kg.
  * Renders the native interactive A2UI `VegaChart` multi-benchmark horizontal bars and tabular pricing breakdown matrix.

### Question 4: 12-Month SARIMAX Forward Econometric Forecast (Second to Last)
* **Prompt**:
  > *"Run a 12-month SARIMAX demand forecast for High Speed Diesel (HSD)."*
* **Tool Invoked**: `run_sarimax_forecast(product_name="High Speed Diesel (HSD)", horizon_months=12)`
* **Expected Ground-Truth Output**:
  * Fits seasonal ARIMA on authentic 77-month PPAC series.
  * Projects demand through August 2027 (terminal: **~7,839 TMT/month**, +3.7% YoY Seasonally Adjusted Annual Growth).
  * Renders native interactive A2UI `VegaChart` with dynamic full-spectrum Y-scale (`[3,800, 12,900] TMT`), shared axis resolve, and 80%/95% confidence bands, accompanied by the **Interactive 12-Month Monthly Projections Matrix Table** detailing projected demand, bounds, and seasonal regimes.

### Question 5: Statutory Report Synthesis & Publication (Final)
* **Prompt**:
  > *"Compile and publish the official August 2026 PPAC Monthly Ready Reckoner."*  
  *(Or: "Compile and publish the official August 2026 PPAC Executive Report.")*
* **Tool Invoked**: `compile_statutory_report(period_id="2026-08")`
* **Expected Ground-Truth Output**:
  * Synthesizes the statutory publication with authentic MoPNG masthead, Three Lions State Emblem, 1:1 scaled PPAC 25-Year jubilee emblem, and uncrowded leader-line charts.
  * Emits the **[HTML Sovereign Monthly Ready Reckoner](https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.html)** featuring the borderless red **`⚠️ PROTOTYPE DEMO REPORT`** disclaimer, 10 official Monthly Highlights, 27 tables, and 10 numbered citations.

### Question 6: Chromebook Live In-Browser Editing & Governance Sign-Off
* **Workflow**:
  1. Open the [HTML Dashboard](https://storage.cloud.google.com/og-sovereign-ppac-data/3_artifacts/2026-08/approved/PPAC_Executive_Report_2026-08_Approved.html).
  2. Click any table cell or sentence to edit in-place directly on your screen.
  3. Use **`💾 Save Edits`** (auto-persists to browser storage), **`📥 Download HTML`** (saves standalone copy), and **`🖨 Print / PDF`** (exports clean official PDF with toolbar automatically suppressed).

---

## 8. Git Repository Coordinates & Release Version

* **Official Repository**: [https://github.com/amandeepsinghs-cyber/ppac-energy-intelligence-agent](https://github.com/amandeepsinghs-cyber/ppac-energy-intelligence-agent)
* **Release**: `V1.0.0`
* **Target Sovereign Authority**: Ministry of Petroleum & Natural Gas (MoPNG) / Petroleum Planning & Analysis Cell (PPAC)
* **Governing Google Cloud Project**: `og-agentic-ecosystem` (`asia-south1` Mumbai)
