"""
Comprehensive Indian Tax Engine & Master Knowledge Base
Up-to-date with Budget 2024 Amendments, FY 2024-25 (AY 2025-26) & FY 2025-26.
"""

from typing import Dict, Any, Optional

INDIAN_TAX_RULES_MASTER = """
# 🇮🇳 MASTER INDIAN TAX RULES (FY 2024-25 / AY 2025-26 & FY 2025-26)

## 1. INCOME TAX REGIMES & SLABS

### A. New Tax Regime (Default u/s 115BAC)
* **Standard Deduction**: ₹75,000 for salaried employees and pensioners (increased from ₹50,000 in Budget 2024).
* **Tax Slabs**:
  - Up to ₹3,00,000: **0% (NIL)**
  - ₹3,00,001 to ₹7,00,000: **5%**
  - ₹7,00,001 to ₹10,00,000: **10%**
  - ₹10,00,001 to ₹12,00,000: **15%**
  - ₹12,00,001 to ₹15,00,000: **20%**
  - Above ₹15,00,000: **30%**
* **Rebate u/s 87A**: Tax rebate up to ₹25,000 for taxable income up to ₹7,00,000. Effectively, salaried individuals with Gross Salary up to **₹7,75,000** pay **₹0 tax** (₹7.75L - ₹75k std ded = ₹7.00L taxable).
* **Allowed Deductions in New Regime**:
  - Standard Deduction: ₹75,000
  - Employer contribution to NPS u/s 80CCD(2) up to 14% of salary (Govt) / 14% (Private sector increased from 10% in Budget 2024).
  - Agniveer Corpus Fund u/s 80CCH.
  - Family Pension deduction: ₹25,000 (increased from ₹15,000).
  - Transport allowance for divyang/specially-abled.

### B. Old Tax Regime (Optional)
* **Standard Deduction**: ₹50,000.
* **Tax Slabs**:
  - Up to ₹2,50,000: **0% (NIL)** (Senior Citizens 60-80 yrs: ₹3,00,000; Super Senior >80 yrs: ₹5,00,000)
  - ₹2,50,001 to ₹5,00,000: **5%**
  - ₹5,00,001 to ₹10,00,000: **20%**
  - Above ₹10,00,000: **30%**
* **Rebate u/s 87A**: Tax rebate up to ₹12,500 for taxable income up to ₹5,00,000 (Nil tax up to ₹5.50L for salaried with std ded).
* **Major Deductions in Old Regime**:
  - **Section 80C**: Up to ₹1,50,000 (EPF, PPF, ELSS Mutual Funds, Life Insurance Premium, Home Loan Principal repayment, SSY, NSC, 5-yr Tax-saving FD, Children's Tuition fees).
  - **Section 80D (Health Insurance)**:
    - Self, Spouse, Dependent Children: Up to ₹25,000 (₹50,000 if senior citizen).
    - Parents: Additional up to ₹25,000 (₹50,000 if senior citizen). Max deduction can be up to ₹1,00,000.
    - Preventive health checkup: Up to ₹5,000 (within the 80D overall limit).
  - **Section 80CCD(1B)**: Additional NPS self-contribution up to ₹50,000 over and above 80C.
  - **Section 24(b)**: Home loan interest deduction up to ₹2,00,000 for self-occupied property.
  - **Section 80E**: Interest paid on higher education loan (100% deductible for 8 years, no upper cap).
  - **Section 80G**: Donations to eligible charitable funds (50% or 100% deduction depending on fund).
  - **Section 80TTA**: Savings account interest up to ₹10,000 (Individual/HUF < 60 yrs).
  - **Section 80TTB**: Interest income from Savings & FDs up to ₹50,000 for Senior Citizens.
  - **HRA Exemption u/s 10(13A)**: Minimum of (1) Actual HRA received, (2) Rent paid - 10% of basic salary, (3) 50% of basic (metro) or 40% (non-metro).
  - **LTA u/s 10(5)**: Exemption for travel within India twice in a block of 4 calendar years.

---

## 2. CAPITAL GAINS TAXATION (Budget 2024 Overhaul & Current Rules)

### A. Listed Equity Shares & Equity Mutual Funds (>65% equity)
* **Holding Period for Long-Term**: > 12 months.
* **Short-Term Capital Gains (STCG u/s 111A)**: **20%** (increased from 15% w.e.f. July 23, 2024).
* **Long-Term Capital Gains (LTCG u/s 112A)**: **12.5%** (increased from 10% w.e.f. July 23, 2024).
* **LTCG Exemption Limit**: First **₹1,25,000 per financial year is 100% tax-free** (increased from ₹1,00,000).
* **STT (Securities Transaction Tax)**: Payable on buy/sell of equity and equity funds.

### B. Debt Mutual Funds & Fixed Income Products
* **Specified Mutual Funds (>65% Debt bought after 1-Apr-2023)**: Taxed at normal applicable income tax slab rates (deemed short-term capital asset u/s 50AA regardless of holding period).
* **Pre-April 1, 2023 Debt Funds held > 36 months**: LTCG 12.5% without indexation (or 20% with indexation if grandfathered).

### C. Real Estate / Immovable Property
* **Holding Period for Long-Term**: > 24 months.
* **STCG**: Taxed at applicable slab rates.
* **LTCG**: **12.5% without indexation** (For property acquired before July 23, 2024, resident individuals/HUFs can choose lower of 12.5% without indexation OR 20% with indexation).
* **Exemptions**:
  - Section 54: Reinvestment in residential house property (up to ₹10 Crore).
  - Section 54EC: Capital Gain Bonds (NHAI, REC, PFC, IRFC) up to ₹50 Lakh within 6 months.

### D. Physical Gold, Gold ETFs, & Sovereign Gold Bonds (SGB)
* **Holding Period for Long-Term**: > 24 months (reduced from 36 months).
* **Physical Gold / Gold ETFs / Gold Mutual Funds**:
  - STCG (< 24 months): Slab rate.
  - LTCG (> 24 months): **12.5% without indexation**.
* **Sovereign Gold Bonds (SGB)**:
  - Capital Gains on redemption at maturity (8 years) for individuals: **100% TAX-FREE**.
  - Annual 2.5% coupon interest: Taxed at slab rates.

### E. Unlisted Equity Shares & Private Assets
* **Holding Period for Long-Term**: > 24 months.
* **STCG**: Slab rates.
* **LTCG**: **12.5% without indexation** (for both residents and non-residents).

### F. Virtual Digital Assets (Crypto / NFTs u/s 115BBH)
* **Tax Rate**: Flat **30%** on gains + 4% cess.
* **TDS u/s 194S**: 1% TDS on transfer value exceeding ₹50,000 (or ₹10,000 for specific persons).
* **No Deduction**: No deduction allowed except cost of acquisition.
* **No Loss Set-off**: Crypto losses cannot be set off against any other income or crypto profits.

---

## 3. SURCHARGES & HEALTH & EDUCATION CESS

* **Health and Education Cess**: **4%** applied on (Income Tax + Surcharge) across all categories.
* **Surcharge Rates (Individuals/HUF)**:
  - Total Income ₹50 Lakh to ₹1 Crore: **10%**
  - Total Income ₹1 Crore to ₹2 Crore: **15%**
  - Total Income ₹2 Crore to ₹5 Crore: **25%**
  - Total Income > ₹5 Crore: **25% under New Regime** (capped at 25%) | **37% under Old Regime**.
  - Surcharge on STCG (111A), LTCG (112, 112A), and Dividend income is capped at **15%**.

---

## 4. ADVANCE TAX SCHEDULE & INTEREST (Sec 234A, 234B, 234C)
Applicable if net tax liability after TDS exceeds **₹10,000** in a financial year:
1. By 15th June: 15% of total tax
2. By 15th September: 45% of total tax
3. By 15th December: 75% of total tax
4. By 15th March: 100% of total tax
* Senior citizens (>=60 yrs) not having business/professional income are **exempt** from advance tax.

---

## 5. COMMON TDS SECTIONS
* **Section 192**: Salary (computed at slab rates).
* **Section 194A**: Bank FD Interest (TDS 10% if interest > ₹40,000 for regular, > ₹50,000 for senior citizens).
* **Section 194**: Dividend from domestic company (10% if > ₹5,000).
* **Section 194J**: Professional fees (10% or 2% for technical services).
* **Section 194C**: Payments to contractors (1% for individual/HUF, 2% for others).
* **Section 194IB**: Rent paid by individual/HUF exceeding ₹50,000/month (TDS 2% or 5%).
* **Section 194Q**: Purchase of goods exceeding ₹50 Lakhs (0.1% TDS).
"""


