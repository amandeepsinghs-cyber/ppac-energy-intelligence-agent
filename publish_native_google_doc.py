"""Generate publication-grade Markdown and create native Google Doc via Workspace server."""

import subprocess
import json
from pathlib import Path
from app.synthesis.ready_reckoner_data import get_ready_reckoner_dataset

def generate_markdown(period_id="2026-08") -> str:
    ds = get_ready_reckoner_dataset(period_id=period_id)
    lines = []
    
    # Masthead & Header
    lines.append("# ⚠ DRAFT FOR STATUTORY REVIEW — CONFIDENTIAL / PROVISIONAL RELEASE ⚠")
    lines.append("**PETROLEUM PLANNING & ANALYSIS CELL (PPAC) · MINISTRY OF PETROLEUM & NATURAL GAS, GOVT OF INDIA**")
    lines.append(f"**MONTHLY READY RECKONER — SNAPSHOT OF INDIA'S OIL & GAS DATA ({period_id.upper()})**")
    lines.append(f"*Statutory Close: August 2026 | Publication Ref: PPAC-RR-{period_id}-PROV | 48-Hour Desk Review Window*\n")
    lines.append("---")
    
    # KPI Executive Summary
    lines.append("## Executive Sovereign Key Performance Indicators")
    lines.append("* **Indian Crude Basket (ICB):** **$90.19 / bbl** (₹7,589.50 / bbl) | *Source: PPAC Table 25*")
    lines.append("* **Brent Crude Benchmark:** **$90.84 / bbl** (ICE London Close) | *Source: Platts / ICE*")
    lines.append("* **APM Natural Gas Price:** **$7.00 / MMBTU** (Statutory Ceiling Enforced) | *Source: MoPNG Gazette*")
    lines.append("* **Net Oil & Gas Trade Bill:** **$11.20 Billion** (Crude: $13.7B, LNG: $1.2B, Exports: $5.0B) | *Source: DGCIS*")
    lines.append("* **Gross POL Delivery:** **18,606 TMT** (18.61 MMT) | *Source: PPAC Table 11(A)*\n")
    lines.append("---")
    
    # Highlights for the Month (PPAC pp. 2-3)
    lines.append("## Highlights for the Month (July 2026 Actuals / August 2026 Provisional)")
    lines.append("*(Official statutory executive release from PPAC Ready Reckoner Pages 2–3)*\n")
    
    highlights = [
        "**Indigenous Crude Oil & Condensate Production:** Production during July 2026 was **2.3 MMT** (August provisional: 2,246 TMT). Around **78.7%** of production came from Nomination Fields, **11.8%** from Pre-NELP Fields, and **9.3%** from NELP Fields. De-growth of 5.3% YoY was recorded against July 2025.",
        "**Refinery Crude Processing:** Total crude oil processed during July 2026 was **23.8 MMT** (+2.0% YoY), of which PSU/JV refiners processed 15.8 MMT and private refiners processed 8.0 MMT. Total indigenous crude processed was 2.1 MMT and imported crude was 21.6 MMT.",
        "**Crude Oil Imports & Net Trade Bill:** Crude oil imports registered a growth of **13.3%** during July 2026 (21.4 MMT; $13.7 Billion). As compared to net oil & gas import bill for July 2025 of $9.4 Billion, the net import bill for July 2026 was **$11.2 Billion** (Crude: $13.7B, LNG imports: $1.2B, POL exports: $5.0B).",
        "**International Benchmark & Basket Pricing:** Brent Crude averaged **$90.84/bbl** for August 2026 provisional ($83.41/bbl in July 2026). The Indian Basket Crude (ICB) price averaged **$90.19/bbl** (₹7,589.50/bbl at RBI ₹84.15/USD) for August 2026 (vs $82.04/bbl in July 2026 and $70.95/bbl in July 2025).",
        "**Production of Petroleum Products (POL):** Production reached **24.8 MMT** during July 2026 (+3.0% YoY; 24.5 MMT refinery throughput + 0.3 MMT fractionators). Major product shares: High-Speed Diesel (HSD) **41.9%**, Motor Spirit (MS) **17.5%**, Naphtha **6.5%**, ATF **5.1%**, Pet Coke **4.8%**, LPG **4.9%**.",
        "**Imports of POL Products:** Registered a de-growth of **40.6%** during July 2026 (2.5 MMT; $1.3 Billion) and 45.1% during April–July FY 2026-27, driven by sharp reductions in imports of LPG, petcoke, and fuel oil.",
        "**Exports of POL Products:** Registered a growth of **8.3%** during July 2026 (5.5 MMT; $5.0 Billion), with cumulative April–July FY 2026-27 exports standing at 16.5 MMT ($16.7 Billion).",
        "**Domestic Consumption of POL Products:** Domestic consumption during July 2026 was **19.91 MMT** (+2.9% YoY compared to 19.35 MMT in July 2025). Growth was driven by **+10.0%** in HSD and **+9.2%** in MS, offset by 16.4% de-growth in LPG and 13.8% in Naphtha. Cumulative April–July volume reached 77.8 MMT.",
        "**Ethanol Blending Programme (EBP):** Ethanol blending in Petrol achieved **20.0%** during July 2026. Cumulative blending during Ethanol Supply Year (ESY Nov 2025 – Jul 2026) was **20.0%**, achieving the national statutory target.",
        "**Natural Gas & LNG Consumption:** Total natural gas consumption (including internal consumption) for July 2026 was **5,740 MMSCM** (-1.05% YoY). Gross natural gas production stood at 2,864 MMSCM. Prorated LNG import volume was **2,915 MMSCM** (+1.50% YoY)."
    ]
    for idx, h in enumerate(highlights, 1):
        lines.append(f"{idx}. {h}")
    lines.append("\n---")
    
    # Part A
    lines.append("## Part A: Macroeconomic Indicators & Energy Balance\n")
    lines.append("### Table 1: Selected Indicators of the Indian Economy [Source: 8, 9]")
    lines.append("| Economic Indicator | Unit / Base | Current Period | Previous Year | YoY Growth / Change |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table1_economic_indicators"]:
        lines.append(f"| {r['indicator']} | {r['unit']} | {r['val_cur']} | {r['val_prev']} | {r['yoy']} |")
    lines.append("*Source: Reserve Bank of India [8], Ministry of Statistics and Programme Implementation (MoSPI) [9].*\n")
    
    lines.append("### Table 2: Crude Oil, LNG and Petroleum Products at a Glance [Source: 2, 3, 6]")
    lines.append("| Commodity / Energy Flow | Unit | Aug 2026 (P) | Jul 2026 | Aug 2025 | MoM % | YoY % | FYTD 26-27 | FYTD 25-26 | YTD % |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in ds["table2_energy_glance"]:
        lines.append(f"| {r['item']} | {r['unit']} | {r['aug26']} | {r['jul26']} | {r['aug25']} | {r['mom']} | {r['yoy']} | {r['fytd27']} | {r['fytd26']} | {r['ytd_chg']} |")
    lines.append("*Source: PPAC Table 2 [2], DGCIS [3], Refinery returns [6].*\n")
    lines.append("---")
    
    # Part B
    lines.append("## Part B: Upstream Crude Production, Refining & Foreign Trade\n")
    lines.append("### Table 3: Indigenous Crude Oil and Condensate Production by Regime (TMT) [Source: 4, 7]")
    lines.append("| Production Regime / Operator | Aug 2026 (P) | Jul 2026 | Aug 2025 | YoY % | FYTD 2026-27 | FYTD 2025-26 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in ds["table3_indigenous_crude"]:
        b = "**" if "Total" in r["regime"] else ""
        lines.append(f"| {b}{r['regime']}{b} | {r['aug26']} | {r['jul26']} | {r['aug25']} | {r['yoy']} | {r['fytd27']} | {r['fytd26']} |")
    lines.append("*Source: Directorate General of Hydrocarbons (DGH) [4], ONGC and OIL [7].*\n")
    
    lines.append("### Figure 1: Operator Share in Crude Production (%) [PPAC Table 3 Graph]")
    lines.append("* **ONGC (Nomination Fields):** 73.2% (1,644 TMT)")
    lines.append("* **OIL India Ltd:** 14.8% (332 TMT)")
    lines.append("* **Vedanta (Cairn Oil & Gas):** 3.8% (85 TMT)")
    lines.append("* **CEHL / Reliance / Sun Petro / Others:** 8.2% (185 TMT)\n")
    
    lines.append("### Table 4: Domestic Oil & Gas Production vis-à-vis Overseas Sovereign Production [Source: 4, 7]")
    lines.append("| Asset Origin / Operator | Hydrocarbon Stream | Aug 2026 (P) | FYTD 2026-27 | Asset Share % |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table4_overseas_production"]:
        lines.append(f"| {r['entity']} | {r['type']} | {r['aug26']} | {r['fytd27']} | {r['share']} |")
    lines.append("*Source: ONGC Videsh Ltd (OVL) [7], DGH [4].*\n")
    
    lines.append("### Table 5: High Sulphur (HS) & Low Sulphur (LS) Crude Oil Processing Diet [Source: 2, 6]")
    lines.append("| Crude Classification | Processing Volume (MMT) | Diet Share % | Representative Benchmark Grades |")
    lines.append("|---|---|---|---|")
    for r in ds["table5_crude_processing_diet"]:
        lines.append(f"| {r['crude_type']} | {r['volume_mmt']} | {r['share_pct']} | {r['key_grades']} |")
    lines.append("*Source: PPAC Table 5 [2], Refinery crude intake registers [6].*\n")
    
    lines.append("### Table 6: Quantity and Value of Crude Oil Imports & Trade Bill [Source: 3, 8]")
    lines.append("| Hydrocarbon Trade Stream | Quantity (MMT) | Value (USD B) | Value (INR Cr) | FYTD Qty (MMT) | FYTD Val (USD B) |")
    lines.append("|---|---|---|---|---|---|")
    for r in ds["table6_crude_imports_trade"]:
        lines.append(f"| {r['commodity']} | {r['qty_mmt']} | {r['val_usd_billion']} | {r['val_inr_crore']} | {r['fytd_qty_mmt']} | {r['fytd_val_usd']} |")
    lines.append("*Source: DGCIS Customs Border Clearance [3], RBI Exchange Rate (₹84.15/USD) [8].*\n")
    
    lines.append("### Table 7: Self-Sufficiency & Import Dependency in Petroleum Products [Source: 2]")
    lines.append("| Energy Commodity | Indigenous Supply | Total Domestic Req | Import Dependency % | Trade Status |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table7_self_sufficiency"]:
        lines.append(f"| {r['sector']} | {r['indigenous']} | {r['total_req']} | **{r['import_dependency']}** | {r['status']} |")
    lines.append("*Source: PPAC Table 7 [2].*\n")
    
    lines.append("### Table 8: Refineries Installed Capacity and Crude Throughput [Source: 2, 6]")
    lines.append("| Refining Sector | Installed Capacity (MMTPA) | Crude Processed (MMT) | Capacity Utilization % |")
    lines.append("|---|---|---|---|")
    for r in ds["table8_refineries_capacity"]:
        lines.append(f"| {r['sector']} | {r['installed_mmtpa']} | {r['crude_processed_mmt']} | **{r['utilization_pct']}** |")
    lines.append("*Source: PPAC Table 8 [2], Refinery operational reports [6].*\n")
    
    lines.append("### Table 9: Crude Oil & Product Pipeline Infrastructure [Source: 5]")
    lines.append("| Pipeline Trunkline Category | Length (km) | Installed Capacity (MMTPA) | Utilization % | Key Operators |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table9_pipelines_network"]:
        lines.append(f"| {r['network_type']} | {r['length_km']} | {r['capacity_mmtpa']} | {r['utilization_pct']} | {r['primary_operators']} |")
    lines.append("*Source: Petroleum & Natural Gas Regulatory Board (PNGRB) [5].*\n")
    
    lines.append("### Table 10: Gross Refining Margins (GRM) of Key Refineries ($/bbl) [Source: 2, 6, 10]")
    lines.append("| Refining Company / Entity | GRM Q1 FY 2026-27 | GRM FY 2025-26 | Nelson Complexity (NCI) |")
    lines.append("|---|---|---|---|")
    for r in ds["table10_grm_margins"]:
        lines.append(f"| {r['refinery_entity']} | {r['grm_q1_fy27']} | {r['grm_fy26']} | {r['complexity_nelson']} |")
    lines.append("*Source: Corporate Filings [6], Platts Assessments [10].*\n")
    lines.append("---")
    
    # Part C
    lines.append("## Part C: Petroleum Products (POL) Consumption & Regional Demand\n")
    lines.append("### Table 11(A): POL Consumption by Product (TMT) [Source: 2, 6]")
    lines.append("| Petroleum Product | Aug 2026 (P) | Jul 2026 | Aug 2025 | MoM % | YoY % | FYTD 26-27 | FYTD 25-26 | YTD % |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in ds["table11a_pol_consumption"]:
        b = "**" if "Total" in r["product"] else ""
        lines.append(f"| {b}{r['product']}{b} | {r['aug26']} | {r['jul26']} | {r['aug25']} | {r['mom']} | {r['yoy']} | {r['fytd27']} | {r['fytd26']} | {r['ytd_chg']} |")
    lines.append("*Source: PPAC Table 11(A) [2], OMC sales registers [6].*\n")
    
    lines.append("### Table 11(B): Regionwise POL Consumption Report (TMT) [Source: 2, 6]")
    lines.append("| Geographical Demand Region | Motor Spirit (MS) | High Speed Diesel (HSD) | Aviation Fuel (ATF) | LPG Total | Regional Total (TMT) | National Share % |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in ds["table11b_regional_consumption"]:
        lines.append(f"| {r['region']} | {r['ms_tmt']} | {r['hsd_tmt']} | {r['atf_tmt']} | {r['lpg_tmt']} | {r['total_tmt']} | {r['share']} |")
    lines.append("*Source: PPAC Table 11(B) [2], Regional OMC Dispatch Returns [6].*\n")
    
    lines.append("### Table 12: PDS Kerosene Allocation vs Upliftment [Source: 1, 2]")
    lines.append("| State Category / Jurisdiction | Allocation (TMT) | Upliftment (TMT) | Upliftment % | Subsidy Status |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table12_kerosene_allocation"]:
        lines.append(f"| {r['state_category']} | {r['allocation_tmt']} | {r['upliftment_tmt']} | {r['upliftment_pct']} | {r['subsidy_status']} |")
    lines.append("*Source: MoPNG PDS Cell [1], PPAC Table 12 [2].*\n")
    
    lines.append("### Table 13: Ethanol Blending Programme (EBP) Progress [Source: 1, 2]")
    lines.append("| Parameter | Value (Aug 2026) | Benchmark Target | Compliance Status |")
    lines.append("|---|---|---|---|")
    for r in ds["table13_ethanol_blending"]:
        lines.append(f"| {r['metric']} | **{r['value']}** | {r['benchmark_target']} | {r['compliance']} |")
    lines.append("*Source: Department of Food & Public Distribution (DFPD) & MoPNG Biofuel Cell [1].*\n")
    
    lines.append("### Table 14: National Downstream Marketing & Retail Distribution Infrastructure [Source: 1, 6]")
    lines.append("| Infrastructure Facility | August 2026 | August 2025 | Net Additions |")
    lines.append("|---|---|---|---|")
    for r in ds["table14_marketing_infrastructure"]:
        lines.append(f"| {r['facility']} | {r['aug26']} | {r['aug25']} | **{r['net_add']}** |")
    lines.append("*Source: PPAC Table 14 [2], OMC Physical Audits [6].*\n")
    lines.append("---")
    
    # Part D
    lines.append("## Part D: Liquefied Petroleum Gas (LPG) Marketing & PMUY Expansion\n")
    lines.append("### Table 15: LPG Consumption by Consumer Category (TMT) [Source: 1, 2, 6]")
    lines.append("| Consumer Category | Volume (TMT) | Category Share % | Active Consumer Base |")
    lines.append("|---|---|---|---|")
    for r in ds["table15_lpg_consumption_split"]:
        lines.append(f"| {r['category']} | {r['volume_tmt']} | {r['share_pct']} | {r['active_base']} |")
    lines.append("*Source: PPAC Table 15 [2], OMC LPG Sales Registers [6].*\n")
    
    lines.append("### Table 16: LPG Marketing Infrastructure & PMUY Enrolment [Source: 1, 6]")
    lines.append("| Parameter | August 2026 | August 2025 | YoY Growth / Change |")
    lines.append("|---|---|---|---|")
    for r in ds["table16_lpg_marketing_pmuy"]:
        lines.append(f"| {r['parameter']} | {r['aug26']} | {r['aug25']} | **{r['yoy_growth']}** |")
    lines.append("*Source: PMUY Central Dashboard [1], PPAC Table 16 [2].*\n")
    
    lines.append("### Table 17: Region-Wise PMUY Beneficiaries and Refill Rates [Source: 1, 6]")
    lines.append("| Geographical Region | PMUY Beneficiaries (Cr) | Average Refills / Year | Active Distributorships |")
    lines.append("|---|---|---|---|")
    for r in ds["table17_lpg_regional_refills"]:
        lines.append(f"| {r['region']} | {r['pmuy_customers_cr']} | {r['avg_refills_year']} | {r['active_distributors']} |")
    lines.append("*Source: PPAC Table 17 [2], OMC CRM Ledgers [6].*\n")
    lines.append("---")
    
    # Part E
    lines.append("## Part E: Natural Gas Sector, CBM & LNG Infrastructure\n")
    lines.append("### Table 18: National Natural Gas Balance & Off-take Split (MMSCM) [Source: 2, 3, 5]")
    lines.append("| Gas Flow / Component | Volume (MMSCM) | National Share % | Primary Sectoral End-Users |")
    lines.append("|---|---|---|---|")
    for r in ds["table18_natural_gas_balance"]:
        lines.append(f"| {r['component']} | {r['volume_mmscm']} | {r['share_pct']} | {r['primary_sources']} |")
    lines.append("*Source: PPAC Table 18 [2], DGCIS [3], PNGRB [5].*\n")
    
    lines.append("### Table 19: Coal Bed Methane (CBM) Production Projects [Source: 4]")
    lines.append("| CBM Block / Field | State | Aug 2026 (P) (MMSCM) | FYTD 2026-27 (MMSCM) | Operational Status |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table19_cbm_development"]:
        lines.append(f"| {r['cbm_block']} | {r['state']} | {r['aug26_mmscm']} | {r['fytd_mmscm']} | {r['status']} |")
    lines.append("*Source: DGH CBM Division [4].*\n")
    
    lines.append("### Table 20: Natural Gas Transmission Pipeline Network [Source: 5]")
    lines.append("| Authorized Operator / Trunkline | Operational Length (km) | Design Capacity (MMSCMD) | Utilization % |")
    lines.append("|---|---|---|---|")
    for r in ds["table20_gas_pipeline_network"]:
        lines.append(f"| {r['operator']} | {r['operational_km']} | {r['capacity_mmscmd']} | **{r['utilization_pct']}** |")
    lines.append("*Source: PNGRB Gas Pipeline Register [5].*\n")
    
    lines.append("### Table 21: Existing LNG Regasification Terminals [Source: 5]")
    lines.append("| Terminal Name | State | Installed Capacity (MMTPA) | Utilization % | Sendout (MMSCMD) |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table21_lng_terminals"]:
        lines.append(f"| {r['terminal_name']} | {r['state']} | {r['capacity_mmtpa']} | **{r['utilization_pct']}** | {r['sendout_mmscmd']} |")
    lines.append("*Source: PNGRB LNG Authorizations [5].*\n")
    
    lines.append("### Table 22: City Gas Distribution (CGD) Infrastructure [Source: 5]")
    lines.append("| Infrastructure Metric | August 2026 | August 2025 | Coverage / Growth |")
    lines.append("|---|---|---|---|")
    for r in ds["table22_cgd_infrastructure"]:
        lines.append(f"| {r['parameter']} | {r['aug26']} | {r['aug25']} | **{r['coverage_pct']}** |")
    lines.append("*Source: PNGRB CGD Progress Reports [5].*\n")
    lines.append("---")
    
    # Part F
    lines.append("## Part F: Pricing Benchmarks, Taxes, Subsidies & PSU CAPEX\n")
    lines.append("### Table 23: Domestic Natural Gas Pricing (APM Formula) [Source: 1, 2]")
    lines.append("| Pricing Regime | Formula Basis | Effective Price ($/MMBTU) | Statutory Status |")
    lines.append("|---|---|---|---|")
    for r in ds["table23_domestic_gas_prices"]:
        lines.append(f"| {r['pricing_regime']} | {r['formula_basis']} | {r['effective_price']} | **{r['statutory_status']}** |")
    lines.append("*Source: MoPNG Kirit Parikh Formula Notifications [1], PPAC [2].*\n")
    
    lines.append("### Table 24: Retail Selling Prices of CNG & PNG in Selected Cities [Source: 1, 6]")
    lines.append("| City | CNG Price (₹/kg) | Domestic PNG (₹/SCM) | State VAT on CNG (%) |")
    lines.append("|---|---|---|---|")
    for r in ds["table24_metro_cng_png_prices"]:
        lines.append(f"| {r['city']} | {r['cng_price']} | {r['png_domestic']} | {r['state_vat_cng']} |")
    lines.append("*Source: CGD Operator Tariff Notices [6].*\n")
    
    lines.append("### Table 25: Retail Selling Price Buildup & Four-City Comparison [Source: 1, 6]")
    lines.append("| City | Petrol (MS) (₹/L) | Diesel (HSD) (₹/L) | LPG Domestic (14.2kg) |")
    lines.append("|---|---|---|---|")
    for r in ds["table25_pricing_tax_buildup"]["metro_comparison"]:
        lines.append(f"| {r['metro']} | {r['petrol_inr_l']} | {r['diesel_inr_l']} | {r['lpg_domestic_cylinder']} |")
    lines.append("*Source: IOCL, BPCL, HPCL RSP Notices [6].*\n")
    
    lines.append("### Table 26: Capital Expenditure (CAPEX) of Major PSU Oil Companies [Source: 1, 7]")
    lines.append("| PSU Oil & Gas Entity | BE FY 2026-27 | Actual Spent (Aug 2026) | Achievement % | Focus Areas |")
    lines.append("|---|---|---|---|---|")
    for r in ds["table26_psu_capex"]:
        lines.append(f"| {r['psu_entity']} | {r['annual_budget']} | {r['actual_spent_aug26']} | **{r['achievement_pct']}** | {r['major_projects']} |")
    lines.append("*Source: MoPNG Monthly CAPEX Dashboard [1], Published Accounts [7].*\n")
    
    lines.append("### Table 27: Standard Hydrocarbon Conversion Factors [Source: 2]")
    lines.append("| Measurement Dimension | Sovereign Statutory Conversion Ratio |")
    lines.append("|---|---|")
    for r in ds["table27_conversion_factors"]:
        lines.append(f"| **{r['dimension']}** | {r['conversion']} |")
    lines.append("*Source: PPAC Ready Reckoner Technical Annexure [2].*\n")
    lines.append("---")
    
    # Section 7: Citations
    lines.append("## Section 7: Statutory Data Sources & Numbered Citations\n")
    lines.append("| Ref ID | Statutory Authority / Agency | Jurisdiction, Regulatory Mandate & Scope | Reporting Cycle |")
    lines.append("|---|---|---|---|")
    lines.append("| **[1]** | **Ministry of Petroleum & Natural Gas (MoPNG)** | Apex federal ministry governing hydrocarbon policy, PMUY subsidies, administrative price mechanisms (APM), and Gazette directives under the Petroleum Act. | Monthly / Continuous |")
    lines.append("| **[2]** | **Petroleum Planning & Analysis Cell (PPAC)** | Attached statutory office of MoPNG maintaining official national hydrocarbon repository, Ready Reckoners, and consumption ledgers. | Monthly (T+0 / T+2 Close) |")
    lines.append("| **[3]** | **Directorate General of Commercial Intelligence & Statistics (DGCIS)** | Ministry of Commerce & Industry division providing verified customs bills of entry, merchandise trade valuations, and port clearances. | Monthly Trade Close |")
    lines.append("| **[4]** | **Directorate General of Hydrocarbons (DGH)** | Upstream technical regulator monitoring Production Sharing Contracts (PSC), Revenue Sharing Contracts (RSC), and CBM operations. | Monthly E&P Audits |")
    lines.append("| **[5]** | **Petroleum & Natural Gas Regulatory Board (PNGRB)** | Downstream regulator overseeing pipeline common carriers, City Gas Distribution (CGD) bidding rounds, PNG domestic connections, and CNG stations. | Quarterly / Monthly Audits |")
    lines.append("| **[6]** | **Public Sector Oil Marketing Companies (OMCs)** | Primary ERP sales records, refinery runs, and marketing logs from Indian Oil (IOCL), Bharat Petroleum (BPCL), and Hindustan Petroleum (HPCL). | Daily / Monthly Returns |")
    lines.append("| **[7]** | **Upstream & Refining PSUs** | Physical extraction, throughput, and CAPEX accounts from ONGC, Oil India (OIL), GAIL (India), CPCL, MRPL, and Numaligarh Refinery (NRL). | Monthly Operating Returns |")
    lines.append("| **[8]** | **Reserve Bank of India (RBI)** | Central bank of India publishing sovereign foreign exchange reserves, reference exchange rates (USD/INR), and monetary aggregates. | Weekly / Monthly Close |")
    lines.append("| **[9]** | **MoSPI & Registrar General of India (RGI)** | Central statistics ministry compiling Index of Industrial Production (IIP Base: 2022-23) and sovereign population projections. | Monthly / Annual Census Projections |")
    lines.append("| **[10]** | **S&P Global Platts & ICE Benchmark Services** | International pricing reporting agencies providing verified spot price settlements for Dated Brent, Dubai, and Oman crude assessments. | Daily Trading Settlement Close |")
    
    return "\n".join(lines)

def create_google_doc():
    md = generate_markdown("2026-08")
    title = "PPAC Monthly Ready Reckoner — August 2026 (Official Sovereign Executive Report)"
    
    p = subprocess.Popen(
        ['/google/bin/releases/codemind-mcp-servers/workspace_server.par'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    p.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'ppac-publisher', 'version': '1.0'}}}) + '\n')
    p.stdin.flush()
    p.stdout.readline()
    
    call_req = {
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'tools/call',
        'params': {
            'name': 'create_document',
            'arguments': {
                'title': title,
                'markdown_text': md,
                'content_type': 'doc'
            }
        }
    }
    p.stdin.write(json.dumps(call_req) + '\n')
    p.stdin.flush()
    call_resp = json.loads(p.stdout.readline())
    p.terminate()
    
    print("Google Doc Creation Result:")
    print(json.dumps(call_resp, indent=2))
    return call_resp

if __name__ == "__main__":
    create_google_doc()
