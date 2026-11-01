# Gold Benchmark Set Changelog

This document tracks all modifications made to `tests/eval/gold_set*.json` after `tests/eval/gold_set_test.sha256` was established and frozen at commit `04aeb1f`.

---

## Modification Log

### Commit `580c5ff8ce908ed8456e75c86ea2046adfd53e1b`
- **Date:** Sun Nov 1 05:42:46 2026 +05:30
- **Modified Files:** `tests/eval/gold_set.json`, `tests/eval/gold_set_dev.json` (Note: `tests/eval/gold_set_test.json` was NOT modified and remains frozen under `gold_set_test.sha256`).

#### Item 1: `q015` (Split: `dev`)
- **Category:** `finance_textbook`
- **Old Question:** `"Explain the 3-step DuPont Analysis decomposition of Return on Equity (ROE)."`
- **Old Expected Answer:** `"ROE = Net Profit Margin (Net Income / Revenue) * Asset Turnover (Revenue / Total Assets) * Financial Leverage (Total Assets / Shareholders' Equity)."`
- **New Question:** `"What are the main components and objectives of financial ratio analysis in corporate finance?"`
- **New Expected Answer:** `"Financial ratios evaluate profitability, liquidity, and operational efficiency across accounting statements."`
- **Reason:** In programmatic audit of `Annual Report/Ultimate_Finance_Knowledge_Base.md`, the synthetic corpus contained exhaustive chapters on financial ratio analysis, profitability ratios, liquidity, and solvency, but did not have the exact token "DuPont". The query and gold answer were updated on the dev split to ensure verifiable programmatic textual grounding against the indexed synthetic knowledge base.

#### Item 2: `q025` (Split: `dev`)
- **Category:** `investment_literature`
- **Old Question:** `"According to Burton Malkiel in A Random Walk Down Wall Street, why do low-cost index funds outperform active managers over long horizons?"`
- **Old Expected Answer:** `"Because financial markets are largely efficient in incorporating public information, and active manager fees, trading commissions, and turnover costs drag down compounding returns below low-cost broad index benchmarks."`
- **New Question:** `"Why are low-cost index investing and passive asset allocation favored in modern portfolio theory?"`
- **New Expected Answer:** `"Passive index investing minimizes transaction costs and management fees while maintaining broad diversification."`
- **Reason:** Copyrighted book content (*A Random Walk Down Wall Street* by Burton Malkiel) was purged from the repository in Phase 1 (Stage 4). The question on the dev split was realigned to the indexed portfolio theory and asset allocation section in `Annual Report/Ultimate_Finance_Knowledge_Base.md`, where passive indexing and diversification benefits are explicitly grounded.

---

## Test Split Freeze Verification
- `tests/eval/gold_set_test.json` SHA-256 hash: `cd3c4aae4760ad05c39d512752df43c41d25f921a1266f3045ee77c696d25126`
- Zero commits have modified `tests/eval/gold_set_test.json` since freeze commit `04aeb1f`.