def calculate_income_tax_new_regime(gross_income: float, is_salaried: bool = True) -> Dict[str, Any]:
    """
    Calculates exact Indian Income Tax under New Tax Regime (Section 115BAC) for FY 2024-25 / AY 2025-26.
    """
    std_deduction = 75000.0 if is_salaried else 0.0
    taxable_income = max(0.0, gross_income - std_deduction)

    slabs = [
        (300000, 0.0),
        (400000, 0.05),  # 3L to 7L (span 4L)
        (300000, 0.10),  # 7L to 10L (span 3L)
        (200000, 0.15),  # 10L to 12L (span 2L)
        (300000, 0.20),  # 12L to 15L (span 3L)
        (float('inf'), 0.30)  # > 15L
    ]

    breakdown = []
    remaining = taxable_income
    raw_tax = 0.0
    slab_starts = [0, 300000, 700000, 1000000, 1200000, 1500000]

    for i, (span, rate) in enumerate(slabs):
        if remaining <= 0:
            break
        taxable_in_slab = min(remaining, span)
        tax_in_slab = taxable_in_slab * rate
        raw_tax += tax_in_slab
        start = slab_starts[i]
        end = start + span if span != float('inf') else "Above"
        breakdown.append({
            "slab": f"₹{start:,.0f} to ₹{end:,.0f}" if isinstance(end, (int, float)) else f"> ₹{start:,.0f}",
            "rate": f"{rate*100:.0f}%",
            "taxable_amount": taxable_in_slab,
            "tax": tax_in_slab
        })
        remaining -= taxable_in_slab

    # Section 87A Rebate in New Regime (up to ₹25,000 for taxable income <= 7,00,000)
    rebate_87a = 0.0
    if taxable_income <= 700000.0:
        rebate_87a = raw_tax
        tax_after_rebate = 0.0
    else:
        tax_after_rebate = raw_tax

    # Surcharge
    surcharge = 0.0
    if taxable_income > 50000000:
        surcharge = tax_after_rebate * 0.25
    elif taxable_income > 20000000:
        surcharge = tax_after_rebate * 0.25
    elif taxable_income > 10000000:
        surcharge = tax_after_rebate * 0.15
    elif taxable_income > 5000000:
        surcharge = tax_after_rebate * 0.10

    # 4% Cess
    cess = (tax_after_rebate + surcharge) * 0.04
    total_tax = tax_after_rebate + surcharge + cess

    return {
        "regime": "New Tax Regime (u/s 115BAC)",
        "gross_income": gross_income,
        "standard_deduction": std_deduction,
        "taxable_income": taxable_income,
        "raw_tax": raw_tax,
        "rebate_87a": rebate_87a,
        "tax_after_rebate": tax_after_rebate,
        "surcharge": surcharge,
        "cess_4pct": cess,
        "total_tax": round(total_tax, 2),
        "effective_tax_rate": f"{(total_tax / gross_income * 100):.2f}%" if gross_income > 0 else "0%",
        "breakdown": breakdown
    }


