# 02 Quantitative Analysis

Purpose: maintain the source of truth for the Rix private-fund quantitative analysis workflow.

This folder owns the rules, schemas, calculation logic, checks, and memo-aligned output specification for the quant workbook. The Google Sheet is the team interface; this folder is the version-controlled source of truth.

## Current design

The workbook is split into three layers:

1. Inputs - literal outputs from Data Extraction and Cleaning, plus benchmark and public-data inputs.
2. Calculations - formulas only, pulling from input tabs. No hardcoded derived values.
3. Outputs - memo-ready sections matching the Investment Memo structure.

## Workbook tabs

Inputs:
- 01_GP
- 02_Team
- 03_Funds
- 04_Investments
- 05_Cashflows_Gross
- 06_Cashflows_Net
- 07_Benchmarks
- 08_Public_Data

Calculations:
- 20_Checks
- 21_Fund_Calcs
- 22_Company_Calcs
- 23_Team_Calcs
- 24_Benchmark_Calcs
- 25_Scoring_Calcs_PE / VC / Secondaries

Outputs:
- 40_Executive_Summary
- 41_Opportunity
- 42_Strategy
- 43_Performance
- 44_Portfolio
- 45_Value_Creation
- 46_Team
- 47_Alignment_LPs_CoInvest
- 48_Risks_and_Red_Flags
- 49_Scoring_and_Data_Quality

## Operating rules

- The extraction workbook remains the upstream source of facts.
- Quant workbooks are always created in the relevant Drive folder's z_workings folder.
- The input tabs should mirror extraction output; manual edits should be exceptional and visible.
- Calculations should be simple, formula-driven, and auditable.
- Outputs should be organised around the memo, not around the old workbook.
- Scoring is downstream of evidence and should separate calculated score, override score, and final score.
- Checks in this quant workbook validate transfer integrity and odd calculations; extraction-level checks should remain in the extraction workflow.
