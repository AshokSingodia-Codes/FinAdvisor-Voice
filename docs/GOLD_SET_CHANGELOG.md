# Gold Benchmark Set Changelog

This document tracks all modifications made to `tests/eval/gold_set*.json` after `tests/eval/gold_set_test.sha256` was established and frozen at commit `04aeb1f`.

---

## Modification Log

### Commit `580c5ff8ce908ed8456e75c86ea2046adfd53e1b`
- **Date:** Sun Nov 1 05:42:46 2026 +05:30
- **Modified Files:** `tests/eval/gold_set.json`, `tests/eval/gold_set_dev.json` (Note: `tests/eval/gold_set_test.json` remains frozen).
- **`q015` (Dev)**: Adjusted topic to general financial ratio analysis to align with indexed textbook chapters.
- **`q025` (Dev)**: Replaced references to Burton Malkiel's *A Random Walk Down Wall Street* with modern portfolio theory passive diversification.

### Task 2 Update: Strict Value & Passage Grounding Audit
- **Date:** Sun Nov 1 06:33:00 2026 +05:30
- **Modified Files:** `tests/eval/gold_set.json`, `tests/eval/gold_set_dev.json` (Note: `tests/eval/gold_set_test.json` was NOT modified and remains frozen under `gold_set_test.sha256`).

#### 1. `q_ret_057` (Split: `dev`)
- **Old Expected Answer:** `"Revenue increased by 2.0% (from $383,285 million to $391,035 million)"`
- **New Expected Answer:** `"Total net sales increased by 2% from $383,285 million in 2023 to $391,035 million in 2024"`
- **Reason:** In Apple's FY 2024 10-K, Item 7 specifically reports the audited figure as `"Total net sales $ 391,035 2 % $ 383,285 (3)%"`. The answer and gold keywords were aligned to the audited table text.

#### 2. `q015` (Split: `dev`)
- **Old Expected Answer:** `"Financial ratios evaluate profitability, liquidity, and operational efficiency across accounting statements."`
- **New Expected Answer:** `"Perform ratio analysis, cash-flow analysis, and risk-capacity assessment using Net Worth, Liquidity Ratios, and Debt-Service Coverage Ratio (DSCR)."`
- **Reason:** Aligned to the exact verbatim financial analysis methodology block in Chapter 1 of `Ultimate_Finance_Knowledge_Base.md`.

#### 3. `q009`, `q_ret_053`, `q_ret_061`, `q_ret_065`, `q_ret_067`, `q_ret_069` (Split: `dev`)
- **Reason:** Removed parenthetical redundant phrases (such as `($... billion)`) to require exact adherence to audited 10-K millions/percentages tables.

---

## Test Split Freeze Verification & Grounding Audit Summary
- `tests/eval/gold_set_test.json` SHA-256 hash: `cd3c4aae4760ad05c39d512752df43c41d25f921a1266f3045ee77c696d25126`
- **Integrity Rule**: As instructed, zero changes were made to `tests/eval/gold_set_test.json`.
- **Audit Outcomes (from `reports/latest/gold_source_audit.json` across 54 retrieval items)**:
  - **Verified items**: 33
  - **Unverified (conceptual)**: 1 (`q025`)
  - **Failed (numeric proximity)**: 20
- **Crucial Caveat**: All 20 failed items reside in the frozen test split (because the test set expected answers include parenthetical conversions such as `($... billion)` that do not appear verbatim within 300 characters of the segment topic in the raw 10-K tables). Because the test split was intentionally left unchanged to preserve frozen SHA-256 integrity, retrieval results on the test split are **NOT reliable** until a new test split (`gold_set_test_v2.json`) is authored, audited, and frozen. Never state that 54/54 items are verified.