def calculate_income_tax_old_regime(
    gross_income: float,
    is_salaried: bool = True,
    deduction_80c: float = 0.0,
    deduction_80d: float = 0.0,
    home_loan_interest_24b: float = 0.0,
    nps_80ccd_1b: float = 0.0,
    other_deductions: float = 0.0,
    age: int = 30
) -> Dict[str, Any]:
    """
    Calculates exact Indian Income Tax under Old Tax Regime with all standard deductions (80C, 80D, 24b, NPS).
    """
    std_deduction = 50000.0 if is_salaried else 0.0
    capped_80c = min(150000.0, max(0.0, deduction_80c))
    capped_80d = min(100000.0, max(0.0, deduction_80d))
    capped_24b = min(200000.0, max(0.0, home_loan_interest_24b))
    capped_nps = min(50000.0, max(0.0, nps_80ccd_1b))

    total_deductions = std_deduction + capped_80c + capped_80d + capped_24b + capped_nps + max(0.0, other_deductions)
    taxable_income = max(0.0, gross_income - total_deductions)

    # Basic exemption by age
    if age >= 80:
        exempt_limit = 500000
    elif age >= 60:
        exempt_limit = 300000
    else:
        exempt_limit = 250000

    raw_tax = 0.0
    breakdown = []

    if taxable_income > exempt_limit:
        # Tier 1 (up to 5L)
        slab1_span = 500000 - exempt_limit
        taxable_slab1 = min(taxable_income - exempt_limit, slab1_span)
        tax_slab1 = taxable_slab1 * 0.05
        raw_tax += tax_slab1
        breakdown.append({
            "slab": f"₹{exempt_limit:,.0f} to ₹5,00,000",
            "rate": "5%",
            "taxable_amount": taxable_slab1,
            "tax": tax_slab1
        })

    if taxable_income > 500000:
        # Tier 2 (5L to 10L)
        taxable_slab2 = min(taxable_income - 500000, 500000)
        tax_slab2 = taxable_slab2 * 0.20
        raw_tax += tax_slab2
        breakdown.append({
            "slab": "₹5,00,001 to ₹10,00,000",
            "rate": "20%",
            "taxable_amount": taxable_slab2,
            "tax": tax_slab2
        })

    if taxable_income > 1000000:
        # Tier 3 (> 10L)
        taxable_slab3 = taxable_income - 1000000
        tax_slab3 = taxable_slab3 * 0.30
        raw_tax += tax_slab3
        breakdown.append({
            "slab": "> ₹10,00,000",
            "rate": "30%",
            "taxable_amount": taxable_slab3,
            "tax": tax_slab3
        })

    # Rebate 87A (taxable <= 5,00,000)
    rebate_87a = 0.0
    if taxable_income <= 500000:
        rebate_87a = min(raw_tax, 12500.0)
        tax_after_rebate = max(0.0, raw_tax - rebate_87a)
    else:
        tax_after_rebate = raw_tax

    # Surcharge
    surcharge = 0.0
    if taxable_income > 50000000:
        surcharge = tax_after_rebate * 0.37
    elif taxable_income > 20000000:
        surcharge = tax_after_rebate * 0.25
    elif taxable_income > 10000000:
        surcharge = tax_after_rebate * 0.15
    elif taxable_income > 5000000:
        surcharge = tax_after_rebate * 0.10

    # Cess
    cess = (tax_after_rebate + surcharge) * 0.04
    total_tax = tax_after_rebate + surcharge + cess

    return {
        "regime": "Old Tax Regime",
        "gross_income": gross_income,
        "standard_deduction": std_deduction,
        "deductions_claimed": {
            "80C": capped_80c,
            "80D": capped_80d,
            "24b_home_loan": capped_24b,
            "80CCD_1B_NPS": capped_nps,
            "other": other_deductions,
            "total": total_deductions
        },
        "taxable_income": taxable_income,
        "raw_tax": raw_tax,
        "rebate_87a": rebate_87a,
        "tax_after_rebate": tax_after_rebate,
        "surcharge": surcharge,
        "cess_4pct": cess,
        "total_tax": round(total_tax, 2),
        "effective_tax_rate": f"{(total_tax / gross_income * 100):.2f}%" if gross_income > 0 else "0%",
        "breakdown": breakdown
    }


def compare_tax_regimes(
    gross_income: float,
    is_salaried: bool = True,
    deduction_80c: float = 150000.0,
    deduction_80d: float = 25000.0,
    home_loan_interest_24b: float = 0.0,
    nps_80ccd_1b: float = 0.0,
    other_deductions: float = 0.0
) -> Dict[str, Any]:
    """
    Compares New Tax Regime vs Old Tax Regime and provides optimal recommendation.
    """
    new_res = calculate_income_tax_new_regime(gross_income, is_salaried)
    old_res = calculate_income_tax_old_regime(
        gross_income, is_salaried, deduction_80c, deduction_80d,
        home_loan_interest_24b, nps_80ccd_1b, other_deductions
    )

    savings = abs(new_res["total_tax"] - old_res["total_tax"])
    if new_res["total_tax"] < old_res["total_tax"]:
        recommended = "New Tax Regime"
        advice = f"You save ₹{savings:,.2f} under the New Tax Regime."
    elif old_res["total_tax"] < new_res["total_tax"]:
        recommended = "Old Tax Regime"
        advice = f"You save ₹{savings:,.2f} under the Old Tax Regime by claiming ₹{old_res['deductions_claimed']['total']:,.0f} in deductions."
    else:
        recommended = "Either (Identical Tax)"
        advice = "Both regimes result in the exact same tax liability."

    return {
        "gross_income": gross_income,
        "new_regime": new_res,
        "old_regime": old_res,
        "recommended_regime": recommended,
        "tax_savings": round(savings, 2),
        "advisor_verdict": advice
    }


def calculate_capital_gains_tax(
    asset_type: str,
    buy_price: float,
    sell_price: float,
    holding_months: int
) -> Dict[str, Any]:
    """
    Computes Capital Gains Tax under the revised July 2024 / FY 2024-25 Indian tax rules.
    """
    gain = sell_price - buy_price
    if gain <= 0:
        return {
            "asset_type": asset_type,
            "status": "Loss",
            "capital_loss": abs(gain),
            "tax_payable": 0.0,
            "notes": "Capital loss can be set off or carried forward for up to 8 assessment years."
        }

    asset_lower = asset_type.lower()
    tax_rate = 0.0
    is_long_term = False
    exemption = 0.0
    taxable_gain = gain

    if "equity" in asset_lower or "stock" in asset_lower or "mutual_fund" in asset_lower or "share" in asset_lower:
        is_long_term = holding_months > 12
        if is_long_term:
            # LTCG: 12.5% above ₹1.25 Lakh exemption
            exemption = min(gain, 125000.0)
            taxable_gain = max(0.0, gain - exemption)
            tax_rate = 0.125
            rule_ref = "Section 112A (LTCG > 12 months @ 12.5% above ₹1.25L exemption)"
        else:
            # STCG: 20%
            tax_rate = 0.20
            rule_ref = "Section 111A (STCG <= 12 months @ 20%)"

    elif "property" in asset_lower or "real_estate" in asset_lower or "house" in asset_lower:
        is_long_term = holding_months > 24
        if is_long_term:
            tax_rate = 0.125
            rule_ref = "LTCG on Real Estate > 24 months @ 12.5% without indexation (Budget 2024)"
        else:
            rule_ref = "STCG on Real Estate <= 24 months (Taxed at normal income tax slab rates)"
            return {
                "asset_type": asset_type,
                "holding_months": holding_months,
                "gain_type": "STCG",
                "capital_gain": gain,
                "tax_rate": "Applicable Income Tax Slab Rate",
                "notes": "Added to total income and taxed as per your slab."
            }

    elif "gold" in asset_lower:
        is_long_term = holding_months > 24
        if is_long_term:
            tax_rate = 0.125
            rule_ref = "LTCG on Gold > 24 months @ 12.5% without indexation"
        else:
            rule_ref = "STCG on Gold <= 24 months (Taxed at normal slab rates)"
            return {
                "asset_type": asset_type,
                "holding_months": holding_months,
                "gain_type": "STCG",
                "capital_gain": gain,
                "tax_rate": "Applicable Income Tax Slab Rate",
                "notes": "Added to total income and taxed as per your slab."
            }

    elif "crypto" in asset_lower or "vda" in asset_lower or "bitcoin" in asset_lower:
        tax_rate = 0.30
        rule_ref = "Section 115BBH (Flat 30% on Virtual Digital Assets + 1% TDS u/s 194S)"
        is_long_term = False

    else:
        # Generic unlisted/other asset
        is_long_term = holding_months > 24
        if is_long_term:
            tax_rate = 0.125
            rule_ref = "LTCG on Unlisted/Other Assets > 24 months @ 12.5%"
        else:
            rule_ref = "STCG on Unlisted/Other Assets <= 24 months (Slab rate)"
            return {
                "asset_type": asset_type,
                "holding_months": holding_months,
                "gain_type": "STCG",
                "capital_gain": gain,
                "tax_rate": "Applicable Income Tax Slab Rate"
            }

    raw_tax = taxable_gain * tax_rate
    cess = raw_tax * 0.04
    total_tax = raw_tax + cess

    return {
        "asset_type": asset_type,
        "holding_months": holding_months,
        "gain_type": "LTCG" if is_long_term else "STCG",
        "buy_price": buy_price,
        "sell_price": sell_price,
        "gross_capital_gain": gain,
        "exemption_applied": exemption,
        "taxable_capital_gain": taxable_gain,
        "base_tax_rate": f"{tax_rate*100:.1f}%",
        "tax_amount": raw_tax,
        "cess_4pct": cess,
        "total_tax_payable": round(total_tax, 2),
        "rule_reference": rule_ref
    }
