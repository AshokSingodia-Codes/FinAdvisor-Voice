# The Ultimate Finance & CA Knowledge Base

## Chapter 1: Personal Finance and Wealth Management Basics

# Chapter 1 – Personal Finance and Wealth Management Basics  

*Prepared for Chartered Accountant (CA) candidates – Ultimate Finance Textbook*  

---  

## 1.1 What Is Personal Finance?  

> **Personal Finance** – *the systematic planning, organizing, directing and controlling of an individual’s or household’s monetary resources to achieve short‑term and long‑term financial objectives.*  

Personal finance covers **budgeting, saving, investing, risk management, tax planning, retirement planning, and estate planning**.  

---

## 1.2 The Wealth‑Management Process  

| Step | Description | CA‑Level Focus |
|------|-------------|----------------|
| **1. Goal‑Setting** | Identify measurable, time‑bound financial goals (e.g., “Buy a house in 5 years”). | Formulating realistic assumptions for cash‑flow forecasts. |
| **2. Data Gathering** | Collect income statements, balance sheets, tax returns, insurance policies, and legal documents. | Preparing a **Personal Financial Statement** (PFS). |
| **3. Analysis & Diagnosis** | Perform ratio analysis, cash‑flow analysis, and risk‑capacity assessment. | Using **Net Worth**, **Liquidity Ratios**, **Debt‑Service Coverage Ratio (DSCR)**. |
| **4. Planning & Recommendation** | Develop a comprehensive financial plan (budget, investment, insurance, tax, retirement, estate). | Drafting a **Financial Planning Report** with quantitative justifications. |
| **5. Implementation** | Execute the plan – open accounts, purchase assets, adjust insurance, set up trusts. | Recording journal entries for each transaction. |
| **6. Monitoring & Review** | Periodic performance measurement, re‑balancing, and goal‑re‑assessment. | Conducting **Variance Analysis** and **Performance Attribution**. |

---

## 1.3 Fundamentals of Budgeting  

### 1.3.1 The Zero‑Based Budget  

\[
\text{Total Income} - \text{Total Expenditures} = 0
\]

Every rupee (or dollar) is assigned a purpose.  

**Example (FY 2025‑26):**  

| Category | Monthly Amount (₹) |
|----------|-------------------|
| Salary (net) | 80,000 |
| Fixed Expenses (rent, utilities) | 30,000 |
| Variable Expenses (food, transport) | 20,000 |
| Savings / Investments | 20,000 |
| **Total** | **80,000** |

### 1.3.2 The 50/30/20 Rule  

- **50 %** – Needs (essential living expenses)  
- **30 %** – Wants (discretionary spending)  
- **20 %** – Savings & Debt Repayment  

**CA‑Exam Tip:** Convert the rule into a **budget variance worksheet** and compute the **percentage deviation** from the target allocation.

---

## 1.4 Time Value of Money (TVM)  

### 1.4.1 Key Definitions  

- **Present Value (PV)** – *Current worth of a future cash flow discounted at the appropriate rate.*  
- **Future Value (FV)** – *Value of a current cash flow after earning interest for a given period.*  
- **Discount Rate (r)** – *The required rate of return or cost of capital.*  
- **Annuity** – *A series of equal cash flows occurring at regular intervals.*  

### 1.4.2 Core Formulas  

\[
\boxed{PV = \frac{FV}{(1+r)^n}}
\qquad
\boxed{FV = PV \times (1+r)^n}
\]

For an ordinary annuity (payments at period‑end):  

\[
\boxed{PV_{\text{ann}} = PMT \times \frac{1-(1+r)^{-n}}{r}}
\qquad
\boxed{FV_{\text{ann}} = PMT \times \frac{(1+r)^n-1}{r}}
\]

### 1.4.3 Numerical Example  

**Problem:** You plan to invest ₹1,00,000 today in a mutual fund that promises an annual return of 12 % compounded annually. What will be the amount after 8 years?  

**Solution:**  

\[
FV = 1,00,000 \times (1+0.12)^8 = 1,00,000 \times 2.518 = \mathbf{₹2,51,800}
\]

**CA‑Exam Variation:** Compute the **internal rate of return (IRR)** for a cash‑flow series: –₹1,00,000 (t=0), +₹30,000 (t=1), +₹40,000 (t=2), +₹50,000 (t=3).  

*Step‑by‑step:*  

1. Set NPV = 0:  

   \[
   0 = -1,00,000 + \frac{30,000}{(1+IRR)^1} + \frac{40,000}{(1+IRR)^2} + \frac{50,000}{(1+IRR)^3}
   \]  

2. Use trial‑and‑error or Excel’s **IRR** function.  
3. Approximate IRR ≈ **15.2 %** (verified by iteration).  

---

## 1.5 Savings & Investment Vehicles  

| Vehicle | Risk | Expected Return (₹) | Liquidity | Typical Use |
|---------|------|---------------------|-----------|-------------|
| **Savings Account** | Low | 3–4 % (nominal) | High | Emergency fund |
| **Fixed Deposit (FD)** | Low‑Medium | 6–7 % (annual) | Medium | Short‑term goals |
| **Public Provident Fund (PPF)** | Low | 7–8 % (tax‑free) | 15 yr lock‑in | Long‑term tax‑saving |
| **Equity Mutual Funds** | High | 12–15 % (historical) | Medium‑High | Wealth creation |
| **Direct Equity** | Very High | 15–20 %+ | Low‑Medium | Aggressive growth |
| **Real Estate** | Medium‑High | 8–10 % (incl. appreciation) | Low | Asset diversification |
| **National Pension System (NPS)** | Low‑Medium | 8–9 % (mixed) | Low (until retirement) | Retirement corpus |

### 1.5.1 Asset Allocation & the Efficient Frontier  

The **Mean‑Variance Optimization** problem:  

\[
\min_{\mathbf{w}} \ \mathbf{w}^\top \Sigma \mathbf{w} \quad \text{s.t.} \quad \mathbf{w}^\top \mathbf{1}=1,\ \mathbf{w}^\top \mu = \mu_p
\]

- \(\mathbf{w}\) = vector of portfolio weights  
- \(\Sigma\) = covariance matrix of asset returns  
- \(\mu\) = vector of expected returns  

**CA‑Study Note:** In the exam, you may be given a 2‑asset case (e.g., equities and bonds) and asked to compute the **optimal weight** for a target portfolio return.

**Example:**  

- Expected return on equities (\(E_R^E\)) = 14 %  
- Expected return on bonds (\(E_R^B\)) = 6 %  
- Correlation = 0.2, σ_E = 18 %, σ_B = 5 %  

Target portfolio return = 10 %  

Solution (using the formula for two‑asset allocation):  

\[
w_E = \frac{(\mu_p - \mu_B)\sigma_B^2 - (\mu_E - \mu_B)\sigma_{EB}}{(\mu_E - \mu_B)^2\sigma_B^2 + (\mu_E - \mu_B)^2\sigma_E^2 - 2(\mu_E - \mu_B)(\mu_B - \mu_p)\sigma_{EB}}
\]

Plugging numbers yields **\(w_E \approx 0.55\)** (55 % equities, 45 % bonds).  

---

## 1.6 Risk Management & Insurance  

### 1.6.1 Key Definitions  

- **Risk Capacity** – *Maximum amount of risk an individual can financially bear.*  
- **Risk Appetite** – *The amount of risk an individual is willing to accept.*  
- **Deductible** – *The out‑of‑pocket amount the insured pays before the insurer settles a claim.*  

### 1.6.2 Types of Personal Insurance  

| Type | Coverage | Typical Policy Term | Example Premium Calculation |
|------|----------|---------------------|-----------------------------|
| **Life Insurance** | Death benefit | Whole life / term (10‑30 yr) | Premium = \(\frac{Sum\;Assured \times Mortality\;Rate}{(1+r)^n}\) |
| **Health Insurance** | Hospitalisation, OPD | 1 yr renewable | Premium = Base Rate × Age Factor × Sum Insured Factor |
| **Disability (Accidental) Insurance** | Income replacement | 5‑20 yr | Premium = \(\frac{Annual\;Benefit}{\text{Annuity\;Factor at r}}\) |
| **Property (Home) Insurance** | Fire, natural calamities | 1 yr | Premium = \(\text{Rebuilding Cost} \times \text{Rate per ₹1,000}\) |
| **Motor Insurance** | Liability & own‑damage | 1 yr | Premium = \(\text{IDV} \times \text{Rate} + \text{GST}\) |

### 1.6.3 Insurance Needs Analysis – Step‑by‑Step  

1. **Determine Net Worth** – Assets – Liabilities.  
2. **Identify Potential Losses** (e.g., loss of earning capacity, medical expenses).  
3. **Quantify Required Coverage** using the **Human Life Value (HLV)** method:  

   \[
   HLV = \text{Annual Net Income} \times \left(\frac{1-(1+r)^{-n}}{r}\right)
   \]  

   where *n* = remaining working years.  

4. **Select Policy Type & Sum Assured** that meets or exceeds HLV.  

**Example:**  

- Age 35, net annual income ₹12 lakh, expected retirement at 60 → *n* = 25 years, *r* = 8 %  

\[
HLV = 12,00,000 \times \frac{1-(1+0.08)^{-25}}{0.08} = 12,00,000 \times 10.68 = \mathbf{₹1.28\;crore}
\]  

Thus, a term life cover of at least ₹1.3 crore is advisable.

---

## 1.7 Taxation Basics for Individuals  

| Tax Component | Description | Current Indian Rates (FY 2025‑26) |
|---------------|-------------|-----------------------------------|
| **Income Tax** | Tax on taxable income after deductions (Section 80C, 80D, etc.) | Up to **30 %** for income > ₹15 lakh |
| **Capital Gains Tax** | Tax on profit from sale of assets | Short‑term (STCG) – as per slab; Long‑term (LTCG) – 10 % above ₹1 lakh |
| **Dividend Tax** | Tax on dividend income | 10 % (post‑2020) |
| **Wealth Tax** | Abolished (replaced by **Surcharge** on high incomes) | — |
| **Goods & Services Tax (GST)** | Indirect tax on consumption | 5‑28 % depending on goods/services |

### 1.7.1 Tax‑Saving Instruments (Section 80C)  

| Instrument | Max Deduction | Lock‑in | Typical Return |
|------------|---------------|---------|-----------------|
| **PPF** | ₹1.5 lakh | 15 yr | 7‑8 % (tax‑free) |
| **ELSS Mutual Funds** | ₹1.5 lakh | 3 yr | 12‑15 % (taxable) |
| **National Savings Certificate (NSC)** | ₹1.5 lakh | 5 yr | 6‑7 % |
| **Life Insurance Premium** | ₹1.5 lakh (combined) | Varies | – |

**CA‑Exam Application:** Compute **taxable income** after applying Section 80C, 80D (medical insurance), and HRA exemption.  

**Example:**  

- Gross Salary = ₹12 lakh  
- HRA received = ₹2.4 lakh, rent paid = ₹2.1 lakh, non‑metro city  
- Section 80C investments = ₹1.5 lakh  
- Section 80D premium = ₹25,000  

**HRA exemption** (minimum of three):  

1. Actual HRA received = ₹2.4 lakh  
2. Rent paid – 10 % of salary = 2.1 lakh – 1.2 lakh = ₹0.9 lakh  
3. 40 % of salary (non‑metro) = 0.4 × 12 lakh = ₹4.8 

---

## Chapter 2: The Time Value of Money and Advanced Annuities

# Chapter 2  
## **The Time Value of Money and Advanced Annuities**  

*Prepared for Chartered Accountant (CA) examinations – a definitive study guide*  

---  

> **“A rupee today is worth more than a rupee tomorrow.”** – This simple statement underpins every calculation in finance. In this chapter we formalise the concept, develop the mathematics, and apply it to a wide variety of **annuity** structures that appear in CA‑level problems.  

---  

## Table of Contents  

| # | Section | Topics Covered |
|---|---------|----------------|
| 2.1 | **Fundamentals of the Time Value of Money (TVM)** | Present value, future value, discounting, compounding, rates |
| 2.2 | **Interest‑Rate Conventions** | Nominal vs. effective, convertible frequencies, continuous compounding |
| 2.3 | **Single‑Cash‑Flow Valuation** | Formulas, cash‑flow diagrams, real‑world examples |
| 2.4 | **Ordinary Annuities (Annuity‑Immediate)** | PV, FV, annuity factor tables, example |
| 2.5 | **Annuities‑Due** | Shift‑operator technique, PV/FV derivations |
| 2.6 | **Perpetuities & Growing Perpetuities** | Gordon growth model, valuation under inflation |
| 2.7 | **Advanced Annuities** | Varying payments, changing interest rates, deferred annuities, annuity certain, annuity with payment in arrears |
| 2.8 | **Loan Amortisation & Bond Pricing** | Schedule construction, yield‑to‑maturity, duration |
| 2.9 | **Net Present Value (NPV) & Internal Rate of Return (IRR)** | Decision rules, multi‑period cash‑flow analysis |
| 2.10 | **Step‑by‑Step CA‑Level Problem Solving** | Three full‑length worked examples |
| 2.11 | **Summary Checklist** | Quick‑reference formulas |
| 2.12 | **Practice Questions & Answers** | 10 MCQs, 5 short‑answer, 2 extended problems |

---  

## 2.1 Fundamentals of the Time Value of Money (TVM)

### 2.1.1 **Definition – Time Value of Money**  
> **Time Value of Money (TVM)** – *The principle that a sum of money available today is worth more than the same sum in the future because of its potential earning capacity.*  

The two core operations are:

| Operation | Symbol | Meaning |
|-----------|--------|---------|
| **Compounding** | \(FV = PV\,(1+i)^n\) | Growing a present amount \(PV\) to a future amount \(FV\) over \(n\) periods at interest rate \(i\). |
| **Discounting** | \(PV = \dfrac{FV}{(1+i)^n}\) | Bringing a future amount back to its present value. |

> **Key Insight:** The **discount factor** \(\dfrac{1}{(1+i)^n}\) is the present‑value weight applied to a cash flow occurring at the end of period \(n\).

### 2.1.2 Cash‑Flow Diagram  

```
Time → 0      1      2      …      n
       |------|------|------|------|
       PV     CF1    CF2          CFn
```

- **\(t=0\)** – Present (cash‑flow occurs today).  
- **\(t=n\)** – Future (cash‑flow occurs at the end of period \(n\)).  

---  

## 2.2 Interest‑Rate Conventions  

### 2.2.1 **Nominal Rate (\(i^{(m)}\))**  
> **Nominal Rate** – *The quoted annual interest rate compounded \(m\) times per year.*  

Effective periodic rate:  

\[
i = \frac{i^{(m)}}{m}
\]

### 2.2.2 **Effective Annual Rate (EAR)**  

\[
\boxed{(1+i_{\text{eff}})=\left(1+\frac{i^{(m)}}{m}\right)^{m}}
\]

> **Example:** A nominal 12 % p.a. compounded quarterly (\(m=4\)).  

\[
i_{\text{eff}} = \left(1+\frac{0.12}{4}\right)^{4}-1 = (1.03)^{4}-1 = 0.1255 \; \text{or } 12.55\%
\]

### 2.2.3 **Continuous Compounding**  

\[
\boxed{FV = PV\,e^{\delta t}} \qquad \boxed{PV = FV\,e^{-\delta t}}
\]

where \(\delta\) is the **force of interest** (continuous rate).  

Relationship to nominal rate:  

\[
\delta = \ln(1+i_{\text{eff}})
\]

---  

## 2.3 Single‑Cash‑Flow Valuation  

### 2.3.1 Future Value (FV) of a Single Sum  

\[
FV = PV\,(1+i)^n
\]

**Numerical Example** – Deposit ₹100,000 at 9 % p.a. compounded annually for 5 years.  

\[
FV = 100{,}000\,(1+0.09)^5 = 100{,}000\,(1.53862) = \mathbf{₹153,862}
\]

### 2.3.2 Present Value (PV) of a Future Sum  

\[
PV = \frac{FV}{(1+i)^n}
\]

**Example** – What is the present value of ₹250,000 due in 8 years at 11 % p.a.?  

\[
PV = \frac{250{,}000}{(1.11)^8}= \frac{250{,}000}{2.331}= \mathbf{₹107,260}
\]

---  

## 2.4 Ordinary Annuities (Annuity‑Immediate)

### 2.4.1 **Definition – Ordinary Annuity**  
> **Ordinary Annuity (Annuity‑Immediate)** – *A series of equal cash flows occurring at the **end** of each period for \(n\) periods.*  

### 2.4.2 Present‑Value Factor  

\[
\boxed{a_{\overline{n}|i}= \frac{1-(1+i)^{-n}}{i}}
\]

### 2.4.3 Future‑Value Factor  

\[
\boxed{s_{\overline{n}|i}= \frac{(1+i)^{n}-1}{i}}
\]

### 2.4.4 Example – Salary Advance  

A company offers a **salary‑advance** of ₹50,000 payable in 12 equal monthly installments at 10 % p.a. (effective monthly \(i=0.10/12=0.008333\)).  

- **PV of the annuity** (what the employee actually receives today):  

\[
a_{\overline{12}|0.008333}= \frac{1-(1+0.008333)^{-12}}{0.008333}=11.255
\]  

\[
PV = 50{,}000 \times \frac{1}{12}\times a_{\overline{12}|0.008333}= 50{,}000 \times 0.08333 \times 11.255 = \mathbf{₹46,880}
\]

- **FV at the end of 12 months** (total amount paid back):  

\[
s_{\overline{12}|0.008333}= \frac{(1+0.008333)^{12}-1}{0.008333}=12.682
\]  

\[
FV = 50{,}000 \times 0.08333 \times 12.682 = \mathbf{₹52,850}
\]

> **Interpretation:** The employee receives ₹46,880 today but repays ₹52,850 over a year, reflecting the cost of financing.

---  

## 2.5 Annuities‑Due  

### 2.5.1 **Definition – Annuity‑Due**  
> **Annuity‑Due** – *A series of equal cash flows occurring at the **beginning** of each period.*  

### 2.5.2 Relationship to Ordinary Annuity  

\[
a_{\overline{n}|i}^{\text{due}} = (1+i)\,a_{\overline{n}|i}
\qquad
s_{\overline{n}|i}^{\text{due}} = (1+i)\,s_{\overline{n}|i}
\]

### 2.5.3 Example – Lease Payments  

A firm leases equipment with **₹30,000** payable at the start of each quarter for 5 quarters. Quarterly rate \(i=6\%/4=1.5\%\).  

\[
a_{\overline{5}|0.015}^{\text{due}} = (1+0.015)\times\frac{1-(1.015)^{-5}}{0.015}=1.015\times4.713=4.784
\]  

\[
PV = 30{,}000 \times 4.784 = \mathbf{₹143,520}
\]

---  

## 2.6 Perpetuities & Growing Perpetuities  

### 2.6.1 **Definition – Perpetuity**  
> **Perpetuity** – *An infinite series of equal cash flows occurring at regular intervals.*  

\[
\boxed{PV_{\text{perp}} = \frac{C}{i}}
\]

where \(C\) = constant cash flow per period.

### 2.6.2 **Definition – Growing Perpetuity**  
> **Growing Perpetuity** – *An infinite series of cash flows that grow at a constant rate \(g\) each period.*  

\[
\boxed{PV_{\text{gperp}} = \frac{C}{i-g}}, \qquad i>g
\]

### 2.6.3 Example – Preferred Stock  

A preferred share pays ₹5 annually, expected to grow at 2 % forever. Required return \(i=8\%\).  

\[
PV = \frac{5}{0.08-0.02}= \frac{5}{0.06}= \mathbf{₹83.33}
\]

---  

## 2.7 Advanced Annuities  

### 2.7.1 Varying‑Payment Annuities  

When payments follow a known arithmetic or geometric progression, we decompose the cash flow into a **base annuity** plus a **gradient** component.

#### 2.7.1.1 Arithmetic Gradient  

Cash flow in period \(t\): \(C_t = C_1 + (t-1)g\)  

PV formula:  

\[
PV = C_1 a_{\overline{n}|i} + g\left(\frac{a_{\overline{n}|i} - n(1+i)^{-n}}{i}\right)
\]

> **Derivation** – The gradient term is the present value of a series \(0,\,g,\,2g,\dots,(n-1)g\).

**Example** – A contractor receives ₹10,000 in year 1, increasing by ₹2,000 each subsequent year for 6 years. Discount rate 10 %.  

\[
C_1 = 10{,}000,\; g = 2{,}000,\; n=6,\; i=0.10
\]  

\[
a_{\overline{6}|0.10}=4.3553
\]  

\[
PV = 10{,}000(4.3553) + 2{,}000\left(\frac{4.3553-6(1.10)^{-6}}{0.10}\right)
\]  

\[
PV = 43{,}553 + 2{,}000\left(\frac{4.3553-6/1.7716}{0.10}\right)
\]  

\[
PV = 43{,}553 + 2{,}000\left(\frac{4.3553-3.389}{0.10}\right)=43{,}553+2{,}000(9.663)=\mathbf{₹62,859}
\]

#### 2.7.1.2 Geometric Gradient  

Cash flow in period \(t\): \(C_t = C_1(1+g)^{t-1}\)  

PV formula (when \(i\neq g\)):  

\[
PV = C_1\frac{1-(\frac{1+g}{1+i})^{n}}{i-g}
\]

**Example** – A scholarship pays ₹50,000 in year 1 and grows at 5 % annually for 8 years. Discount rate 9 %.  

\[
C_1=50{,}

---

## Chapter 3: Introduction to Accounting Principles and Bookkeeping

# **Chapter 3 – Introduction to Accounting Principles & Bookkeeping**  
*Ultimate Finance Textbook – CA‑Level Study Guide*  

---

## **Table of Contents**

1. [Learning Objectives](#learning-objectives)  
2. [Fundamental Accounting Concepts & Principles](#fundamental-concepts)  
3. [The Accounting Equation & Double‑Entry System](#equation-double)  
4. [The Accounting Cycle – From Transaction to Financial Statements](#accounting-cycle)  
5. [Journalising Transactions](#journalising)  
6. [Posting to Ledger & Preparing a Trial Balance](#ledger-trial)  
7. [Adjusting, Closing & Post‑Closing Entries](#adjusting-closing)  
8. [Key Book‑Keeping Tools & Software](#tools)  
9. [Internal Controls & Ethical Considerations](#controls)  
10. [Advanced CA‑Level Problem – Step‑by‑Step Solution](#ca-problem)  
11. [Summary Checklist](#summary)  
12. [Practice Questions & Answers](#practice)  

---

<a name="learning-objectives"></a>
## 1. Learning Objectives  

By the end of this chapter you will be able to:

- **Define** the core accounting concepts and differentiate between GAAP and IFRS.  
- **Apply** the accounting equation to a variety of business transactions.  
- **Record** transactions using the double‑entry system, journal entries, and posting to T‑accounts.  
- **Prepare** a trial balance, adjust entries, and produce the basic financial statements (Statement of Financial Position, Profit & Loss Account, Cash Flow Statement).  
- **Explain** the role of bookkeeping software and internal controls in safeguarding assets.  
- **Solve** a comprehensive CA‑level exam problem covering the entire accounting cycle.  

---

<a name="fundamental-concepts"></a>
## 2. Fundamental Accounting Concepts & Principles  

| **Concept / Principle** | **Definition** | **Key Implication** |
|--------------------------|----------------|---------------------|
| **Entity Concept** | **The business is regarded as a separate economic entity from its owners and other entities.** | Personal transactions of owners are **not** recorded in the business books. |
| **Going‑Concern Assumption** | **Assumes that the entity will continue its operations for the foreseeable future.** | Assets are recorded at cost, not liquidation value. |
| **Accrual Basis** | **Revenue and expenses are recognised when earned or incurred, not when cash is received or paid.** | Leads to **accrued revenues**, **accrued expenses**, **deferred revenues**, and **deferred expenses**. |
| **Consistency Principle** | **The same accounting policies must be applied from one period to the next unless a change is justified.** | Enables comparability of financial statements. |
| **Materiality** | **Only items that could influence the economic decisions of users need to be disclosed.** | Small, immaterial items may be aggregated. |
| **Prudence (Conservatism)** | **When in doubt, anticipate no profit but anticipate all losses.** | Leads to lower asset valuations and higher expense recognition. |
| **Matching Principle** | **Expenses are recognised in the same period as the revenues they help generate.** | Basis for depreciation, amortisation, and inventory costing. |
| **Historical Cost Principle** | **Assets are recorded at the purchase price, not at current market value.** | Provides reliability but may understate true value. |
| **Revenue Recognition Principle** | **Revenue is recognised when it is earned and measurable.** | For sales of goods: at point of delivery; for services: as performance occurs. |
| **Full Disclosure** | **All material information must be disclosed in the financial statements and notes.** | Ensures transparency for stakeholders. |

> **Note:** In India, the **Companies Act, 2013** and **Ind AS (Indian Accounting Standards)** are the statutory frameworks, while **GAAP** (Indian GAAP) still applies to certain entities.  

---

<a name="equation-double"></a>
## 3. The Accounting Equation & Double‑Entry System  

### 3.1 The Accounting Equation  

\[
\boxed{\text{Assets} = \text{Liabilities} + \text{Equity}}
\]

- **Assets** – Resources controlled by the entity.  
- **Liabilities** – Present obligations arising from past events.  
- **Equity** – Residual interest of owners (Capital + Retained Earnings).  

### 3.2 Expanded Form  

\[
\text{Assets} = \text{Liabilities} + \text{Share Capital} + \text{Reserves} + \text{Retained Earnings}
\]

### 3.3 Double‑Entry Mechanics  

| **Debit (Dr)** | **Credit (Cr)** |
|----------------|-----------------|
| Increases **Asset** or **Expense** accounts | Increases **Liability**, **Equity**, or **Revenue** accounts |
| Decreases **Liability**, **Equity**, or **Revenue** accounts | Decreases **Asset** or **Expense** accounts |

**Fundamental Rule:** Every transaction must **balance** – total debits = total credits.  

#### Example – Purchase of Machinery on Credit  

- **Transaction:** Buy machinery worth ₹ 150,000, payment deferred 30 days.  

| Account | Dr (₹) | Cr (₹) |
|---------|--------|--------|
| Machinery (Asset) | 150,000 | – |
| Creditors (Liability) | – | 150,000 |

*The equation remains balanced: Assets ↑150,000; Liabilities ↑150,000.*

---

<a name="accounting-cycle"></a>
## 4. The Accounting Cycle – From Transaction to Financial Statements  

| **Step** | **Description** | **Key Output** |
|----------|----------------|----------------|
| 1. **Identify & Analyse Transaction** | Determine the nature, parties, and amounts. | Source documents (invoice, receipt). |
| 2. **Journalise** | Record in the **General Journal** using double‑entry. | Journal entries. |
| 3. **Post to Ledger** | Transfer each journal line to its respective **T‑account**. | Ledger balances. |
| 4. **Prepare Unadjusted Trial Balance** | List all ledger balances to test equality of debits & credits. | Unadjusted trial balance. |
| 5. **Adjusting Entries** | Record accruals, deferrals, depreciation, inventory adjustments. | Adjusted trial balance. |
| 6. **Prepare Financial Statements** | Statement of Financial Position, Profit & Loss, Cash Flow. | Draft financial statements. |
| 7. **Closing Entries** | Transfer temporary accounts (Revenue, Expense) to **Retained Earnings**. | Post‑closing trial balance. |
| 8. **Re‑open for Next Period** | Carry forward permanent balances. | Ready for next accounting cycle. |

---

<a name="journalising"></a>
## 5. Journalising Transactions  

### 5.1 Structure of a Journal Entry  

```
Date      | Account Title                | Dr (₹)   | Cr (₹)   | Narration
----------|------------------------------|----------|----------|------------------------------
DD/MM/YY  | Account A (Debit)            |  xx,xxx  |          | Explanation
          | Account B (Credit)           |          |  xx,xxx | Explanation
```

### 5.2 Common Types of Transactions  

| **Transaction** | **Journal Entry (Illustrative)** |
|-----------------|-----------------------------------|
| **Cash Sale** (₹ 25,000) | Dr Cash ₹ 25,000 <br> Cr Sales Revenue ₹ 25,000 |
| **Credit Purchase** of inventory (₹ 12,000) | Dr Purchases ₹ 12,000 <br> Cr Trade Payables ₹ 12,000 |
| **Payment of Salaries** (₹ 8,500) | Dr Salaries Expense ₹ 8,500 <br> Cr Cash ₹ 8,500 |
| **Depreciation** (Straight‑Line, ₹ 5,000 per year) | Dr Depreciation Expense ₹ 5,000 <br> Cr Accumulated Depreciation ₹ 5,000 |
| **Receipt of Unearned Revenue** (₹ 20,000) | Dr Cash ₹ 20,000 <br> Cr Unearned Revenue (Liability) ₹ 20,000 |
| **Recognition of Earned Revenue** (₹ 20,000) | Dr Unearned Revenue ₹ 20,000 <br> Cr Service Revenue ₹ 20,000 |

### 5.3 Real‑World Example – Small Manufacturing Firm  

**Scenario (Jan 2026):**  

- Purchased raw material on cash: ₹ 45,000.  
- Sold finished goods on credit: ₹ 78,000 (cost of goods sold = ₹ 45,000).  
- Paid electricity bill (cash): ₹ 3,200.  

| Date | Account | Dr (₹) | Cr (₹) | Narration |
|------|---------|--------|--------|-----------|
| 05/01/2026 | Raw Materials Inventory | 45,000 | – | Purchase of raw material (cash) |
|            | Cash | – | 45,000 | Same as above |
| 12/01/2026 | Accounts Receivable | 78,000 | – | Credit sale of finished goods |
|            | Sales Revenue | – | 78,000 | Same as above |
| 12/01/2026 | Cost of Goods Sold | 45,000 | – | Cost of goods sold |
|            | Finished Goods Inventory | – | 45,000 | Transfer cost to COGS |
| 20/01/2026 | Electricity Expense | 3,200 | – | Cash payment for electricity |
|            | Cash | – | 3,200 | Same as above |

---

<a name="ledger-trial"></a>
## 6. Posting to Ledger & Preparing a Trial Balance  

### 6.1 T‑Account Layout  

```
          Account Name
   -----------------------------
   |   Dr   |   Cr   |
   -----------------------------
   |        |         |
   |        |         |
   -----------------------------
   | Balance| Balance |
   -----------------------------
```

#### Example – Cash T‑Account (Jan 2026)

| Date | Details | Dr (₹) | Cr (₹) | Balance (₹) |
|------|---------|--------|--------|-------------|
| 01/01 | Opening Balance | 120,000 | – | 120,000 |
| 05/01 | Raw Materials (cash) | – | 45,000 | 75,000 |
| 20/01 | Electricity (cash) | – | 3,200 | 71,800 |
| 31/01 | Closing Balance | – | – | **71,800** |

### 6.2 Unadjusted Trial Balance  

| **Account** | **Dr (₹)** | **Cr (₹)** |
|-------------|------------|------------|
| Cash | 71,800 | – |
| Accounts Receivable | 78,000 | – |
| Raw Materials Inventory | 45,000 | – |
| Finished Goods Inventory | – | 45,000 |
| Equipment (Cost) | 150,000 | – |
| Accumulated Depreciation – Equip. | – | 5,000 |
| Trade Payables | – | 45,000 |
| Capital | – | 200,000 |
| Sales Revenue | – | 78,000 |
| Cost of Goods Sold | 45,000 | – |
| Electricity Expense | 3,200 | – |
| **Totals** | **392,000** | **392,000** |

*If totals differ, locate posting errors before proceeding.*

---

<a name="adjusting-closing"></a>
## 7. Adjusting, Closing & Post‑Closing Entries  

### 7.1 Types of Adjusting Entries  

| **Adjustment** | **Purpose** | **Typical Journal Entry** |
|----------------|-------------|---------------------------|
| **Accrued Revenue** | Revenue earned but not yet billed. | Dr Accounts Receivable / Cr Revenue |
| **Accrued Expense** | Expense incurred but not yet paid. | Dr Expense / Cr Accrued Liability |
| **Deferred Revenue** | Cash received before earning. | Dr Cash / Cr Unearned Revenue (initial) → Dr Unearned Revenue / Cr Revenue (recognition) |
| **Deferred Expense (Prepaid)** | Payment made before benefit. | Dr Prepaid Expense / Cr Cash (initial) → Dr Expense / Cr Prepaid Expense (allocation) |
| **Depreciation** | Allocation of asset cost over useful life. | Dr Depreciation Expense / Cr Accumulated Depreciation |
| **Inventory Adjustments** | Physical count vs. book value. | Dr/Cr Inventory / Dr/Cr COGS |

#### Example – Depreciation (Straight‑Line)  

- **Asset:** Machinery, Cost = ₹ 150,000  
- **Useful Life:** 5 years  
- **Residual Value:** ₹ 0  

\[
\text{Annual Depreciation} = \frac{\text{Cost} - \text{Residual}}{\text{Useful Life}} = \frac{150,000}{5} = ₹ 30,000
\]

**Journal (Year‑end):**  

```
Dr Depreciation Expense      30,000
   Cr Acc

---

## Chapter 4: Advanced Financial Reporting (IFRS & US GAAP)

# Chapter 4 – Advanced Financial Reporting  
**IFRS & US GAAP**  

*Prepared for Chartered Accountant (CA) candidates – definitive study guide*  

---  

## Table of Contents  

| # | Section | Pages |
|---|---------|-------|
| 4.1 | **Introduction & Conceptual Framework** | 1 |
| 4.2 | **Convergence & Key Differences** | 3 |
| 4.3 | **Revenue Recognition (IFRS 15 / ASC 606)** | 5 |
| 4.4 | **Leases (IFRS 16 / ASC 842)** | 9 |
| 4.5 | **Financial Instruments (IFRS 9 / ASC 320‑825)** | 14 |
| 4.6 | **Consolidation & Business Combinations** (IFRS 10/3 / ASC 810) | 20 |
| 4.7 | **Impairment of Assets** (IFRS 13/IAS 36 / ASC 350‑360) | 27 |
| 4.8 | **Income Taxes (IAS 12 / ASC 740)** | 33 |
| 4.9 | **Equity, Share‑Based Payments & Dilution** (IAS 32/IAS 12 / ASC 718) | 38 |
| 4.10| **Segment & Disclosure Requirements** (IFRS 8 / ASC 280) | 44 |
| 4.11| **Exam‑Style Problems & Step‑by‑Step Solutions** | 49 |
| 4.12| **Summary Checklist for CA Exams** | 58 |
| 4.13| **Further Reading & References** | 60 |

---  

## 4.1 Introduction & Conceptual Framework  

### 4.1.1 Purpose of Advanced Reporting  

Advanced financial reporting equips professionals to:  

1. **Interpret** complex transactions under two globally dominant standards – **International Financial Reporting Standards (IFRS)** and **US Generally Accepted Accounting Principles (US GAAP)**.  
2. **Apply** judgment‑based guidance to achieve faithful representation and comparability.  
3. **Prepare** high‑quality financial statements for multinational entities, IPOs, and M&A transactions.  

### 4.1.2 Conceptual Framework – Core Principles  

| IFRS (IAS 1‑8) | US GAAP (FASB Conceptual Framework) |
|----------------|--------------------------------------|
| **Objective of Financial Reporting** – Provide information useful to existing and potential investors, lenders, and other creditors. | Same objective, but US GAAP emphasises **decision‑usefulness** and **reliability** more explicitly. |
| **Qualitative Characteristics** – *Relevance, Faithful Representation, Comparability, Verifiability, Timeliness, Understandability.* | Identical list, but US GAAP adds **Neutrality** and **Prudence** (as a component of faithful representation). |
| **Elements of Financial Statements** – Assets, Liabilities, Equity, Income, Expenses, Gains, Losses. | Same elements, but US GAAP distinguishes **Comprehensive Income** as a separate element. |
| **Recognition Criteria** – Probability of future economic benefit & reliable measurement. | Similar, but US GAAP includes a **“cost‑benefit”** test for certain disclosures. |

> **Bold Definition** – **Probability**: The likelihood that an inflow or outflow of resources will occur, measured as **greater than 50 %** in practice.  

---  

## 4.2 Convergence & Key Differences  

| Area | IFRS | US GAAP | Practical Impact |
|------|------|---------|-------------------|
| **Principles vs. Rules** | Principled, fewer detailed rules. | Rule‑based, extensive industry‑specific guidance. | IFRS demands more professional judgment; US GAAP offers more “check‑list” compliance. |
| **Revenue Recognition** | Single 5‑step model (IFRS 15). | Same 5‑step model (ASC 606) but with different timing for “transfer of control” tests in certain industries (e.g., software). |
| **Leases** | All leases (except short‑term & low‑value) on balance sheet (right‑of‑use asset & lease liability). | Dual model: finance vs. operating leases; operating leases remain off‑balance‑sheet (though ASC 842 now requires balance‑sheet recognition). |
| **Financial Instruments** | Classification based on **business model** and **cash‑flow characteristics** (IFRS 9). | Classification based on **intent** (held‑to‑maturity, trading, available‑for‑sale). |
| **Impairment** | **Expected Credit Loss (ECL)** model for all financial assets. | **Incurred loss** model for most assets; **CECL** (ASC 326) for loans. |
| **Goodwill** | Tested annually for impairment (no amortisation). | Tested annually for impairment (no amortisation). |
| **Presentation of Comprehensive Income** | One statement or two‑statement approach (IAS 1). | Two‑statement approach mandatory (Statement of Comprehensive Income & Statement of Changes in Equity). |
| **Segment Reporting** | Based on **management‑driven** segments (IFRS 8). | Similar, but US GAAP requires **public‑entity** segment disclosures (ASC 280) and includes **reconciliations** to GAAP totals. |

> **Bold Definition** – **Management‑driven segment**: A component of an entity for which separate financial information is evaluated by the chief operating decision maker (CODM) in allocating resources and assessing performance.  

---  

## 4.3 Revenue Recognition (IFRS 15 / ASC 606)  

### 4.3.1 The 5‑Step Model  

1. **Identify the contract(s) with a customer**  
2. **Identify the performance obligations**  
3. **Determine the transaction price**  
4. **Allocate the transaction price to the performance obligations**  
5. **Recognise revenue when (or as) each performance obligation is satisfied**  

### 4.3.2 Key IFRS 15/ASC 606 Concepts  

| Concept | IFRS 15 | ASC 606 |
|---------|---------|---------|
| **Contract existence** | Must have commercial substance, enforceable rights, and collectability probable. | Same, but US GAAP adds a **“significant financing component”** test for long‑term contracts. |
| **Variable consideration** | Expected value or most likely amount, constrained by risk of over‑statement. | Same, but US GAAP requires a **“constraint”** analysis for each period. |
| **Significant financing component** | Discounted at a market rate if the timing of payments differs materially. | Same, but US GAAP provides a **“incremental borrowing rate”** guidance. |
| **Contract modifications** | Treated as a new contract if the modification adds distinct goods/services. | Same, but US GAAP distinguishes **“prospective”** vs **“cumulative”** approach. |

### 4.3.3 Mathematical Formulas  

- **Present Value of Transaction Price (PV)**  

\[
PV = \sum_{t=1}^{n} \frac{C_t}{(1+r)^t}
\]

where:  

* \(C_t\) = cash flow at time \(t\)  
* \(r\) = discount rate (incremental borrowing rate or market rate)  

- **Allocation of Transaction Price (A\_i)**  

\[
A_i = \frac{S_i}{\sum_{j=1}^{m} S_j} \times TP
\]

where:  

* \(S_i\) = stand‑alone selling price of performance obligation \(i\)  
* \(TP\) = total transaction price  

### 4.3.4 Real‑World Example  

**Scenario**: A construction company signs a 3‑year contract to build a plant for **$30 million**. Payments are **$10 million** at the end of each year. The contract includes a **$2 million** penalty if the plant is not operational by the end of year 3. The company’s incremental borrowing rate is **6 %**.  

**Step‑by‑Step**  

| Step | Action | Calculation |
|------|--------|-------------|
| 1 | Identify contract – exists (commercial substance, enforceable). | – |
| 2 | Identify performance obligations – single obligation (construction of plant). | – |
| 3 | Determine transaction price – variable consideration (penalty) is **constrained** because collectability is probable. **TP = $30 m + $2 m = $32 m**. |
| 4 | Allocate – only one obligation, so **A = $32 m**. |
| 5 | Recognise revenue over time (since the entity creates or enhances an asset that the customer controls). Use **input method** (cost incurred). | Compute **PV** of payments: \(\displaystyle PV = \frac{10}{1.06} + \frac{10}{1.06^2} + \frac{10}{1.06^3} = 9.434 + 8.902 + 8.398 = \$26.734\) m. The **unearned revenue** liability at inception is **$32 m – $26.734 m = $5.266 m** (reflects time value of money). |
| 6 | As costs are incurred, recognise revenue proportionally. If by end of Year 1 costs = 30 % of total estimated costs, recognise **30 % × $32 m = $9.6 m** revenue, reduce liability accordingly. | – |

> **Bold Definition** – **Input method**: A method of measuring progress toward completion based on the entity’s efforts or inputs (e.g., costs incurred, labor hours).  

### 4.3.5 Exam‑Style Question  

> **Q4.3.1** – *A software vendor sells a 5‑year licence for $12 million, payable $2 million at signing and $2 million at the end of each subsequent year. The licence includes a $1 million upgrade option that the customer is *reasonably certain* to exercise. The vendor’s incremental borrowing rate is 5 %. Prepare the journal entries for the first two years under IFRS 15.*  

**Solution Outline**  

1. **Identify contract** – exists.  
2. **Performance obligations** – (a) licence (distinct), (b) upgrade option (distinct).  
3. **Transaction price** – $12 m + $1 m = $13 m.  
4. **Allocate** – use stand‑alone selling prices (assume licence $12 m, upgrade $1 m). Allocation: licence 92.31 % ($12 m), upgrade 7.69 % ($1 m).  
5. **Present value** of payments (discount at 5 %):  

\[
PV = \frac{2}{1.05} + \frac{2}{1.05^2} + \frac{2}{1.05^3} + \frac{2}{1.05^4} + \frac{2}{1.05^5} = 1.905 + 1.815 + 1.729 + 1.647 + 1.569 = \$8.665\text{ m}
\]

6. **Initial journal (Signing)**  

| Account | Dr | Cr |
|---------|----|----|
| Cash | $2 m | |
| Contract liability – licence (92.31 % of PV) | | $8.000 m |
| Contract liability – upgrade (7.69 % of PV) | | $0.665 m |
| **Total** | $2 m | $8.665 m |

7. **Revenue recognition** – Assume straight‑line over 5 years for licence (no significant costs). Annual revenue = $12 m / 5 = $2.4 m. Allocate proportionally to liability:  

| Year | Dr (Liability) | Cr (Revenue) |
|------|----------------|--------------|
| 1 (after cash receipt) | $1.733 m | $2.4 m |
| 2 | $1.733 m | $2.4 m |

*(Liability reduction = PV portion allocated to licence × (1/5)).*  

---  

## 4.4 Leases (IFRS 16 / ASC 842)  

### 4.4.1 Core Principles  

| IFRS 16 | ASC 842 |
|---------|----------|
| **Single‑model** – All leases (except short‑term & low‑value) recognised on balance sheet. | **Dual‑model** – Finance leases (on‑balance) vs. operating leases (off‑balance, but with right‑of‑use asset & lease liability under the “new” model). |
| **Lessee accounting** – Right‑of‑use (ROU) asset measured at **initial liability + initial direct costs**. | Same for finance leases; operating leases recognise ROU asset and liability but expense lease cost on a straight‑line basis. |
|

---

## Chapter 5: Corporate Finance: Cost of Capital, Capital Structure, and Dividend Policy

# **Chapter 5 – Corporate Finance: Cost of Capital, Capital Structure, and Dividend Policy**  

*Prepared for Chartered Accountant (CA) examinations – ultimate study guide*  

---  

## Table of Contents  

| # | Section | Topics |
|---|---------|--------|
| 5.1 | **Cost of Capital** | Definition, Cost of Debt, Cost of Equity (CAPM, DDM, Earnings‑Based), Weighted‑Average Cost of Capital (WACC), Adjustments, CA‑style problem |
| 5.2 | **Capital Structure** | Definition, Modigliani‑Miller propositions, Trade‑off & Pecking‑order theories, Leverage ratios, Tax shield, Bankruptcy cost, CA‑style optimisation problem |
| 5.3 | **Dividend Policy** | Definition, Types of dividends, Theories (MM, Bird‑in‑the‑Hand, Tax Preference, Agency, Signalling), Payout & Retention ratios, Sustainable growth rate, CA‑style dividend‑policy problem |
| 5.4 | **Integrated Decision‑Making** | Interaction of the three pillars, Real‑world case study (Apple Inc.) |
| 5.5 | **Summary & Quick‑Reference Sheet** |
| 5.6 | **Practice Questions & Answers** |

---  

## 5.1 Cost of Capital  

### 5.1.1 **Definition**  

> **Cost of Capital** – the minimum rate of return that a firm must earn on its invested capital to satisfy its providers of capital (debt‑holders, equity‑holders, and preferred‑stockholders) and to preserve the firm’s market value.  

It is the **discount rate** used in valuation, capital‑budgeting, and performance‑measurement exercises.  

---

### 5.1.2 Components of Cost of Capital  

| Source of Capital | Symbol | Typical Cost Formula |
|-------------------|--------|----------------------|
| **Debt (after‑tax)** | \(k_d\) | \(k_d = r_d (1 - T)\) |
| **Preferred Stock** | \(k_{ps}\) | \(k_{ps}= \dfrac{D_{ps}}{P_{ps}}\) |
| **Common Equity** | \(k_e\) | See Section 5.1.4 |
| **Weighted‑Average Cost of Capital** | \(WACC\) | \(WACC = \dfrac{D}{V}k_d + \dfrac{P}{V}k_{ps} + \dfrac{E}{V}k_e\) |

where  

- \(D, P, E\) = market values of debt, preferred stock, and equity, respectively  
- \(V = D+P+E\) = total market value of the firm  
- \(T\) = corporate tax rate  

---

### 5.1.3 Cost of Debt  

**Formula**  

\[
k_d = r_d (1 - T)
\]

- \(r_d\) = **pre‑tax yield** on existing or new debt (YTM of bonds or interest rate on loans).  
- \(T\) = marginal corporate tax rate (interest is tax‑deductible).  

**Example 5.1 – After‑Tax Cost of Debt**  

A firm has a 10‑year corporate bond with a **coupon rate** of 7 % paid semi‑annually, a **current market price** of 950 % of par, and a **tax rate** of 30 %.  

1. Compute the bond’s **yield‑to‑maturity (YTM)** \(r_d\).  
   - Using a financial calculator or Excel `=YIELD(settlement, maturity, rate, pr, redemption, frequency, [basis])` → \(r_d \approx 8.00\%\) (effective annual).  
2. After‑tax cost:  

\[
k_d = 0.08 \times (1-0.30) = 0.056 = \boxed{5.6\%}
\]

---

### 5.1.4 Cost of Common Equity  

#### (a) Capital Asset Pricing Model (CAPM)  

\[
\boxed{k_e = r_f + \beta \bigl( r_m - r_f \bigr)}
\]

- \(r_f\) = risk‑free rate (e.g., 10‑year Treasury yield).  
- \(\beta\) = equity beta (measure of systematic risk).  
- \(r_m\) = expected market return.  

**Example 5.2 – CAPM**  

- \(r_f = 3.5\%\)  
- \(\beta = 1.25\)  
- Expected market return \(r_m = 10\%\)  

\[
k_e = 0.035 + 1.25(0.10-0.035) = 0.035 + 1.25(0.065) = 0.035 + 0.08125 = \boxed{11.125\%}
\]

#### (b) Dividend Discount Model (DDM) – Gordon Growth  

\[
\boxed{k_e = \frac{D_1}{P_0} + g}
\]

- \(D_1\) = dividend expected next period.  
- \(P_0\) = current share price.  
- \(g\) = sustainable dividend growth rate (usually \(ROE \times b\)).  

**Example 5.3 – DDM**  

- Current price \(P_0 = \$45\)  
- Expected dividend next year \(D_1 = \$2.70\)  
- Expected growth \(g = 5\%\)  

\[
k_e = \frac{2.70}{45} + 0.05 = 0.06 + 0.05 = \boxed{11.0\%}
\]

#### (c) Earnings‑Based (Residual Income) Approach  

\[
\boxed{k_e = \frac{E_1}{P_0} + g_E}
\]

where \(E_1\) = expected earnings per share, \(g_E\) = earnings growth. This is useful when a firm does **not** pay dividends.

---

### 5.1.5 Weighted‑Average Cost of Capital (WACC)  

\[
\boxed{WACC = \frac{D}{V}k_d + \frac{P}{V}k_{ps} + \frac{E}{V}k_e}
\]

**Example 5.4 – Full WACC Calculation**  

| Item | Market Value (₹ mn) | Cost |
|------|--------------------|------|
| Debt (long‑term) | 400 | \(k_d = 6.0\%\) (after‑tax) |
| Preferred Stock | 100 | \(k_{ps}= 9.0\%\) |
| Common Equity | 500 | \(k_e = 12.0\%\) |
| **Total (V)** | **1,000** | — |

\[
\begin{aligned}
WACC &= \frac{400}{1,000}\times0.06 + \frac{100}{1,000}\times0.09 + \frac{500}{1,000}\times0.12\\
&= 0.024 + 0.009 + 0.060 = \boxed{9.3\%}
\end{aligned}
\]

---

### 5.1.6 Adjustments to the Cost of Capital  

| Adjustment | Reason | Typical Formula |
|------------|--------|-----------------|
| **Flotation Costs** | New securities issuance incurs underwriting, legal, and registration fees. | Adjusted cost \(k^{*}= \frac{k}{1 - f}\) where \(f\) = flotation cost % |
| **Marginal vs. Average Cost** | Decision‑making for a *new* project uses the **marginal** cost of the next unit of capital. | Use the cost of the *cheapest* available source that can be raised. |
| **Project‑Specific Risk** | Projects in a different line of business may have a different beta. | Re‑estimate \(k_e\) using a project‑specific \(\beta\). |
| **Country‑Risk Premium** (for multinational firms) | Additional compensation for sovereign risk. | Add \(CRP\) to the market risk premium in CAPM. |

---

### 5.1.7 **CA‑Level Problem – Compute WACC with Flotation Costs**  

**Problem Statement**  

A manufacturing firm plans to raise ₹ 200 mn through a **new term loan** (interest 9 % p.a.) and **new equity** (expected return 13 %).  

- Tax rate \(T = 35\%\).  
- Flotation cost on debt = 2 % of the amount raised.  
- Flotation cost on equity = 5 % of the amount raised.  

The firm’s current market capital structure (excluding the new issue) is:  

- Debt = ₹ 800 mn (market value)  
- Equity = ₹ 1,200 mn (market value)  

**Required** – Compute the **post‑issue WACC** to be used for evaluating a new project.  

**Step‑by‑Step Solution**  

1. **Determine net proceeds** after flotation:  

   - Debt net = \(200 \times (1-0.02) = ₹ 196\) mn  
   - Equity net = \(200 \times (1-0.05) = ₹ 190\) mn  

2. **Calculate the after‑tax cost of the new debt**  

   \[
   k_{d}^{\text{new}} = 0.09 \times (1-0.35) = 0.0585 = 5.85\%
   \]

3. **Cost of new equity** is given as \(k_{e}^{\text{new}} = 13\%\).  

4. **Compute the new market values** (old + net proceeds):  

   \[
   \begin{aligned}
   D_{\text{total}} &= 800 + 196 = 996\ \text{mn} \\
   E_{\text{total}} &= 1,200 + 190 = 1,390\ \text{mn} \\
   V_{\text{total}} &= 996 + 1,390 = 2,386\ \text{mn}
   \end{aligned}
   \]

5. **Weight of each component**  

   \[
   w_d = \frac{996}{2,386}=0.4176,\qquad 
   w_e = \frac{1,390}{2,386}=0.5824
   \]

6. **WACC**  

   \[
   \begin{aligned}
   WACC &= w_d \times k_{d}^{\text{new}} + w_e \times k_{e}^{\text{new}}\\
   &= 0.4176 \times 0.0585 + 0.5824 \times 0.13\\
   &= 0.0244 + 0.0757 = \boxed{10.01\%}
   \end{aligned}
   \]

> **Take‑away:** Flotation costs raise the effective cost of capital because the firm must raise more gross capital to obtain the required net proceeds.  

---  

## 5.2 Capital Structure  

### 5.2.1 **Definition**  

> **Capital Structure** – the mix of long‑term sources of financing a firm uses, primarily **debt**, **preferred equity**, and **common equity**.  

The choice of mix influences the firm’s **risk profile**, **cost of capital**, and ultimately its **valuation**.  

---

### 5.2.2 Theoretical Foundations  

| Theory | Core Proposition | Implication for Optimal Structure |


---

## Chapter 6: Advanced Capital Budgeting and Risk Analysis

# Chapter 6 – Advanced Capital Budgeting and Risk Analysis  

*Prepared for Chartered Accountant (CA) examinations – Ultimate Finance Textbook*  

---  

## 6.1  Introduction  

Capital budgeting is the systematic process of evaluating long‑term investment projects. While the basic tools (NPV, IRR, Payback) are covered in introductory chapters, real‑world decisions require **advanced techniques** that incorporate **uncertainty, flexibility, and risk‑adjusted valuation**.  

This chapter equips you with:

1. **Quantitative methods** – real‑options valuation, Monte‑Carlo simulation, decision‑tree analysis.  
2. **Risk‑adjusted discounting** – CAPM, Adjusted Present Value (APV), and the Weighted Average Cost of Capital (WACC) with beta adjustments.  
3. **Performance metrics** – Economic Value Added (EVA), Risk‑Adjusted Return on Capital (RAROC).  
4. **CA‑style problem‑solving** – step‑by‑step solutions to exam‑type questions.  

> **Learning Objective:** By the end of this chapter you will be able to **model, value, and recommend** complex investment projects under uncertainty, and **justify** your recommendation using CA‑level analytical rigor.  

---  

## 6.2  Core Concepts and Definitions  

| Term | Definition |
|------|------------|
| **Net Present Value (NPV)** | The present value of all cash inflows **minus** the present value of all cash outflows, discounted at the project’s **risk‑adjusted cost of capital**. |
| **Internal Rate of Return (IRR)** | The discount rate that makes the NPV of a project **exactly zero**. |
| **Modified Internal Rate of Return (MIRR)** | An IRR variant that assumes **reinvestment at the firm’s cost of capital** (rather than the IRR itself) and financing at the **finance rate**. |
| **Real Options** | The **right, but not the obligation**, to make strategic decisions (e.g., expand, abandon, defer) that add value to a project, analogous to financial options. |
| **Monte‑Carlo Simulation** | A computational technique that generates a large number of random scenarios for uncertain variables to produce a **probability distribution** of project outcomes. |
| **Decision Tree** | A graphical representation of **sequential decisions and chance events**, used to compute the **expected monetary value (EMV)** of each strategy. |
| **Weighted Average Cost of Capital (WACC)** | The **average** after‑tax cost of all sources of capital (debt, equity, preferred) weighted by their market values. |
| **Beta (β)** | A measure of a security’s **systematic risk** relative to the market; used in the **CAPM** to estimate the cost of equity. |
| **Adjusted Present Value (APV)** | The NPV of a project **plus** the present value of financing side‑effects (e.g., tax shields). |
| **Economic Value Added (EVA)** | **NOPAT – (Invested Capital × WACC)**; a measure of value creation after accounting for the cost of capital. |
| **Risk‑Adjusted Return on Capital (RAROC)** | **(Risk‑adjusted profit) / (Economic capital)**; used for performance measurement and capital allocation. |
| **Sensitivity Analysis** | A “what‑if” technique that varies **one input** at a time to assess its impact on NPV or IRR. |
| **Scenario Analysis** | Evaluates **multiple coherent sets** of assumptions (e.g., best‑case, base‑case, worst‑case) simultaneously. |
| **Probability‑Weighted Expected NPV** | The sum of **NPV × probability** for each scenario, providing a single risk‑adjusted figure. |

---  

## 6.3  Risk‑Adjusted Discount Rates  

### 6.3.1  Cost of Equity via CAPM  

\[
\boxed{r_e = r_f + \beta \bigl( r_m - r_f \bigr)}
\]

* \(r_f\) – risk‑free rate (e.g., 10‑year government bond).  
* \(\beta\) – equity beta (levered).  
* \(r_m\) – expected market return.  

**Example 6.1 – Calculating Cost of Equity**  

| Input | Value |
|-------|-------|
| Risk‑free rate, \(r_f\) | 4.5 % |
| Market risk premium, \(r_m - r_f\) | 6.0 % |
| Levered beta, \(\beta\) | 1.30 |

\[
r_e = 4.5\% + 1.30 \times 6.0\% = 4.5\% + 7.8\% = 12.3\%
\]

### 6.3.2  After‑Tax Cost of Debt  

\[
\boxed{r_d^{\text{after}} = r_d \times (1 - T_c)}
\]

* \(r_d\) – nominal cost of debt.  
* \(T_c\) – corporate tax rate.  

**Example 6.2 – After‑Tax Debt Cost**  

* Nominal debt rate = 8 %  
* Tax rate = 30 %  

\[
r_d^{\text{after}} = 8\% \times (1 - 0.30) = 5.6\%
\]

### 6.3.3  Computing WACC  

\[
\boxed{\text{WACC}= \frac{E}{V} r_e + \frac{D}{V} r_d^{\text{after}} + \frac{P}{V} r_p}
\]

* \(E, D, P\) – market values of equity, debt, preferred equity.  
* \(V = E + D + P\).  

**Example 6.3 – WACC Calculation**  

| Component | Market Value (₹ mn) | Cost |
|-----------|-------------------|------|
| Equity (E) | 120 | 12.3 % |
| Debt (D)   | 80  | 5.6 % |
| Preferred (P) | 0 | – |

\[
\begin{aligned}
\frac{E}{V} &= \frac{120}{200}=0.60\\
\frac{D}{V} &= \frac{80}{200}=0.40\\[4pt]
\text{WACC} &= 0.60 \times 12.3\% + 0.40 \times 5.6\% = 7.38\% + 2.24\% = 9.62\%
\end{aligned}
\]

> **CA Tip:** When the project’s risk profile differs from the firm’s overall risk, **adjust beta** (or use a project‑specific discount rate) rather than applying the corporate WACC blindly.

---  

## 6.4  Advanced NPV Techniques  

### 6.4.1  Adjusted Present Value (APV)  

\[
\boxed{\text{APV}= \text{NPV}_{\text{unlevered}} + \text{PV of financing effects}}
\]

* **Unlevered NPV** – discount cash flows at the **cost of equity** (as if the project were all‑equity financed).  
* **Financing effects** – typically the **tax shield** from debt, valued at the **cost of debt** (or risk‑free rate).  

**Step‑by‑Step APV Example**  

A firm evaluates a ₹ 150 mn project with the following cash flows (₹ mn):  

| Year | Operating CF | Debt Interest (₹ mn) |
|------|--------------|----------------------|
| 0    | –150         | –                    |
| 1    | 45           | 6                    |
| 2    | 55           | 6                    |
| 3    | 65           | 6                    |
| 4    | 70           | –                    |

Assumptions:  

* Cost of equity (unlevered) = 13 %  
* Debt interest rate = 8 % (tax‑deductible)  
* Tax rate = 30 %  

**1. Unlevered cash flows** (ignore interest, add back after‑tax interest shield later):  

\[
\text{CF}_{\text{unlevered}} = \text{Operating CF} + \text{Interest} \times (1 - T_c)
\]

| Year | Operating CF | Interest | Tax shield | Unlevered CF |
|------|--------------|----------|------------|--------------|
| 1    | 45 | 6 | 6×0.30 = 1.8 | 45 + 1.8 = 46.8 |
| 2    | 55 | 6 | 1.8 | 56.8 |
| 3    | 65 | 6 | 1.8 | 66.8 |
| 4    | 70 | 0 | 0 | 70 |

**2. Discount unlevered CF at 13 %**  

\[
\text{NPV}_{\text{unlevered}} = -150 + \sum_{t=1}^{4} \frac{\text{CF}_{t}}{(1+0.13)^t}
\]

| Year | CF | Discount factor (13 %) | PV |
|------|----|------------------------|----|
| 1 | 46.8 | 0.88496 | 41.38 |
| 2 | 56.8 | 0.78313 | 44.48 |
| 3 | 66.8 | 0.69246 | 46.28 |
| 4 | 70   | 0.61391 | 42.97 |

\[
\text{NPV}_{\text{unlevered}} = -150 + (41.38+44.48+46.28+42.97) = -150 + 175.11 = **₹ 25.11 mn**
\]

**3. PV of tax shield** (assume perpetual debt of ₹ 80 mn at 8 % interest):  

\[
\text{Annual tax shield}= \text{Interest} \times T_c = 80 \times 8\% \times 30\% = 1.92 \text{ mn}
\]

Discount at **cost of debt** (8 %):  

\[
\text{PV}_{\text{shield}} = \frac{1.92}{0.08}= 24.0 \text{ mn}
\]

**4. APV**  

\[
\boxed{\text{APV}= 25.11 + 24.0 = \mathbf{₹ 49.11\;mn}}
\]

Since APV > 0, the project is **value‑adding** even after accounting for financing benefits.

---  

### 6.4.2  Real Options Valuation  

Real options are valued using **option‑pricing techniques** (Black‑Scholes, binomial trees) or **decision‑tree analysis**. The most common approach for CA exams is the **binomial lattice** because it accommodates multiple periods and changing cash flows.

#### 6.4.2.1  Binomial Real‑Option Model  

1. **Define the underlying asset** – the present value of expected cash flows if the option is exercised.  
2. **Determine up (\(u\)) and down (\(d\)) factors**:  

\[
u = e^{\sigma \sqrt{\Delta t}}, \quad d = \frac{1}{u}
\]

* \(\sigma\) – volatility of the project's cash flows (often estimated from comparable firms).  
* \(\Delta t\) – length of each period (years).  

3. **Risk‑neutral probability (\(p\))**:  

\[
p = \frac{e^{r \Delta t} - d}{u - d}
\]

* \(r\) – risk‑free rate.  

4. **Construct the lattice** for the project’s value at each node.  
5. **Apply the option payoff** at each node (e.g., for a **call to expand**, payoff = max\((V_{\text{expanded}} - K, 0)\)).  
6. **Discount back** using the risk‑free rate and the risk‑neutral probabilities.

#### 6.4.2.2  Example – Option to Expand  

A mining company has a **base project** with NPV\(_0\) = ₹ 30 mn. After 2 years, management may **expand** by investing an additional ₹ 15 mn, which would increase the project's cash flow by **₹ 12 mn per year forever**.  

Assumptions:  

* Risk‑free rate \(r = 5\%\) (continuous).  
* Volatility of the project's value \(\sigma = 30\%\).  
* One‑year periods (\(\Delta t = 1\)).  

**Step 1 – Compute up/down factors**  

\[
u = e^{0.30 \sqrt{1}} = e^{0.30}=1.3499,\quad d = \frac{1}{u}=0.7408
\]

**Step 2 – Risk‑neutral probability**  

\[
p = \frac{e^{0.05} - d}{u - d

---

## Chapter 7: Equity Valuation Models (DCF, DDM, FCFE/FCFF, Relative Valuation)

# **Chapter 7 – Equity Valuation Models**  
*Discounted Cash Flow (DCF), Dividend Discount Model (DDM), FCFE/FCFF, and Relative Valuation*  

---

## **Learning Objectives**

By the end of this chapter you will be able to:

1. **Define** the core concepts and assumptions underlying each equity valuation model.  
2. **Derive** and **apply** the mathematical formulas for DCF, DDM, FCFE, FCFF, and relative‑valuation multiples.  
3. **Construct** a full valuation worksheet – from forecasting cash flows to computing a terminal value and discounting to present value.  
4. **Perform** sensitivity and scenario analysis to assess valuation risk.  
5. **Select** appropriate comparable companies, adjust for differences, and compute equity value using market‑based multiples.  
6. **Solve** CA‑level exam problems step‑by‑step, showing all intermediate calculations and justifications.  

---

## **1. Discounted Cash Flow (DCF) Valuation**

### 1.1 **Definition**  

> **Discounted Cash Flow (DCF) Valuation** is a **fundamental** method that estimates the intrinsic value of a firm by **discounting** the **expected future cash flows** to the present using an appropriate **cost of capital**.  

The DCF approach rests on the **time‑value of money** principle: a rupee received today is worth more than the same rupee received in the future because it can be invested to earn a return.

### 1.2 Theoretical Framework  

| Component | Description |
|-----------|-------------|
| **Forecast Period** | Typically 5‑10 years, where cash flows are projected explicitly. |
| **Terminal Value (TV)** | Captures the value of cash flows **beyond** the explicit forecast, using a perpetuity or exit‑multiple approach. |
| **Discount Rate** | The **Weighted Average Cost of Capital (WACC)** for FCFF valuations, or **Cost of Equity (Ke)** for FCFE valuations. |
| **Present Value (PV)** | Sum of discounted cash flows + discounted terminal value. |

### 1.3 Key Formulas  

1. **Present Value of Forecast Cash Flows**  

\[
PV_{\text{FCF}} = \sum_{t=1}^{n} \frac{CF_t}{(1+ r)^t}
\]

where  

- \(CF_t\) = cash flow in year *t* (FCFF or FCFE)  
- \(r\) = discount rate (WACC or Ke)  
- \(n\) = last year of explicit forecast  

2. **Perpetuity Growth Terminal Value**  

\[
TV_{\text{Gordon}} = \frac{CF_{n}\,(1+g)}{r - g}
\]

where  

- \(g\) = long‑run sustainable growth rate (usually ≤ g\_{\text{GDP}})  

3. **Enterprise Value (EV)**  

\[
EV = PV_{\text{FCF}} + \frac{TV_{\text{Gordon}}}{(1+r)^n}
\]

4. **Equity Value (E)**  

\[
E = EV - \text{Net Debt} - \text{Minority Interest} + \text{Cash \& Equivalents}
\]

5. **Weighted Average Cost of Capital (WACC)**  

\[
WACC = \frac{E}{V}\,Ke + \frac{D}{V}\,Kd\,(1-T)
\]

where  

- \(E\) = market value of equity, \(D\) = market value of debt, \(V = E + D\)  
- \(Ke\) = cost of equity (CAPM: \(Ke = R_f + \beta (R_m - R_f)\))  
- \(Kd\) = pre‑tax cost of debt, \(T\) = corporate tax rate  

### 1.4 Step‑by‑Step DCF Valuation (CA‑Exam Blueprint)

| Step | Action | Typical Pitfalls |
|------|--------|------------------|
| **1** | **Project Operating Performance** – revenue, margins, CAPEX, working‑capital changes. | Over‑optimistic growth; ignoring cyclicality. |
| **2** | **Compute FCFF** (or FCFE) for each forecast year. | Forgetting to adjust for taxes on EBIT. |
| **3** | **Determine WACC** (or Ke).** | Using book‑value capital structure instead of market values. |
| **4** | **Calculate Terminal Value** – choose growth‑perpetuity or exit‑multiple. | Selecting an unrealistic perpetual growth rate (> g\_{\text{GDP}}). |
| **5** | **Discount** each cash flow and TV back to present. | Mis‑aligning cash‑flow timing (e.g., using end‑of‑year vs. beginning‑of‑year). |
| **6** | **Derive Equity Value** – subtract net debt, add cash. | Ignoring minority interests or preferred equity. |
| **7** | **Sensitivity Analysis** – vary WACC and g to produce a valuation range. | Not documenting assumptions; failing to explain why range is reasonable. |

### 1.5 **Illustrative Example** – *ABC Ltd.*  

Assume the following data (all figures in ₹ crore):

| Year | Revenue | EBIT (15 % of Rev.) | Tax (30 %) | Depreciation | CAPEX | ΔNWC |
|------|---------|--------------------|------------|--------------|-------|------|
| 1 | 1,200 | 180 | 54 | 30 | 40 | 10 |
| 2 | 1,320 | 198 | 59.4 | 33 | 44 | 11 |
| 3 | 1,452 | 218 | 65.4 | 36 | 48 | 12 |
| 4 | 1,597 | 240 | 72 | 40 | 52 | 13 |
| 5 | 1,757 | 263.6 | 79.1 | 44 | 57 | 14 |

**Step 1 – Compute FCFF**  

\[
\text{FCFF}_t = \text{EBIT}_t (1-T) + \text{Dep}_t - \text{CAPEX}_t - \Delta \text{NWC}_t
\]

| Year | EBIT(1‑T) | +Dep | –CAPEX | –ΔNWC | **FCFF** |
|------|-----------|------|--------|-------|----------|
| 1 | 126 | 30 | 40 | 10 | **106** |
| 2 | 138.6 | 33 | 44 | 11 | **116.6** |
| 3 | 152.6 | 36 | 48 | 12 | **128.6** |
| 4 | 168 | 40 | 52 | 13 | **143** |
| 5 | 184.5 | 44 | 57 | 14 | **157.5** |

**Step 2 – Determine WACC**  

- Market‑value equity (E) = ₹ 1,200 cr  
- Market‑value debt (D) = ₹ 300 cr (5 % coupon)  
- \(V = 1,500\) cr  

\[
Ke = 6\% + 1.2 \times (12\% - 6\%) = 13.2\%
\]  

\[
Kd = 5\% \quad (after‑tax) = 5\% \times (1-0.30) = 3.5\%
\]  

\[
WACC = \frac{1,200}{1,500}\times13.2\% + \frac{300}{1,500}\times3.5\% = 10.56\%
\]

**Step 3 – Terminal Value (perpetuity growth)**  

Assume long‑run growth \(g = 3\%\).

\[
TV = \frac{FCFF_5 \times (1+g)}{WACC - g}
     = \frac{157.5 \times 1.03}{0.1056 - 0.03}
     = \frac{162.225}{0.0756}
     = \mathbf{2,147.5\;cr}
\]

**Step 4 – Discount Cash Flows**  

\[
PV = \sum_{t=1}^{5} \frac{FCFF_t}{(1+0.1056)^t}
\]

| Year | Discount Factor \((1+WACC)^t\) | PV of FCFF |
|------|-------------------------------|------------|
| 1 | 1.1056 | 95.94 |
| 2 | 1.2225 | 95.44 |
| 3 | 1.3515 | 95.14 |
| 4 | 1.4940 | 95.71 |
| 5 | 1.6512 | 95.38 |
| **Sum** | — | **477.61** |

**PV of Terminal Value**

\[
PV_{TV}= \frac{2,147.5}{(1+0.1056)^5}= \frac{2,147.5}{1.6512}= \mathbf{1,300.2\;cr}
\]

**Enterprise Value**

\[
EV = 477.61 + 1,300.2 = \mathbf{1,777.8\;cr}
\]

Assume **Net Debt** = Debt – Cash = ₹ 300 cr – ₹ 50 cr = ₹ 250 cr.

\[
\boxed{\text{Equity Value} = EV - \text{Net Debt} = 1,777.8 - 250 = \mathbf{1,527.8\;cr}}
\]

Dividing by the **outstanding shares** (150 cr) gives a **fair price** of **₹ 10.19 per share**.

**Step 5 – Sensitivity Table (WACC ± 1 % ; g ± 0.5 %)**

| WACC \ g | 2.5 % | 3.0 % | 3.5 % |
|----------|------|------|------|
| **9.5 %** | 11.12 | 10.79 | 10.46 |
| **10.5 %**| 10.45 | 10.19 | 9.94 |
| **11.5 %**| 9.84  | 9.60  | 9.36 |

*Interpretation:* The valuation is most sensitive to the discount rate; a 1 % rise in WACC reduces the price by ~₹ 0.75 per share.

### 1.6 **CA‑Level Exam Problem (DCF)**  

**Question:**  
*XYZ Ltd. has the following projected FCFF (₹ million) for the next 4 years: 120, 135, 150, 165. After year 4, cash flows are expected to grow forever at 2 %. The firm’s WACC is 9 %. Net debt is ₹ 200 million, and there are 50 million shares outstanding. Compute the intrinsic share price.*

**Solution – Step‑by‑Step**

1. **Discount FCFF**  

\[
PV = \frac{120}{1.09} + \frac{135}{1.09^2} + \frac{150}{1.09^3} + \frac{165}{1.09^4}
\]  

\[
PV = 110.09 + 113.57 + 

---

## Chapter 8: Fixed Income Securities: Pricing, Duration, Convexity, and Term Structure

# **Chapter 8 – Fixed‑Income Securities: Pricing, Duration, Convexity, and Term Structure**  

*Prepared for Chartered Accountant (CA) examinations – ultimate study guide*  

---  

## 8.1  Introduction  

Fixed‑income securities (primarily **bonds**) dominate global capital markets, providing a predictable stream of cash flows. Understanding how to **price** these instruments, measure their **interest‑rate sensitivity** (duration & convexity), and interpret the **term structure of interest rates** is essential for:

* Valuation of corporate and government debt.  
* Managing interest‑rate risk in portfolios and balance‑sheet items.  
* Solving CA‑level exam questions on bond accounting, fair‑value measurement, and risk management.  

This chapter presents a **complete, step‑by‑step framework** – from cash‑flow fundamentals to advanced term‑structure modelling – with **real‑world numerical examples** and **exam‑style problems**.

---  

## 8.2  Bond Fundamentals  

| **Term** | **Definition** |
|----------|----------------|
| **Face (Par) Value** | **The amount paid to the holder at maturity**, denoted \(F\). Typically \$1,000 for corporate bonds. |
| **Coupon Rate** (\(c\)) | **Annual nominal interest expressed as a percentage of face value**. The periodic coupon payment is \(C = \frac{c}{m}\,F\) where \(m\) = number of coupon periods per year. |
| **Maturity** (\(T\)) | **Time (in years) until the principal is repaid**. |
| **Yield to Maturity (YTM)** (\(y\)) | **The single discount rate that equates the present value of all cash flows to the market price**. |
| **Current Yield** | **Annual coupon payment divided by market price**: \(\displaystyle \text{Current Yield}= \frac{C\cdot m}{P}\). |
| **Accrued Interest** | **Interest earned but not yet paid**: \(\displaystyle AI = C \times \frac{\text{days since last coupon}}{\text{days in coupon period}}\). |
| **Clean Price** | **Market price excluding accrued interest**. |
| **Dirty Price** | **Clean price + accrued interest** (the actual cash outlay). |

### 8.2.1  Cash‑Flow Diagram  

For a **plain‑vanilla coupon bond** with semi‑annual coupons (\(m=2\)):

\[
\begin{array}{c|c}
\text{Period } t & \text{Cash Flow } CF_t \\ \hline
1 & C \\
2 & C \\
\vdots & \vdots \\
n-1 & C \\
n & C+F
\end{array}
\]

where \(n = mT\) total coupon periods.

---  

## 8.3  Bond Pricing  

### 8.3.1  General Pricing Formula  

The **dirty price** \(P\) of a bond is the present value (PV) of all future cash flows discounted at the appropriate **periodic yield** \(i\) (i.e., YTM divided by \(m\)):

\[
\boxed{P = \sum_{t=1}^{n}\frac{C}{(1+i)^{t}} \;+\; \frac{F}{(1+i)^{n}}}
\tag{1}
\]

If the bond is **quoted with a yield curve** (different discount rates for each cash flow), replace the single \(i\) with the **spot rate** \(s_t\):

\[
\boxed{P = \sum_{t=1}^{n}\frac{C}{(1+s_t)^{t}} \;+\; \frac{F}{(1+s_n)^{n}}}
\tag{2}
\]

### 8.3.2  Example 1 – Pricing a Semi‑Annual Coupon Bond  

> **Data**  
> * Face value \(F = \$1,000\)  
> * Coupon rate \(c = 6\%\) (semi‑annual) → \(C = \frac{0.06}{2}\times 1,000 = \$30\) per period  
> * Maturity \(T = 5\) years → \(n = 10\) periods  
> * Market YTM \(y = 5\%\) (annual) → periodic \(i = 0.05/2 = 0.025\)  

**Step‑by‑step**  

1. Compute PV of each coupon: \(\displaystyle \frac{30}{(1.025)^t}\) for \(t=1\ldots9\).  
2. Compute PV of final coupon + principal: \(\displaystyle \frac{30+1,000}{(1.025)^{10}}\).  
3. Sum all PVs.

Using a calculator (or Excel `=PV(0.025,10,30,1000)`):

\[
P = \$1,045.58 \quad\text{(dirty price)}
\]

If the bond is **settled halfway through a coupon period**, subtract accrued interest to obtain the **clean price**.

### 8.3.3  Yield to Maturity (YTM) – Solving for \(y\)  

YTM is the **root** of equation (1). Because it appears in the exponent, we solve iteratively (Newton‑Raphson, bisection) or use financial calculators.

**Example 2 – Finding YTM**  

A bond trades at **\$950** (dirty). Same cash‑flow structure as Example 1. Find YTM.

1. Set up equation:  

\[
950 = \sum_{t=1}^{10}\frac{30}{(1+i)^t} + \frac{1,000}{(1+i)^{10}}
\]

2. Guess \(i = 3\%\) (annual 6%). Compute price → \$1,045 (too high).  
3. Increase \(i\) to 4% (annual 8%). Compute price → \$925 (too low).  
4. Interpolate:  

\[
i \approx 0.03 + \frac{1,045-950}{1,045-925}\times(0.04-0.03) = 0.0336
\]

Annual YTM ≈ **6.72 %**.

---  

## 8.4  Duration – Measuring Interest‑Rate Sensitivity  

### 8.4.1  **Macaulay Duration**  

\[
\boxed{D_{\text{Mac}} = \frac{\displaystyle\sum_{t=1}^{n} t \times \frac{CF_t}{(1+y)^t}}{P}}
\tag{3}
\]

- **Units:** years.  
- Represents the **weighted average time** until cash flows are received.

### 8.4.2  **Modified Duration**  

\[
\boxed{D_{\text{Mod}} = \frac{D_{\text{Mac}}}{1+y}}
\tag{4}
\]

- Approximates the **percentage price change** for a **small parallel shift** in yield:  

\[
\Delta P \approx -D_{\text{Mod}} \times \Delta y \times P
\]

### 8.4.3  **Effective Duration** (for bonds with embedded options)  

\[
\boxed{D_{\text{Eff}} = \frac{P_{-} - P_{+}}{2\,P_0\,\Delta y}}
\tag{5}
\]

where \(P_{-}\) and \(P_{+}\) are prices computed with yields \(y-\Delta y\) and \(y+\Delta y\) respectively.

### 8.4.4  Example 3 – Duration of the Bond in Example 1  

Using the cash‑flow schedule and \(y = 5\%\) (annual):

| \(t\) | \(CF_t\) | PV factor \((1.025)^{-t}\) | PV | \(t \times\)PV |
|------|----------|---------------------------|----|----------------|
| 1 | 30 | 0.97561 | 29.27 | 29.27 |
| 2 | 30 | 0.95181 | 28.55 | 57.10 |
| … | … | … | … | … |
| 9 | 30 | 0.78744 | 23.62 | 212.58 |
|10 | 1,030 | 0.76742 | 791.07 | 7,910.70 |
| **Sum** | – | – | **1,045.58** | **9,215.00** |

\[
D_{\text{Mac}} = \frac{9,215}{1,045.58}= 8.81\ \text{years}
\]

\[
D_{\text{Mod}} = \frac{8.81}{1.05}= 8.39\ \text{years}
\]

Interpretation: a **100 bps increase** in YTM would **decrease price by ≈ 8.39 %** (≈ \$87.9 per \$1,000 face).

---  

## 8.5  Convexity – Refining the Duration Approximation  

### 8.5.1  **Convexity Formula**  

\[
\boxed{C = \frac{1}{P}\sum_{t=1}^{n}\frac{t(t+1)\,CF_t}{(1+y)^{t+2}}}
\tag{6}
\]

- **Units:** years\(^2\).  
- Captures the **curvature** of the price‑yield relationship.

### 8.5.2  Price Approximation Using Duration & Convexity  

For a change \(\Delta y\) (in decimal form):

\[
\frac{\Delta P}{P} \approx -D_{\text{Mod}}\Delta y + \frac{1}{2}C(\Delta y)^2
\tag{7}
\]

### 8.5.3  Example 4 – Convexity of the Bond in Example 1  

Continuing the table, compute \(t(t+1) \times\)PV:

| \(t\) | PV (from above) | \(t(t+1)\) | Contribution \(\frac{t(t+1)PV}{(1.025)^{2}}\) |
|------|----------------|-----------|----------------------------------------------|
| 1 | 29.27 | 2 | 57.07 |
| 2 | 28.55 | 6 | 166.99 |
| … | … | … | … |
|10 | 791.07 | 110 | 6,761.5 |

Sum of contributions ≈ **13,200**.  

\[
C = \frac{13,200}{1,045.58}= 12.63\ \text{years}^2
\]

**Check the approximation**: Suppose YTM rises by 50 bps (\(\Delta y = 0.005\)).

\[
\frac{\Delta P}{P} \approx -8.39(0.005) + \frac{1}{2}\times12.63(0.005)^2 = -0.04195 + 0.000158 = -0.04179
\]

Predicted price drop ≈ **4.18 %** → New price ≈ **\$1,045.58 × 0.9582 ≈ \$1,001.3**.  
Exact price using \(y=5.5\%\) yields \$1,001.0 – the approximation is excellent.

---  

## 8.6  Term Structure of Interest Rates  

The **term structure** (or yield curve) describes how yields vary with maturity. It reflects expectations about future rates, risk premiums, and market segmentation.

### 8.6.1  Core Concepts  

| **Term** | **Definition** |
|----------|----------------|
| **Spot Rate** (\(s_t\)) | **Yield on a zero‑coupon bond** that matures at time \(t\). |
| **Forward Rate** (\(f_{t,t+k}\)) | **Implied rate for the period \([t, t+k]\)** derived from spot rates. |
| **Zero‑Coupon (Zero) Curve** | Plot of spot rates versus maturity. |
| **Par Yield Curve** | Yield of a **hypothetical coupon bond** that trades at par for each maturity. |
| **Yield Curve Shapes** | **Normal (upward), Inverted (downward), Flat, Humped** – each conveys macro‑economic expectations. |
| **Bootstrapping** | **Iterative method** to extract spot rates from market prices of coupon bonds. |

### 8.6.2  Relationship Between Spot and Forward Rates  

From no‑arbitrage:

\[
(1+s_{t+k})^{t+k} = (1+s_t)^{t}\,(1+f_{t,t+k})^{k}
\]

Solving for the forward rate:

\[
\boxed{f_{t,t+k}= \left[\frac{(1+s_{t+k})^{t+k}}{(1+s_t)^{t}}\right]^{

---

## Chapter 9: Derivatives Pricing: Options, Futures, Forwards, and Swaps

# **Chapter 9 – Derivatives Pricing: Options, Futures, Forwards, and Swaps**  

*Prepared for Chartered Accountant (CA) examinations and professional practice*  

---  

## 1. Introduction  

Derivatives are **financial contracts whose value derives from the performance of an underlying asset, index, rate, or event**. They are essential tools for **risk management, speculation, and arbitrage**. This chapter covers the four most widely used derivative instruments:

| Instrument | Primary Underlying | Typical Users | Key Pricing Feature |
|------------|-------------------|---------------|---------------------|
| **Forwards** | Physical asset, index, rate | Corporates, banks | No‑initial‑cost, linear payoff |
| **Futures** | Same as forwards, but exchange‑traded | Hedgers, speculators | Daily marking‑to‑market, margin |
| **Options** | Equity, commodity, FX, rates | Investors, traders | Asymmetric payoff, optionality |
| **Swaps** | Interest rates, currencies, commodities | Corporates, financial institutions | Series of cash‑flows exchanged |

Understanding the **valuation mechanics** of each instrument is a prerequisite for CA‑level exam questions and for real‑world financial reporting (IAS 12, IFRS 9, ASC 815).  

---  

## 2. Fundamental Concepts  

### 2.1 Time Value of Money  

All derivative pricing rests on **discounting future cash flows** at an appropriate risk‑adjusted rate.  

\[
PV = \frac{CF}{(1+r)^t}
\]

where  

* \(PV\) = present value,  
* \(CF\) = cash flow at time \(t\),  
* \(r\) = discount rate (risk‑free rate for pure arbitrage pricing).  

### 2.2 No‑Arbitrage Principle  

If two portfolios generate **identical cash flows** in every state of the world, they must have the **same price**. Any price discrepancy creates an arbitrage opportunity that market participants will exploit until equilibrium is restored.  

### 2.3 Risk‑Neutral Valuation  

Under the **risk‑neutral measure** \(\mathbb{Q}\), all assets earn the risk‑free rate \(r_f\). The price of a derivative \(V_0\) is  

\[
V_0 = e^{-r_f T}\,\mathbb{E}^{\mathbb{Q}}[\,\text{Payoff at }T\,]
\]

This framework underlies the Black‑Scholes‑Merton (BSM) model, the forward‑price formula, and many swap‑valuation techniques.  

---  

## 3. Forward Contracts  

### 3.1 Definition  

A **forward contract** is a **bilateral, over‑the‑counter (OTC) agreement** to buy (long) or sell (short) an underlying asset at a predetermined price \(F_0\) on a future date \(T\).  

### 3.2 Forward Price Derivation  

Assume a non‑dividend‑paying stock with spot price \(S_0\) and a continuously compounded risk‑free rate \(r\). The **no‑arbitrage forward price** is  

\[
\boxed{F_0 = S_0 e^{rT}}
\]

If the underlying pays a known dividend yield \(q\) (continuous), the formula becomes  

\[
\boxed{F_0 = S_0 e^{(r-q)T}}
\]

#### **Derivation (Step‑by‑Step)**  

1. **Construct a synthetic forward**:  
   * Borrow \(S_0\) at rate \(r\).  
   * Use the borrowed cash to buy the underlying today.  
2. **Enter a short forward** to sell the asset at \(T\) for price \(F_0\).  
3. **At maturity**:  
   * Deliver the asset under the forward, receive \(F_0\).  
   * Repay the loan: \(S_0 e^{rT}\).  
4. **No‑arbitrage condition**: cash inflow = cash outflow → \(F_0 = S_0 e^{rT}\).  

### 3.3 Valuation of Existing Forward  

If the market forward price at time \(t\) is \(F_t\) (different from the original contract price \(K\)), the **value of the forward to the long side** is  

\[
\boxed{V_t = e^{-r(T-t)}\,(F_t - K)}
\]

#### **Numerical Example**  

| Item | Value |
|------|-------|
| Spot price today, \(S_0\) | ₹1,200 |
| Risk‑free rate, \(r\) (annual, continuous) | 6 % |
| Time to maturity, \(T\) | 0.5 yr |
| Forward contract price, \(K\) | ₹1,250 |

1. **Compute theoretical forward price**:  

\[
F_0 = 1,200 \times e^{0.06 \times 0.5}=1,200 \times e^{0.03}=1,200 \times 1.03045 = \mathbf{₹1,236.54}
\]

2. **Assume market forward price at \(t=0.25\) yr is \(F_{0.25}=₹1,240\)**.  

3. **Value of the forward to the long**:  

\[
V_{0.25}=e^{-0.06(0.5-0.25)}\,(1,240-1,250)=e^{-0.015}\times(-10)=0.9851\times(-10)=\mathbf{-₹9.85}
\]

The long position is **out‑of‑the‑money** by ₹9.85.  

### 3.4 Accounting Treatment (IFRS 9)  

* **Initial recognition** – no entry (zero cost).  
* **Subsequent measurement** – fair value changes recognized in profit or loss (FVTPL) unless designated as hedging instrument.  

---  

## 4. Futures Contracts  

### 4.1 Definition  

A **futures contract** is a **standardised, exchange‑traded forward** with daily settlement (mark‑to‑market) and a **margin system** to mitigate counter‑party risk.  

### 4.2 Futures vs. Forwards – Key Differences  

| Feature | Forward | Futures |
|---------|---------|---------|
| Trading venue | OTC | Exchange |
| Settlement | At maturity (usually physical) | Daily cash‑settlement |
| Credit risk | Counter‑party | Cleared by clearinghouse |
| Pricing | Spot‑based, no‑arbitrage | Futures price may differ due to **cost‑of‑carry** and **convexity adjustment** |

### 4.3 Cost‑of‑Carry Model  

For a non‑dividend‑paying asset, the **theoretical futures price** \(F_0^{\text{fut}}\) equals the forward price:  

\[
F_0^{\text{fut}} = S_0 e^{rT}
\]

When the underlying **pays a known dividend yield \(q\)** or **has storage costs \(c\)**, the formula becomes  

\[
\boxed{F_0^{\text{fut}} = S_0 e^{(r+ c - q)T}}
\]

### 4.4 Valuation of a Futures Position  

Because of daily settlement, the **value of a futures contract to the holder is always zero** immediately after a margin payment. The **profit or loss** over a period \([t, t+\Delta t]\) is  

\[
\Delta \Pi = (F_{t+\Delta t} - F_t) \times \text{Contract Size}
\]

### 4.5 Example – Index Futures  

Assume the **Nifty 50 index** is at 15,000 points.  

* Risk‑free rate \(r = 5\%\) (continuous).  
* No dividend yield.  
* Time to maturity \(T = 90\) days = 0.2466 yr.  

**Theoretical futures price**  

\[
F_0^{\text{fut}} = 15,000 \times e^{0.05 \times 0.2466}=15,000 \times e^{0.01233}=15,000 \times 1.0124 = \mathbf{15,186\;points}
\]

If the market quotes 15,210 points, a trader can **sell the futures** (short) and **buy the index** (long) to lock in a risk‑free profit of  

\[
(15,210 - 15,186) \times \text{contract multiplier (₹75)} = 24 \times 75 = \mathbf{₹1,800}
\]

---  

## 5. Options  

### 5.1 Definition  

An **option** is a **contract that gives the holder the right, but not the obligation, to buy (call) or sell (put) an underlying asset at a predetermined strike price \(K\) on or before a specified expiry date \(T\)**.  

* **European option** – exercisable only at \(T\).  
* **American option** – exercisable at any time up to \(T\).  

### 5.2 Payoff Diagrams  

| Option Type | Payoff at Expiry \(\Pi_T\) |
|-------------|---------------------------|
| **Long Call** | \(\max(S_T - K, 0)\) |
| **Short Call** | \(-\max(S_T - K, 0)\) |
| **Long Put** | \(\max(K - S_T, 0)\) |
| **Short Put** | \(-\max(K - S_T, 0)\) |

*(All payoffs are per unit of underlying; multiply by contract size for monetary value.)*  

### 5.3 Black‑Scholes‑Merton (BSM) Model – European Options  

Assumptions:  

1. Underlying follows **Geometric Brownian Motion** with constant volatility \(\sigma\).  
2. No arbitrage, frictionless markets, continuous trading.  
3. Constant risk‑free rate \(r\) and dividend yield \(q\).  

#### 5.3.1 Formulae  

\[
\begin{aligned}
d_1 &= \frac{\ln\!\left(\frac{S_0}{K}\right) + \left(r - q + \tfrac{1}{2}\sigma^2\right)T}{\sigma\sqrt{T}}\\[4pt]
d_2 &= d_1 - \sigma\sqrt{T}
\end{aligned}
\]

\[
\boxed{C_0 = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)} \qquad\text{(European Call)}
\]

\[
\boxed{P_0 = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)} \qquad\text{(European Put)}
\]

where \(N(\cdot)\) is the cumulative standard normal distribution.  

#### 5.3.2 Greeks – Sensitivities  

| Greek | Symbol | Interpretation |
|-------|--------|----------------|
| **Delta** | \(\Delta\) | \(\displaystyle \frac{\partial V}{\partial S}\) – price change per unit change in underlying |
| **Gamma** | \(\Gamma\) | \(\displaystyle \frac{\partial^2 V}{\partial S^2}\) – curvature of Delta |
| **Theta** | \(\Theta\) | \(\displaystyle \frac{\partial V}{\partial t}\) – time decay |
| **Vega** | \(\nu\) | \(\displaystyle \frac{\partial V}{\partial \sigma}\) – sensitivity to volatility |
| **Rho** | \(\rho\) | \(\displaystyle \frac{\partial V}{\partial r}\) – sensitivity to risk‑free rate |

*Exact analytical expressions are provided in the appendix.*  

### 5.4 Binomial Tree Model – American Options  

The **Cox‑Ross‑Rubinstein (CRR) binomial model** approximates the underlying price evolution with up‑ and down‑moves at each step.  

#### 5.4.1 Parameters  

\[
\begin{aligned}
u &= e^{\sigma\sqrt{\Delta t}} \quad\text{(up factor)}\\
d &= e^{-\sigma\sqrt{\Delta t}} = \frac{1}{u} \quad\text{(down factor)}\\
p &= \frac{e^{(r-q)\Delta t} - d}{u - d} \quad\text{(risk‑neutral up probability)}
\end{aligned}
\]

where \(\Delta t = T/n\) and \(n\) = number of steps.  

#### 5.4.2 Valuation Steps  

1. **Generate price lattice** for \(S_{i,j}=S_0 u^{j} d^{i-j}\) (i = step, j = up‑moves).  
2. **Compute terminal option values** using payoff formula.  
3. **Roll back**:  

\[
V_{i,j}=e^{-r\Delta t}\big[p\,V_{i+1,j+1}+(1-p)\,V_{i+1,j}\big]
\]

4. **For American options**, at each node compare the **continuation value** above with the **early‑exercise value** \(\max

---

## Chapter 10: Advanced Derivatives: Black-Scholes-Merton, Binomial Trees, and The Greeks

# **Chapter 10 – Advanced Derivatives: Black‑Scholes‑Merton, Binomial Trees, and The Greeks**  

*Prepared for Chartered Accountant (CA) and professional finance examinations*  

---  

## 1. Introduction  

Derivatives are contracts whose value derives from an underlying asset (equity, commodity, currency, interest rate, etc.).  After mastering basic forwards, futures, and plain‑vanilla options, the next logical step is to understand **how to price options analytically** and **how to manage the associated risks**.  

This chapter covers three pillars of modern option theory:

| Pillar | What you will learn |
|--------|--------------------|
| **Black‑Scholes‑Merton (BSM) model** | Closed‑form pricing for European‑style options, implied volatility, and the concept of risk‑neutral valuation. |
| **Binomial‑tree models** | Discrete‑time pricing that works for American options, dividend‑paying stocks, and exotic pay‑offs. |
| **The Greeks** | Sensitivities of option price to underlying variables; how to compute, interpret, and use them for hedging. |

Each section contains **formal definitions (bolded), derivations, numerical examples, and step‑by‑step CA‑style problem‑solving methods**.  

---  

## 2. Black‑Scholes‑Merton (BSM) Model  

### 2.1. Core Assumptions  

> **Assumption 1 – Frictionless Markets** – No transaction costs, taxes, or restrictions on short‑selling.  
> **Assumption 2 – Continuous Trading** – The underlying asset can be bought or sold continuously.  
> **Assumption 3 – Log‑Normal Returns** – The price \(S_t\) follows a geometric Brownian motion:  

\[
dS_t = \mu S_t dt + \sigma S_t dW_t
\]

where \(\mu\) is the drift, \(\sigma\) the **volatility**, and \(W_t\) a standard Wiener process.  
> **Assumption 4 – Constant Parameters** – \(\mu, \sigma, r\) (risk‑free rate) are constant over the option’s life.  
> **Assumption 5 – No Dividends** – The underlying pays no cash dividends (later we relax this).  

### 2.2. Derivation Sketch (Risk‑Neutral Valuation)  

1. **Construct a risk‑free portfolio**: long \(\Delta\) units of the stock, short one option.  
2. **Apply Itô’s Lemma** to the option price \(V(S,t)\):  

\[
dV = \frac{\partial V}{\partial t}dt + \frac{\partial V}{\partial S}dS + \frac{1}{2}\frac{\partial^2 V}{\partial S^2}\sigma^2 S^2 dt
\]

3. **Eliminate the stochastic term** by choosing \(\Delta = \frac{\partial V}{\partial S}\) (the **Delta**).  
4. The portfolio’s return must equal the risk‑free rate \(r\):  

\[
d\Pi = \Delta dS - dV = r\Pi dt
\]

5. Substituting and simplifying yields the **Black‑Scholes partial differential equation (PDE)**:  

\[
\boxed{\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2\frac{\partial^2 V}{\partial S^2}+ rS\frac{\partial V}{\partial S} - rV = 0}
\]

6. Solving the PDE with the terminal condition \(V(S,T)=\max(S-K,0)\) (European call) gives the **closed‑form solution**.

### 2.3. The Black‑Scholes‑Merton Formula  

For a **European call** (\(C\)) and **European put** (\(P\)) on a non‑dividend‑paying stock:

\[
\boxed{C = S_0 N(d_1) - Ke^{-rT} N(d_2)}
\]
\[
\boxed{P = Ke^{-rT} N(-d_2) - S_0 N(-d_1)}
\]

where  

\[
d_1 = \frac{\ln\!\left(\frac{S_0}{K}\right) + \left(r + \frac{\sigma^2}{2}\right)T}{\sigma\sqrt{T}}, \qquad
d_2 = d_1 - \sigma\sqrt{T}
\]

- \(S_0\) – current spot price  
- \(K\) – strike price  
- \(T\) – time to maturity (in years)  
- \(r\) – continuously compounded risk‑free rate  
- \(\sigma\) – **volatility** of the underlying (annualised)  
- \(N(\cdot)\) – cumulative distribution function (CDF) of the standard normal distribution  

#### 2.3.1. Example – Pricing a European Call  

| Parameter | Value |
|-----------|-------|
| Spot price \(S_0\) | **\$52** |
| Strike \(K\) | **\$50** |
| Time to expiry \(T\) | **0.75 yr** |
| Risk‑free rate \(r\) | **5 %** (continuously compounded) |
| Volatility \(\sigma\) | **30 %** |

1. Compute \(d_1\) and \(d_2\):

\[
\begin{aligned}
d_1 &= \frac{\ln(52/50) + (0.05 + 0.5\times0.3^2)\times0.75}{0.30\sqrt{0.75}}\\
    &= \frac{0.03922 + (0.05+0.045)\times0.75}{0.30\times0.8660}\\
    &= \frac{0.03922 + 0.07125}{0.2598}=0.426\\[4pt]
d_2 &= d_1 - 0.30\sqrt{0.75}=0.426-0.2598=0.166
\end{aligned}
\]

2. Look up \(N(d_1)=N(0.426)=0.665\) and \(N(d_2)=N(0.166)=0.566\).  

3. Plug into the formula:

\[
\begin{aligned}
C &= 52 \times 0.665 - 50 e^{-0.05\times0.75}\times 0.566\\
  &= 34.58 - 50 \times e^{-0.0375}\times0.566\\
  &= 34.58 - 50 \times 0.9632 \times 0.566\\
  &= 34.58 - 27.28 = **\$7.30**
\end{aligned}
\]

Thus the fair price of the European call is **\$7.30**.

### 2.4. Implied Volatility  

Given a market price \(C_{\text{mkt}}\), the **implied volatility** \(\hat\sigma\) solves  

\[
C_{\text{BSM}}(S_0,K,T,r,\hat\sigma)=C_{\text{mkt}}
\]

Because the BSM formula is monotonic in \(\sigma\), numerical root‑finding (Newton‑Raphson, bisection) is used.  

#### Example – Finding Implied Volatility  

Suppose the same call trades at **\$9.00**. Using Newton‑Raphson:

1. **Initial guess** \(\sigma_0 = 0.30\).  
2. Compute price \(C(\sigma_0)=7.30\) and **vega** (see Section 5) \(Vega = S_0\sqrt{T}\,N'(d_1) = 52\sqrt{0.75}\times 0.368 = 13.2\).  
3. Update:  

\[
\sigma_1 = \sigma_0 + \frac{C_{\text{mkt}}-C(\sigma_0)}{Vega}
          = 0.30 + \frac{9.00-7.30}{13.2}=0.30+0.129=0.429
\]

4. Re‑evaluate; after a few iterations the solution converges to **\(\hat\sigma \approx 38.5\%\)**.

---  

## 3. Binomial‑Tree Models  

The BSM model is elegant but limited to **European** options and constant parameters.  The **binomial tree** (Cox‑Ross‑Rubinstein, CRR) provides a flexible, discrete‑time framework that can handle:

* American early‑exercise features  
* Discrete dividends  
* Time‑varying volatility or interest rates  
* Exotic pay‑offs (e.g., barrier options)  

### 3.1. One‑Step Binomial Model  

Assume the underlying can move **up** by factor \(u\) or **down** by factor \(d\) over a single period \(\Delta t\).  

\[
S_u = S_0 u,\qquad S_d = S_0 d
\]

Define the **risk‑neutral probability** \(q\) such that the expected discounted stock price equals the current price:

\[
S_0 = e^{-r\Delta t}\bigl(q S_u + (1-q) S_d\bigr)
\]

Solving for \(q\):

\[
\boxed{q = \frac{e^{r\Delta t} - d}{u-d}}
\]

The option price is then:

\[
\boxed{V_0 = e^{-r\Delta t}\bigl(q V_u + (1-q) V_d\bigr)}
\]

where \(V_u, V_d\) are the option values at the up and down nodes (pay‑off at maturity for a European option, or the maximum of continuation value and early‑exercise value for an American option).

#### Example – One‑Step American Put  

| Parameter | Value |
|-----------|-------|
| \(S_0\) | **\$100** |
| \(K\) | **\$95** |
| \(r\) | **4 %** (cont.) |
| \(\sigma\) | **20 %** |
| \(\Delta t\) | **0.5 yr** |
| \(u = e^{\sigma\sqrt{\Delta t}} = e^{0.20\sqrt{0.5}} = 1.151\) |
| \(d = e^{-\sigma\sqrt{\Delta t}} = 1/u = 0.869\) |
| \(q = \frac{e^{0.04\times0.5} - d}{u-d}= \frac{1.0202-0.869}{1.151-0.869}=0.543\) |

1. **Stock values at expiry**:  

\[
S_u = 100\times1.151 = 115.1,\qquad S_d = 100\times0.869 = 86.9
\]

2. **Pay‑offs** (American put):  

\[
V_u = \max(K - S_u,0) = 0,\qquad V_d = \max(K - S_d,0) = 95-86.9 = 8.1
\]

3. **Continuation value** at node \(d\) (if we *did not* exercise early):  

\[
C_d = e^{-0.04\times0.5}\bigl(q\cdot0 + (1-q)\cdot8.1\bigr)=0.9804\times0.457\times8.1=3.62
\]

Since early exercise value at node \(d\) is \(8.1 > 3.62\), we **exercise**.  

4. **Option price today**:  

\[
V_0 = e^{-0.04\times0.5}\bigl(q\cdot0 + (1-q)\cdot8.1\bigr)=3.62
\]

Thus the American put is worth **\$3.62**.

### 3.2. Multi‑Step CRR Tree  

For \(N\) periods of length \(\Delta t = T/N\):

\[
u = e^{\sigma\sqrt{\Delta t}},\qquad d = e^{-\sigma\sqrt{\Delta t}},\qquad
q = \frac{e^{r\Delta t} - d}{u-d}
\]

The price at node \((i,j)\) (i‑th time step, j up‑moves) is  

\[
S_{i,j}=S_0 u^{j} d^{i-j}
\]

**Backward induction** proceeds from terminal pay‑offs to the root:

\[
V_{i,j}=e^{-r\Delta t}\bigl(q V_{i+1,j+1} + (1-q) V_{i+1,j}\bigr)
\]

For an **American** option, replace \(V_{i,j}\) with  

\[
V_{

---

## Chapter 11: Portfolio Management and Asset Pricing Models (CAPM, APT)

# **Chapter 11 – Portfolio Management & Asset‑Pricing Models**  
*CAPM, APT and Their Applications in Professional Practice*  

---

## Table of Contents
1. [Introduction](#introduction)  
2. [Foundations of Portfolio Theory](#foundations-of-portfolio-theory)  
   - 2.1  **Risk & Return**  
   - 2.2  **Diversification & Correlation**  
   - 2.3  **Mean‑Variance Optimization**  
   - 2.4  **Efficient Frontier, CML & SML**  
3. [Capital Asset Pricing Model (CAPM)](#capital-asset-pricing-model-capm)  
   - 3.1  **Assumptions**  
   - 3.2  **Derivation & Formulae**  
   - 3.3  **Beta Estimation**  
   - 3.4  **CAPM in Practice – Numerical Example**  
   - 3.5  **Limitations & Extensions**  
4. [Arbitrage Pricing Theory (APT)](#arbitrage-pricing-theory-apt)  
   - 4.1  **Key Assumptions**  
   - 4.2  **Multi‑Factor Model**  
   - 4.3  **Factor Identification & Estimation**  
   - 4.4  **APT Numerical Example**  
5. [Portfolio Performance Measurement](#portfolio-performance-measurement)  
   - 5.1  **Sharpe Ratio**  
   - 5.2  **Treynor Ratio**  
   - 5.3  **Jensen’s Alpha**  
   - 5.4  **Information Ratio**  
6. [Advanced Portfolio Construction Techniques]  
   - 6.1  **Constrained Mean‑Variance Optimization**  
   - 6.2  **Black‑Litterman Model**  
   - 6.3  **Risk Parity & Factor‑Tilted Portfolios**  
7. [Step‑by‑Step CA‑Level Problem Solving]  
   - 7.1  **CAPM‑Based Valuation**  
   - 7.2  **APT Factor‑Regression**  
   - 7.3  **Optimal Portfolio with Short‑Sale Constraints**  
8. [Summary & Key Take‑aways]  
9. [Practice Questions & Solutions]  

---

## 1. Introduction <a name="introduction"></a>

Portfolio management is the art and science of allocating capital among a set of assets to achieve a desired trade‑off between **expected return** and **risk**. Modern portfolio theory (MPT) provides the analytical framework, while **asset‑pricing models** such as the **Capital Asset Pricing Model (CAPM)** and the **Arbitrage Pricing Theory (APT)** explain how individual securities are priced relative to systematic risk factors.

> **Goal of this chapter** – Equip you with the theoretical foundations, quantitative tools, and exam‑style problem‑solving techniques required to tackle CA‑level questions on portfolio construction, risk measurement, and asset‑pricing.

---

## 2. Foundations of Portfolio Theory <a name="foundations-of-portfolio-theory"></a>

### 2.1 **Risk & Return**

| Term | Definition |
|------|------------|
| **Expected Return** (**\(E[R]\)**) | The probability‑weighted average of all possible returns of an asset or portfolio. |
| **Variance** (**\(\sigma^{2}\)**) | Measure of dispersion of returns around the mean; quantifies **total risk**. |
| **Standard Deviation** (**\(\sigma\)**) | Square‑root of variance; the most common risk metric in MPT. |
| **Systematic (Market) Risk** | Risk that cannot be diversified away; driven by macro‑economic factors. |
| **Unsystematic (Idiosyncratic) Risk** | Asset‑specific risk that can be eliminated through diversification. |

Mathematically, for a single asset *i* with possible returns \(R_{i1},R_{i2},\dots,R_{in}\) and probabilities \(p_{1},p_{2},\dots,p_{n}\):

\[
\boxed{E[R_i]=\sum_{k=1}^{n} p_k R_{ik}}
\qquad
\boxed{\sigma_i^{2}= \sum_{k=1}^{n} p_k (R_{ik}-E[R_i])^{2}}
\]

### 2.2 **Diversification & Correlation**

The **covariance** between assets *i* and *j*:

\[
\boxed{\operatorname{Cov}(R_i,R_j)=\sum_{k=1}^{n}p_k(R_{ik}-E[R_i])(R_{jk}-E[R_j])}
\]

Correlation coefficient:

\[
\boxed{\rho_{ij}= \frac{\operatorname{Cov}(R_i,R_j)}{\sigma_i\sigma_j}}
\]

**Key Insight:** If \(\rho_{ij}<1\), combining assets reduces portfolio variance. The lower the correlation, the greater the diversification benefit.

### 2.3 **Mean‑Variance Optimization**

For a portfolio of *N* assets with weight vector \(\mathbf{w} = (w_1,\dots,w_N)^{\prime}\) (where \(\sum w_i = 1\)), the portfolio’s expected return and variance are:

\[
\boxed{E[R_p]=\mathbf{w}^{\prime}\boldsymbol{\mu}}
\qquad
\boxed{\sigma_p^{2}= \mathbf{w}^{\prime}\mathbf{\Sigma}\mathbf{w}}
\]

- \(\boldsymbol{\mu}\) = column vector of individual expected returns.  
- \(\mathbf{\Sigma}\) = covariance matrix of asset returns.

**Optimization Problem (Markowitz):**

\[
\begin{aligned}
\min_{\mathbf{w}} \quad & \mathbf{w}^{\prime}\mathbf{\Sigma}\mathbf{w} \\
\text{s.t.} \quad & \mathbf{w}^{\prime}\boldsymbol{\mu}= \mu^{*} \\
& \mathbf{w}^{\prime}\mathbf{1}=1
\end{aligned}
\]

where \(\mu^{*}\) is a target expected return.

Solution uses Lagrange multipliers; the resulting set of optimal portfolios forms the **efficient frontier**.

### 2.4 **Efficient Frontier, Capital Market Line (CML) & Security Market Line (SML)**

- **Efficient Frontier** – Upper‑most curve of the feasible set; each point offers the highest expected return for a given level of risk.

- **Capital Market Line (CML)** – Line from the risk‑free rate (\(R_f\)) tangent to the efficient frontier. It represents the risk‑return trade‑off for **efficient portfolios** (including the market portfolio).

\[
\boxed{E[R_p]=R_f+\frac{E[R_M]-R_f}{\sigma_M}\,\sigma_p}
\tag{CML}
\]

- **Security Market Line (SML)** – Plots **expected return of individual assets** against their **beta** (systematic risk). Derived from CAPM.

\[
\boxed{E[R_i]=R_f+\beta_i\bigl(E[R_M]-R_f\bigr)}
\tag{SML}
\]

---

## 3. Capital Asset Pricing Model (CAPM) <a name="capital-asset-pricing-model-capm"></a>

### 3.1 **Assumptions**

| # | Assumption | Rationale |
|---|------------|-----------|
| 1 | **Investors are mean‑variance optimizers** (quadratic utility). | Enables use of variance as risk measure. |
| 2 | **Homogeneous expectations** – all investors share the same estimates of \(\boldsymbol{\mu}\) and \(\mathbf{\Sigma}\). | Guarantees a single market portfolio. |
| 3 | **Perfect capital markets** – no taxes, transaction costs, and unlimited borrowing/lending at the risk‑free rate. | Simplifies the risk‑free asset treatment. |
| 4 | **Single period horizon**. | Removes intertemporal complications. |
| 5 | **All assets are infinitely divisible** and **short‑selling is allowed**. | Enables any weight vector \(\mathbf{w}\). |

### 3.2 **Derivation & Formulae**

1. **Market Portfolio (\(M\))** – the unique tangency portfolio on the efficient frontier.  
2. **Beta (\(\beta_i\))** – sensitivity of asset *i* to market movements:

\[
\boxed{\beta_i = \frac{\operatorname{Cov}(R_i,R_M)}{\operatorname{Var}(R_M)}}
\tag{1}
\]

3. **CAPM Equation** (derived by equating the expected excess return of any asset to its contribution to market risk):

\[
\boxed{E[R_i]=R_f+\beta_i\bigl(E[R_M]-R_f\bigr)}
\tag{2}
\]

4. **Portfolio Beta** – linear combination of constituent betas:

\[
\boxed{\beta_p = \sum_{i=1}^{N} w_i \beta_i}
\tag{3}
\]

### 3.3 **Beta Estimation – Step‑by‑Step**

| Step | Action | Formula / Tool |
|------|--------|----------------|
| 1 | **Collect historical price data** for the asset and a market index (e.g., S&P 500). | Daily/weekly returns \(R_{i,t}, R_{M,t}\). |
| 2 | **Compute excess returns**: \(r_{i,t}=R_{i,t}-R_{f,t}\), \(r_{M,t}=R_{M,t}-R_{f,t}\). | Use Treasury bill rate as \(R_f\). |
| 3 | **Run a linear regression**: \(r_{i,t}= \alpha_i + \beta_i r_{M,t} + \varepsilon_t\). | OLS (ordinary least squares). |
| 4 | **Interpret \(\beta_i\)** – slope coefficient; \(\alpha_i\) is the abnormal return (Jensen’s alpha). |
| 5 | **Statistical checks** – \(R^2\), t‑stat of \(\beta\), Durbin‑Watson for autocorrelation. | Ensure reliability. |

### 3.4 **CAPM in Practice – Numerical Example**

**Scenario:**  
- Risk‑free rate \(R_f = 3\%\) per annum.  
- Expected market return \(E[R_M] = 10\%\).  
- Stock **XYZ** has a historical beta of **1.25**.

**Question:** What is the required rate of return for XYZ according to CAPM?

**Solution:**

\[
\begin{aligned}
E[R_{XYZ}] &= R_f + \beta_{XYZ}\bigl(E[R_M]-R_f\bigr) \\
           &= 0.03 + 1.25\,(0.10-0.03) \\
           &= 0.03 + 1.25 \times 0.07 \\
           &= 0.03 + 0.0875 = 0.1175 \; \text{or } 11.75\%
\end{aligned}
\]

Thus, **XYZ must earn at least 11.75 %** to compensate investors for its systematic risk.

#### **CAPM Valuation of a Stock**

Suppose XYZ is expected to pay a dividend of **\$2** next year, growing at **4 %** forever. Using the required return from CAPM (11.75 %):

\[
\boxed{P_0 = \frac{D_1}{k - g} = \frac{2}{0.1175-0.04}= \frac{2}{0.0775}= \$25.81}
\]

If the market price is **\$28**, the stock is **over‑priced** relative to CAPM.

### 3.5 **Limitations & Extensions**

| Limitation | Why it matters | Common Extension |
|------------|----------------|------------------|
| **Single factor (market) only** | Ignores size, value, momentum effects. | **Fama‑French 3‑Factor**, **Carhart 4‑Factor** models. |
| **Assumes constant beta** | Betas can be time‑varying (e.g., during crises). | **Conditional CAPM**, **Regime‑switching models**. |
| **Perfect markets** | Taxes, transaction costs, and borrowing constraints exist. | **Liquidity‑adjusted CAPM**, **Post‑tax CAPM**. |
| **Homogeneous expectations** | In reality, analysts have divergent forecasts. | **Behavioral CAPM**, **Heterogeneous expectations models**. |

---

## 4. Arbitrage Pricing Theory (APT) <a name="arbitrage-pricing-theory-apt"></a>

### 4.1 **Key Assumptions**

| # | Assumption | Implication |
|---|------------|-------------|
| 1 | **No arbitrage** – identical cash flows must have identical prices. | Prices are linear functions of common factors. |
| 2 | **Factor structure** – asset returns are driven by *k* systematic factors (e.g., inflation, GDP growth). | Allows multiple sources of systematic risk. |
| 3 | **

---

## Chapter 12: Mergers, Acquisitions, and Corporate Restructuring

# **Chapter 12 – Mergers, Acquisitions, and Corporate Restructuring**  
*Ultimate Finance Textbook – CA‑Level Study Guide*  

---  

## **Table of Contents**  

| **Section** | **Sub‑sections** |
|-------------|------------------|
| 12.1 | Introduction & Terminology |
| 12.2 | Strategic Motives for M&A |
| 12.3 | Types of Corporate Combinations |
| 12.4 | Valuation Techniques for M&A |
| 12.5 | Deal Structuring & Financing |
| 12.6 | Accounting for Business Combinations |
| 12.7 | Tax Implications |
| 12.8 | Regulatory & Legal Framework |
| 12.9 | Due Diligence Process |
| 12.10 | Post‑Merger Integration (PMI) |
| 12.11 | Corporate Restructuring – Core Forms |
| 12.12 | Financial Modelling of Restructuring |
| 12.13 | Real‑World Case Studies |
| 12.14 | Practice Questions & Step‑by‑Step Solutions |
| 12.15 | Summary Checklist for CA Exams |

---  

## **12.1 Introduction & Terminology**  

Mergers, acquisitions, and corporate restructuring (collectively **M&A**) are the primary tools for firms to achieve strategic, financial, or operational objectives that cannot be realized organically.  

| **Term** | **Definition** |
|----------|----------------|
| **Merger** | **A transaction in which two (or more) companies combine to form a single legal entity**. The surviving entity may retain the name of one of the participants or adopt a new name. |
| **Acquisition** | **The purchase of a controlling interest (≥ 50 % of voting shares) in another company**, either through share purchase, asset purchase, or a combination thereof. |
| **Take‑over** | **A synonym for acquisition, often used when the target is unwilling (hostile takeover).** |
| **Divestiture** | **The sale, spin‑off, or otherwise disposal of a business unit, subsidiary, or asset**. |
| **Spin‑off** | **A corporate restructuring where a parent company creates an independent company by distributing shares of the new entity to its existing shareholders.** |
| **Demerger** | **A split of a company into two or more separate legal entities, each with its own shareholders.** |
| **Recapitalisation** | **A change in the capital structure (e.g., debt‑for‑equity swap) to improve financial stability or tax efficiency.** |
| **Leveraged Buy‑Out (LBO)** | **An acquisition financed primarily with debt, where the target’s assets serve as collateral.** |
| **Goodwill** | **An intangible asset representing the excess of purchase price over the fair value of identifiable net assets acquired.** |
| **Bargain Purchase Gain** | **A gain recognized when the purchase price is less than the fair value of identifiable net assets.** |

> **Note:** In CA‑level examinations, precise terminology and the ability to differentiate between *share purchase* and *asset purchase* are heavily tested.

---  

## **12.2 Strategic Motives for M&A**  

| **Motivation** | **Explanation** | **Illustrative Example** |
|----------------|----------------|--------------------------|
| **Synergy** | **Cost‑saving (operational) or revenue‑enhancing (strategic) benefits** that exceed the sum of the stand‑alone firms. | A logistics firm acquires a warehousing company; combined, they can reduce overlapping admin costs by **$15 m** and increase cross‑selling revenue by **$30 m**. |
| **Market Power** | **Increasing market share, reducing competition, or achieving pricing power**. | Telecom A buys Telecom B, raising combined market share from 18 % to 32 % in a fragmented market. |
| **Diversification** | **Entering new product lines, geographies, or industries** to reduce business risk. | A consumer‑goods company acquires a health‑care firm to diversify away from cyclical consumer demand. |
| **Tax Efficiency** | **Utilising tax loss carry‑forwards, favourable tax jurisdictions, or structuring debt to lower effective tax rate**. | A profitable U.S. firm acquires a loss‑making European subsidiary to offset taxable income. |
| **Financial Engineering** | **Leveraging the target’s cash flows to support high‑leverage structures (LBO)**. | Private‑equity fund purchases a manufacturing firm with **70 % debt** financed against the target’s stable cash flows. |
| **Strategic Realignment** | **Divesting non‑core assets to focus on core competencies**. | A conglomerate spins off its petrochemical division to concentrate on renewable energy. |
| **Regulatory / Policy Drivers** | **Compliance with antitrust, industry consolidation mandates, or government incentives**. | Government encourages consolidation in the banking sector to improve systemic stability. |

---  

## **12.3 Types of Corporate Combinations**  

### 12.3.1 Horizontal, Vertical, and Conglomerate  

| **Combination** | **Definition** | **Typical Synergies** |
|-----------------|----------------|----------------------|
| **Horizontal** | **Merging with a direct competitor operating at the same stage of the value chain**. | Market share, economies of scale, price‑setting power. |
| **Vertical** | **Combining with a supplier (upstream) or distributor/customer (downstream)**. | Supply‑chain control, cost reduction, improved margins. |
| **Conglomerate** | **Merging with a firm in an unrelated industry**. | Diversification, risk reduction, cross‑selling opportunities. |

### 12.3.2 Transaction Structures  

| **Structure** | **Key Features** | **Accounting Treatment** |
|---------------|------------------|--------------------------|
| **Share Purchase** | Buyer acquires shares of the target; target remains a separate legal entity. | **Purchase method** – goodwill recognized; assets & liabilities recorded at fair value. |
| **Asset Purchase** | Buyer selects specific assets & liabilities; often used to avoid unwanted liabilities. | Only acquired assets/liabilities are recorded; no goodwill (unless excess purchase price). |
| **Merger of Equals** | Two firms combine, often via a **stock swap**; no clear acquirer. | Historically *Pooling of Interests* (now prohibited under IFRS/Ind AS); now treated as purchase method. |
| **Reverse Merger** | Private company merges into a public shell to gain listing without IPO. | Same as share purchase; goodwill may arise. |
| **Joint Venture (JV)** | Two firms create a new entity, sharing control and profits. | Equity method or proportionate consolidation, depending on control. |

---  

## **12.4 Valuation Techniques for M&A**  

A CA must be comfortable with **four core valuation approaches** and know when each is appropriate.  

### 12.4.1 Discounted Cash Flow (DCF) Valuation  

\[
\text{Enterprise Value (EV)} = \sum_{t=1}^{n}\frac{FCFF_t}{(1+WACC)^t} + \frac{TV}{(1+WACC)^n}
\]

- **FCFF** – Free Cash Flow to Firm  
- **WACC** – Weighted Average Cost of Capital  
- **TV** – Terminal Value (Gordon Growth or Exit Multiple)  

**Step‑by‑Step DCF Example**  

> **Target:** XYZ Ltd., a mid‑size software firm.  
> **Assumptions:**  
> - FCFF Year‑1 = **$120 m**, growth 8 % for 5 years, then 3 % perpetuity.  
> - WACC = **10 %**.  

| Year | FCFF ($m) | Discount Factor (10 %) | PV of FCFF ($m) |
|------|-----------|------------------------|-----------------|
| 1 | 120.0 | 0.9091 | 109.1 |
| 2 | 129.6 | 0.8264 | 107.1 |
| 3 | 140.0 | 0.7513 | 105.2 |
| 4 | 151.2 | 0.6830 | 103.3 |
| 5 | 163.3 | 0.6209 | 101.4 |
| **Sum** | — | — | **525.9** |

**Terminal Value (TV)** using Gordon Growth:  

\[
TV = \frac{FCFF_{5}\times (1+g)}{WACC - g} = \frac{163.3 \times 1.03}{0.10 - 0.03}= \frac{168.2}{0.07}=2,402.9\ \text{m}
\]

PV of TV:  

\[
PV_{TV}= \frac{2,402.9}{(1+0.10)^5}= \frac{2,402.9}{1.6105}=1,492.2\ \text{m}
\]

**Enterprise Value** = 525.9 + 1,492.2 = **$2,018.1 m**  

If net debt = **$300 m**, **Equity Value** = $1,718.1 m.  

### 12.4.2 Comparable Company Analysis (Comps)  

\[
\text{Equity Value} = \text{Metric} \times \text{Industry Multiple}
\]

- **Metric**: EBITDA, EBIT, Revenue, etc.  
- **Multiple**: EV/EBITDA, P/E, P/S, etc.  

**Example:**  

| Company | EV (m) | EBITDA (m) | EV/EBITDA |
|---------|--------|------------|-----------|
| A | 5,000 | 500 | 10.0 |
| B | 7,200 | 720 | 10.0 |
| C | 4,500 | 450 | 10.0 |
| **Average** | — | — | **10.0** |

Target XYZ’s EBITDA = **$250 m** → **Implied EV** = 250 × 10 = **$2,500 m**.  

### 12.4.3 Precedent Transaction Analysis  

\[
\text{Implied Multiple} = \frac{\text{Transaction EV}}{\text{Metric (e.g., EBITDA)}}
\]

- Use **control premiums** and **synergy adjustments**.  

**Example:**  

| Deal | Year | EV (m) | EBITDA (m) | EV/EBITDA |
|------|------|--------|------------|----------|
| Acq‑1 | 2022 | 3,200 | 280 | 11.4 |
| Acq‑2 | 2021 | 2,800 | 250 | 11.2 |
| **Median** | — | — | — | **11.3** |

Target EBITDA = $250 m → **Implied EV** = 250 × 11.3 = **$2,825 m**.  

### 12.4.4 Leveraged Buy‑Out (LBO) Valuation  

Key equation:  

\[
\text{IRR} = \frac{\text{Equity Cash Flows}}{\text{Equity Investment}}
\]

**Simplified LBO Model Steps**  

1. **Determine Purchase Price (EV).**  
2. **Structure Debt:** Senior, Sub‑senior, Mezzanine – each with interest rates and amortisation.  
3. **Project Cash Flows (EBITDA → FCFE).**  
4. **Apply Debt Repayment Schedule.**  
5. **Calculate Exit EV (e.g., 5‑year EV/EBITDA multiple).**  
6. **Compute Equity IRR.**  

**Sample LBO Problem (CA‑Level)**  

> **Assumptions:**  
> - Purchase EV = **$1,200 m**.  
> - Debt = **70 %** of EV = $840 m (Senior 6 % interest, 5‑year amortisation).  
> - Equity = $360 m.  
> - EBITDA Year‑1 = $150 m, growing 5 % annually.  
> - CapEx = $20 m each year, ΔNWC = $5 m each year.  
> - Exit multiple = 8× EBITDA in Year‑5.  

**Solution Sketch (provided in Section 12.14).**  

---  

## **12.5 Deal Structuring & Financing**  

| **Financing Tool** | **Typical Use‑Case** | **Key Accounting Impact** |
|--------------------|----------------------|---------------------------|
| **Cash Consideration** | Straight‑forward acquisitions; seller prefers liquidity. | Immediate reduction in cash; goodwill recognized if price > fair value of net assets. |
| **Stock Swaps** | Preserves cash, aligns interests of target shareholders. | Equity issuance → increase in share capital & share premium; goodwill may arise. |
| **Convertible Bonds** | Provides upside to investors; lower coupon. | Debt recorded at fair value; conversion feature accounted for as equity component (IFRS 9/Ind AS 109). |
| **Earn‑outs** | Bridges valuation

---

## Chapter 13: Direct Taxation: Corporate Tax Planning and Wealth Tax

# **Chapter 13 – Direct Taxation: Corporate Tax Planning & Wealth Tax**  

*Prepared for CA‑Final / CS examinations*  

---

## **Table of Contents**

1. [Introduction](#introduction)  
2. [Corporate Taxation – Core Concepts](#corporate-taxation)  
   - 2.1 **Taxable Income**  
   - 2.2 **Tax Rates & Slabs**  
   - 2.3 **Allowable Deductions & Exemptions**  
   - 2.4 **Depreciation & Amortisation**  
   - 2.5 **Capital Gains & Losses**  
   - 2.6 **Tax Credits & Incentives**  
3. [Advanced Corporate Tax Planning Techniques](#advanced-planning)  
   - 3.1 **Timing of Income & Expenditure**  
   - 3.2 **Group Relief & Consolidated Returns**  
   - 3.3 **Transfer Pricing & Arm’s‑Length Principle**  
   - 3.4 **International Tax Planning (DTAs, PE, CFC Rules)**  
   - 3.5 **Restructuring – Mergers, Demergers, Spin‑offs**  
   - 3.6 **Advance Rulings & Tax Audits**  
4. [Wealth Tax – Overview & Computation](#wealth-tax)  
   - 4.1 **Definition & Scope**  
   - 4.2 **Tax Base – Net Wealth Calculation**  
   - 4.3 **Exemptions & Thresholds**  
   - 4.4 **Valuation of Assets**  
   - 4.5 **Wealth‑Tax Planning Strategies**  
5. [Step‑by‑Step Methodology for CA‑Level Exam Problems](#methodology)  
6. [Illustrative Real‑World Numerical Examples](#examples)  
7. [Practice Questions & Model Answers](#practice)  
8. [Key Take‑aways & Quick Revision Checklist](#summary)  
9. [Suggested Further Reading](#references)  

---  

<a name="introduction"></a>  

## 1. Introduction  

Direct taxation on corporations and high‑net‑worth individuals forms a cornerstone of fiscal policy. While **Corporate Tax** captures the earnings of legal entities, **Wealth Tax** targets the accumulated net assets of individuals (and, in some jurisdictions, certain entities).  

For CA aspirants, mastery of the **computation**, **planning**, and **compliance** aspects is essential because exam questions frequently intertwine statutory provisions with strategic decision‑making. This chapter dissects the legislative framework, presents the mathematics behind the tax calculations, and equips you with systematic problem‑solving tools.

---  

<a name="corporate-taxation"></a>  

## 2. Corporate Taxation – Core Concepts  

### 2.1 **Taxable Income**  

> **Taxable Income** – *The amount on which corporate tax is levied after deducting all allowable expenses, depreciation, and other deductions from gross total income.*

Mathematically:  

\[
\boxed{\text{Taxable Income (TI)} = \text{Gross Total Income (GTI)} - \text{Allowable Deductions (AD)}}
\]

Where  

\[
\text{GTI} = \sum_{i=1}^{n} \text{Revenue}_{i} + \text{Other Income}
\]

### 2.2 **Tax Rates & Slabs**  

| **Fiscal Year** | **Taxable Income (₹)** | **Tax Rate** |
|----------------|------------------------|--------------|
| FY 2024‑25 (India) | ≤ 250 crore | 25 % |
| FY 2024‑25 (India) | > 250 crore | 30 % |
| FY 2024‑25 (UK) | All | 19 % (scheduled to rise to 25 % from Apr‑2025) |
| FY 2024‑25 (Australia) | ≤ 50 million AUD | 30 % |
| FY 2024‑25 (UAE) | No corporate tax (except oil & gas, foreign banks) |

> **Note:** Always verify the latest Finance Act / Budget for any surcharge, health & education cess, or regional variations.

### 2.3 **Allowable Deductions & Exemptions**  

| **Category** | **Explanation** | **Statutory Reference** |
|--------------|----------------|------------------------|
| **Business Expenses** | Directly incurred for earning income (e.g., salaries, rent, utilities). | Sec. 37(1) Income Tax Act (India) |
| **Depreciation** | Written‑down value (WDV) or straight‑line (SL) based on asset class. | Sec. 32, 33 |
| **Interest on Borrowings** | Deductible if used for business purposes; subject to thin‑capitalisation limits. | Sec. 36(1)(iii) |
| **Losses Brought Forward** | Unabsorbed losses can be set off against future profits (subject to limits). | Sec. 70 |
| **Specified Deductions** | R&D expenditure, contribution to employee welfare funds, etc. | Sec. 35, 35D |

### 2.4 **Depreciation & Amortisation**  

Two methods are permitted in most jurisdictions:

1. **Straight‑Line (SL) Method**  

\[
\text{Depreciation}_{SL} = \frac{\text{Cost of Asset} \times \text{Rate}}{100}
\]

2. **Written‑Down Value (WDV) Method**  

\[
\text{Depreciation}_{WDV}^{(t)} = \text{Opening WDV}_{t} \times \frac{\text{Rate}}{100}
\]

\[
\text{Closing WDV}_{t} = \text{Opening WDV}_{t} - \text{Depreciation}_{WDV}^{(t)}
\]

**Example:** A plant costing ₹10 crore, rate 15 % (WDV).  

| Year | Opening WDV | Depreciation | Closing WDV |
|------|-------------|--------------|-------------|
| 1 | 10.00 | 1.50 | 8.50 |
| 2 | 8.50 | 1.275 | 7.225 |
| … | … | … | … |

### 2.5 **Capital Gains & Losses**  

- **Short‑Term Capital Gains (STCG)** – Asset held ≤ specified period (e.g., 36 months for immovable property in India). Taxed at normal corporate rates.  
- **Long‑Term Capital Gains (LTCG)** – Asset held > specified period. Taxed at concessional rates (e.g., 10 % for listed equities in India, 20 % for immovable property).  

**Computation:**  

\[
\text{Capital Gain} = \text{Sale Consideration} - (\text{Cost of Acquisition} + \text{Cost of Improvement} + \text{Expenses on Transfer})
\]

If **Capital Losses** exist, they can be set off against gains of the same head (STCG vs. LTCG) and, in many jurisdictions, carried forward for up to 8 years.

### 2.6 **Tax Credits & Incentives**  

| **Credit** | **Eligibility** | **Benefit** |
|------------|----------------|------------|
| **R&D Credit** | Expenditure on approved research projects. | 150 % of eligible spend (India) |
| **Investment Allowance** | New plant & machinery in specified sectors. | 30 % of cost as deduction in the year of acquisition |
| **Export Incentive** | Export‑oriented units (EOU). | 5 % surcharge rebate, duty drawback |

> **Key Point:** Credits are **non‑cumulative** unless expressly stated. Always cross‑check the “carry‑forward” provisions.

---  

<a name="advanced-planning"></a>  

## 3. Advanced Corporate Tax Planning Techniques  

### 3.1 Timing of Income & Expenditure  

- **Accelerated Depreciation** (e.g., Section 32(1)(ii) for new plant) → reduces TI in early years.  
- **Deferred Tax Assets (DTA)** – Recognise future tax benefits from carry‑forward losses or unutilised depreciation.  

**Planning Tip:** If a corporation anticipates a higher tax rate in the next FY (e.g., due to a budgetary hike), it may **pre‑pay** certain deductible expenses (e.g., rent, interest) to claim them in the current lower‑rate year.

### 3.2 Group Relief & Consolidated Returns  

- **Group Relief** allows intra‑group loss set‑off, subject to **shareholding thresholds** (≥ 51 % in India).  
- **Consolidated Tax Return** (CTR) – Some jurisdictions permit a single return for the whole group, simplifying compliance and enabling **tax neutral restructuring**.

**Illustration:**  
Parent Co. (₹120 crore profit) + Subsidiary A (₹‑30 crore loss) + Subsidiary B (₹‑10 crore loss).  

Group taxable income = ₹120 – ₹30 – ₹10 = **₹80 crore** → tax at 25 % = **₹20 crore** (instead of ₹30 crore if filed separately).

### 3.3 Transfer Pricing & Arm’s‑Length Principle  

**Definition:** *Transfer pricing* is the pricing of transactions between related parties. The **Arm’s‑Length Principle (ALP)** requires that such prices be comparable to those that would have been charged between independent parties.

- **Methods** (OECD): Comparable Uncontrolled Price (CUP), Resale Price, Cost‑Plus, Transactional Net Margin (TNMM), Profit Split.  
- **Documentation** – Master file, local file, and Country‑by‑Country Report (CbCR) where applicable.

**Penalty Risk:** Non‑compliance can attract **penalties up to 200 %** of the tax under‑payment (India) or **double taxation** via adjustments.

### 3.4 International Tax Planning  

| **Tool** | **Purpose** | **Key Provision** |
|----------|-------------|-------------------|
| **Double Taxation Avoidance Agreement (DTAA)** | Avoid double tax on cross‑border income. | Article 5 (Permanent Establishment), Article 7 (Business Profits). |
| **Treaty Shopping** | Exploit favorable treaty rates. | Anti‑abuse clause (Limitation on Benefits – LoB). |
| **Controlled Foreign Corporation (CFC) Rules** | Tax on passive income of low‑tax subsidiaries. | Substantial Shareholding (≥ 25 %) & Low‑Tax Jurisdiction (< 15 %). |
| **Base Erosion & Profit Shifting (BEPS) Action 13** | Country‑by‑Country Reporting. | Mandatory for MNEs with revenue > €750 million. |

**Strategic Example:**  
A Indian software services firm sets up a **subsidiary in Ireland** (15 % corporate tax). By routing royalty income through the Irish entity, the effective tax rate drops from 25 % to ~15 % after applying the India‑Ireland DTAA (royalty withholding tax 0 %). However, Indian **GAAR** (General Anti‑Avoidance Rule) may apply if the arrangement lacks commercial substance.

### 3.5 Restructuring – Mergers, Demergers, Spin‑offs  

- **Section 115JB (India)** – Minimum Alternate Tax (MAT) may be triggered post‑restructuring.  
- **Capital Gains Exemption** under **Section 47(iii)** for **demergers** if certain conditions (continuity of business, same shareholders) are met.  
- **Tax Neutral Spin‑off** – Transfer of assets to a new entity in exchange for shares; gains are deferred.

**Checklist for Tax‑Neutral Restructuring:**

1. Verify **continuity of ownership** (≥ 75 % of shareholders).  
2. Ensure **business continuity** (same line of business).  
3. Obtain **Advance Ruling** (if required).  
4. File **Form 3CEB** (for demerger) within prescribed timeline.

### 3.6 Advance Rulings & Tax Audits  

- **Advance Ruling** – A pre‑emptive decision by the tax authority on the taxability of a proposed transaction.  
- **Audit Triggers** – Large **related‑party transactions**, **unusual loss patterns**, **high‑value asset disposals**.

**Best Practice:** Maintain **robust transfer‑pricing documentation** and **contemporaneous board minutes** to substantiate commercial rationale.

---  

<a name="wealth-tax"></a>  

## 4. Wealth Tax – Overview & Computation  

> **Wealth Tax** – *A direct tax levied on the net wealth (assets minus liabilities) of an individual or entity as on a specified valuation date.*

> **Note:** While many jurisdictions (e.g., India) have abolished wealth tax, several

---

## Chapter 14: Indirect Taxation: GST, Value Added Taxes, and Customs Duty

# Chapter 14 – Indirect Taxation: **GST**, **Value‑Added Tax (VAT)**, and **Customs Duty**  

*Prepared for CA‑Level examinations and professional practice*  

---  

## 1. Introduction  

Indirect taxes are levied on the **consumption** of goods and services rather than on income or profits. They are collected by an intermediary (the seller) from the ultimate consumer and later remitted to the government. The three major pillars of modern indirect taxation in India (and many other jurisdictions) are:

| Pillar | Acronym | Core Feature |
|--------|---------|--------------|
| **Goods and Services Tax** | **GST** | Destination‑based, multi‑stage, value‑added tax on all supplies of goods & services. |
| **Value‑Added Tax** | **VAT** | Earlier state‑level tax on the value added at each stage; now subsumed by GST in India but still relevant internationally. |
| **Customs Duty** | – | Tax on imports (and, in some cases, exports) levied at the border based on customs valuation and classification. |

Understanding the **mechanics**, **accounting treatment**, and **exam‑level problem‑solving** for each of these taxes is essential for CA‑Final, CMA, and other professional exams.

---  

## 2. Goods and Services Tax (GST)

### 2.1 Definition  

> **Goods and Services Tax (GST)** – a **comprehensive, destination‑based, multi‑stage, value‑added tax** levied on every supply of goods and services in India, subsuming Central Excise, Service Tax, VAT, Central Sales Tax, and other levies.

### 2.2 Structural Overview  

| Component | Governing Law | Rate(s) | Collected By |
|-----------|---------------|--------|--------------|
| **CGST** – Central GST | CGST Act, 2017 | 0 % – 28 % (plus cess) | Central Government |
| **SGST** – State GST | SGST Act, 2017 | Same as CGST | Respective State Government |
| **IGST** – Integrated GST | IGST Act, 2017 | Same as CGST/SGST | Central Government (for inter‑state supplies) |

> **Key Principle:** Tax is **charged on the value added at each stage**; the final consumer bears the cumulative tax, while businesses can claim **Input Tax Credit (ITC)** for taxes paid on inputs.

### 2.3 Key Terms (Bolded)

- **Supply** – *any transaction involving sale, transfer, barter, exchange, license, rental, lease or disposal of goods or services*.
- **Taxable Person** – *any person who carries on business and is registered under GST*.
- **Input Tax Credit (ITC)** – *the credit a taxable person can claim for GST paid on purchases (inputs) used in the course of business*.
- **Composition Scheme** – *a simplified tax scheme for small taxpayers with turnover ≤ ₹1.5 cr (₹75 L for service providers)*.
- **Reverse Charge Mechanism (RCM)** – *tax liability shifts from supplier to recipient*.
- **E‑Way Bill** – *electronic document required for movement of goods above a prescribed value*.
- **Anti‑Profiteering** – *regulation ensuring that benefits of tax rate reductions are passed on to consumers*.

### 2.4 GST Registration  

| Criteria | Threshold (as of FY 2025‑26) |
|----------|------------------------------|
| **Normal Taxpayer** | Turnover > ₹40 L (₹20 L for special category states) |
| **E‑Commerce Operator** | Any aggregate turnover |
| **Inter‑State Supplier** | Any inter‑state supply of goods/services |

**Steps to Register (CA‑level outline):**  

1. **Obtain PAN & Aadhaar** of the proprietor/partner/director.  
2. **Visit the GST Portal** (https://www.gst.gov.in) → *Services → Registration → New Registration*.  
3. **Fill Part‑A** – Business details, PAN, email, mobile. OTP verification.  
4. **Receive Application Reference Number (ARN).**  
5. **Complete Part‑B** – Upload documents (PAN, address proof, bank statement, photographs, incorporation certificate).  
6. **Verification** – Digital Signature Certificate (DSC) for companies; Aadhaar OTP for individuals.  
7. **GSTIN Issuance** – Within 7 days (or 3 days for certain categories).  

### 2.5 Input Tax Credit (ITC) – Mechanics  

**ITC Eligibility Conditions**  

1. **Taxable supply** – The recipient must be a taxable person.  
2. **Possession of tax invoice** – Proper GST invoice must be in possession.  
3. **Receipt of goods/services** – Must have actually received the inputs.  
4. **Payment of tax** – Supplier must have paid GST to the government.  

**ITC Formula**  

\[
\boxed{
\text{ITC}_{\text{available}} = \sum \text{ITC}_{\text{purchases}} - \sum \text{ITC}_{\text{reversed}} - \sum \text{ITC}_{\text{blocked}}
}
\]

- **ITC\(_{purchases}\)** – GST paid on eligible purchases.  
- **ITC\(_{reversed}\)** – ITC reversed on disposal of capital assets, etc.  
- **ITC\(_{blocked}\)** – For motor vehicles, personal expenses, etc.

**ITC Utilisation**  

\[
\text{GST Payable} = \underbrace{\text{Output GST}}_{\text{CGST + SGST/IGST}} - \underbrace{\text{ITC}_{\text{available}}}_{\text{as above}}
\]

If **ITC > Output GST**, the excess is **carried forward** as a **deferred credit** to the next tax period.

### 2.6 GST Returns – Overview  

| Return | Frequency | Forms (as of FY 2025‑26) | Key Features |
|--------|-----------|--------------------------|--------------|
| **GSTR‑1** | Monthly | GSTR‑1 | Outward supplies (sales) |
| **GSTR‑2A/2B** | Auto‑populated | GSTR‑2A (static) / GSTR‑2B (dynamic) | Input tax credit details |
| **GSTR‑3B** | Monthly | GSTR‑3B | Summary of outward & inward supplies; payment of tax |
| **GSTR‑4** | Quarterly (Composition) | GSTR‑4 | Simplified return for composition taxpayers |
| **GSTR‑5** | Monthly (Non‑resident) | GSTR‑5 | For non‑resident taxable persons |
| **GSTR‑9/9C** | Annual | GSTR‑9 (regular) / GSTR‑9C (audit) | Reconciliation and audit |

**Sample GSTR‑3B Calculation (Illustrative)**  

| Description | Amount (₹) |
|-------------|------------|
| **Total Outward Taxable Supplies** | 10,00,000 |
| **CGST @ 9 %** | 90,000 |
| **SGST @ 9 %** | 90,000 |
| **IGST @ 18 %** | 1,80,000 |
| **Total Output GST** | **3,60,000** |
| **ITC Available (CGST/SGST/IGST)** | 2,70,000 |
| **Net GST Payable** | **90,000** (to be paid with challan) |

### 2.7 E‑Way Bill – Practical Example  

**Scenario:** A manufacturer in Maharashtra sells goods worth ₹12 lakhs to a dealer in Karnataka.  

- **Step 1:** Log in to the e‑Way Bill portal (https://ewaybillgst.gov.in).  
- **Step 2:** Enter **GSTIN of supplier**, **GSTIN of recipient**, **HSN code**, **Invoice number**, **Invoice date**, **Total value (₹12,00,000)**, **Transporter details**.  
- **Step 3:** Generate **E‑Way Bill Number (EBN)** – e.g., **23AAAB1234567**.  
- **Step 4:** Print the **QR code** and attach it to the consignment.  

**Compliance:** For inter‑state movement, an e‑Way Bill is mandatory when the value exceeds ₹50,000 (as per latest rules).  

### 2.8 Composition Scheme – Numerical Illustration  

| Parameter | Normal Taxpayer | Composition Taxpayer (₹1 cr turnover) |
|-----------|----------------|----------------------------------------|
| **Tax Rate** | 18 % (CGST 9 % + SGST 9 %) | 1 % (if manufacturing) / 5 % (if service) |
| **Tax Payable on ₹1 cr sales** | ₹18,00,000 | ₹1,00,000 (manufacturing) |
| **Eligibility for ITC** | Yes | No (cannot claim ITC) |
| **Compliance Burden** | Detailed returns (GSTR‑1, GSTR‑3B) | Quarterly return (GSTR‑4) |

> **Exam Tip:** When a problem asks to compare tax liability under normal vs. composition scheme, compute tax payable on the same turnover using the respective rates and note the loss of ITC for composition taxpayers.

### 2.9 Anti‑Profiteering – Conceptual Note  

When the government reduces GST rates, the **Anti‑Profiteering Rules (2018)** require businesses to **pass on the benefit** to consumers within **30 days**. The **National Anti‑Profiteering Authority (NAA)** monitors compliance.  

**Key compliance steps:**  

1. **Maintain records** of purchase cost, selling price, and GST rates.  
2. **Re‑calculate** selling price after a rate change.  
3. **Issue revised invoices** reflecting the lower price.  

---  

## 3. Value‑Added Tax (VAT)

### 3.1 Definition  

> **Value‑Added Tax (VAT)** – a **state‑level, multi‑stage tax** on the **value added** at each point of sale, levied on **goods only** (services are excluded).  

> *Note:* In India, VAT was **replaced by GST** on 1 July 2017, but many countries (e.g., EU members, Canada, Australia) still operate a VAT system. The concepts remain relevant for comparative analysis and CA‑level international taxation.

### 3.2 VAT Mechanics  

**VAT Payable Formula**  

\[
\boxed{
\text{VAT Payable} = \underbrace{\text{Output VAT}}_{\text{VAT on sales}} - \underbrace{\text{Input VAT}}_{\text{VAT on purchases}}
}
\]

**Illustrative Example (UK VAT – 20 % standard rate)**  

| Transaction | Sale Price (ex‑VAT) | VAT @20 % | Total (incl. VAT) |
|-------------|---------------------|----------|-------------------|
| Sale to customer | ₹5,00,000 | ₹1,00,000 | ₹6,00,000 |
| Purchase of raw material | ₹2,00,000 | ₹40,000 | ₹2,40,000 |
| **VAT Payable** | – | **₹1,00,000 – ₹40,000 = ₹60,000** | – |

### 3.3 Key VAT Terms  

- **Taxable Supply** – *any supply of goods that is not exempt.*  
- **Exempt Supply** – *goods/services outside the VAT net (e.g., health, education).*  
- **Zero‑Rated Supply** – *taxable but at 0 % rate; still eligible for ITC.*  
- **VAT Registration Threshold** – *varies by jurisdiction (e.g., £85,000 in the UK).*

### 3.4 VAT vs. GST – Quick Comparison  

| Feature | GST (India) | VAT (pre‑GST India / International) |
|---------|-------------|--------------------------------------|
| **Scope** | Goods + Services (nationwide) | Goods only (state‑level) |
| **Tax Structure** | CGST + SGST + IGST (dual) | Single state tax |
| **Input Credit** | On both goods & services | Only on goods |
| **Place of Taxation** | Destination (where consumption occurs) | Origin (where sale occurs) |
| **Compliance** | Uniform national portal | Separate state returns |

---  

## 4. Customs Duty  

### 4.1 Definition  

> **Customs Duty** – a **tax levied on the import (and, in limited cases, export)

---

## Chapter 15: Principles of Auditing and Assurance Engagements

# **Chapter 15 – Principles of Auditing and Assurance Engagements**  
*Ultimate Finance Textbook – Chartered Accountant (CA) Edition*  

---  

## **Table of Contents**  

| # | Section | Pages |
|---|---------|-------|
| 15.1 | **Introduction & Scope** | 1 |
| 15.2 | **Fundamental Concepts & Terminology** | 3 |
| 15.3 | **Audit Planning & Risk Assessment** | 7 |
| 15.4 | **Materiality & Performance Materiality** | 12 |
| 15.5 | **Audit Evidence – Types & Gathering Techniques** | 16 |
| 15.6 | **Audit Sampling – Theory & Application** | 21 |
| 15.7 | **Audit Risk Model & Analytical Procedures** | 27 |
| 15.8 | **Internal Control Evaluation** | 33 |
| 15.9 | **Audit Documentation (Working Papers)** | 38 |
| 15.10 | **Audit Reporting – Forms & Opinions** | 42 |
| 15.11 | **Assurance Engagements – Types & Frameworks** | 48 |
| 15.12 | **Ethics, Independence & Professional Skepticism** | 55 |
| 15.13 | **International & Indian Auditing Standards (ISA/AS)** | 60 |
| 15.14 | **CA‑Level Exam Problem – Step‑by‑Step Solution** | 68 |
| 15.15 | **Summary & Quick Revision Checklist** | 74 |
| 15.16 | **Further Reading & References** | 76 |

---  

## **15.1 Introduction & Scope**  

Auditing is the **systematic, independent examination** of financial information of an entity, **with the objective of expressing an opinion** on whether the financial statements are presented **fairly, in all material respects**, in accordance with an applicable financial reporting framework.  

Assurance engagements broaden the concept of auditing to include **non‑financial information**, **sustainability reports**, **internal controls**, and **compliance**. This chapter provides a **comprehensive, CA‑level treatment** of the principles, standards, and practical techniques required to conduct high‑quality audits and assurance engagements.  

---  

## **15.2 Fundamental Concepts & Terminology**  

| Term | Definition |
|------|------------|
| **Audit** | **A systematic, independent, and documented process** for obtaining evidence about an entity’s financial statements and evaluating the evidence to express a conclusion. |
| **Assurance Engagement** | **An engagement in which a practitioner expresses a conclusion designed to enhance the confidence of the intended users** about the outcome of the evaluation of a subject matter against criteria. |
| **Independent Auditor** | **A person or firm that is independent in both fact and appearance** and is engaged to perform an audit. |
| **Materiality** | **The magnitude of an omission or misstatement of accounting information that, in the light of surrounding circumstances, makes it probable that the judgment of a reasonable user would have been changed**. |
| **Audit Risk (AR)** | **The risk that the auditor expresses an inappropriate audit opinion when the financial statements are materially misstated**. |
| **Inherent Risk (IR)** | **The susceptibility of an assertion to a material misstatement, assuming no related controls**. |
| **Control Risk (CR)** | **The risk that a material misstatement will not be prevented or detected and corrected on a timely basis by the entity’s internal control**. |
| **Detection Risk (DR)** | **The risk that the auditor’s procedures will not detect a material misstatement that exists**. |
| **Professional Skepticism** | **An attitude that includes a questioning mind and a critical assessment of audit evidence**. |
| **Working Papers** | **Documents that record audit procedures performed, evidence obtained, and conclusions reached**. |
| **Audit Opinion** | **A formal statement, expressed in the auditor’s report, on the financial statements**. |
| **Limited Assurance** | **An assurance engagement in which the practitioner obtains sufficient appropriate evidence to conclude that nothing has come to the auditor’s attention that causes the practitioner to believe that the subject matter is not in accordance with the criteria** (e.g., review engagements). |
| **Reasonable Assurance** | **A high, but not absolute, level of assurance** (e.g., audit engagements). |

> **Note:** Throughout the chapter, **bold** terms indicate **key concepts** that you must master for the CA exams.  

---  

## **15.3 Audit Planning & Risk Assessment**  

### 15.3.1 Objectives of Audit Planning  

1. **Obtain a thorough understanding of the entity and its environment** (including internal control).  
2. **Identify and assess risks of material misstatement** at the financial statement and assertion levels.  
3. **Develop an overall audit strategy** and a detailed audit plan that specifies nature, timing, and extent of procedures.  

### 15.3.2 The Audit Planning Process  

| Step | Activity | Typical Output |
|------|----------|----------------|
| 1 | **Engagement Acceptance & Continuance** – evaluate independence, competence, and client risk. | Engagement Letter |
| 2 | **Pre‑Engagement Activities** – obtain prior year audit files, understand the industry, regulatory environment. | Preliminary Risk Assessment Memo |
| 3 | **Understanding the Entity** – review business model, governance, accounting policies, and IT environment. | Entity Understanding Document |
| 4 | **Risk Identification** – use **brainstorming**, **questionnaires**, and **walk‑throughs**. | Risk Register |
| 5 | **Materiality Determination** – apply quantitative and qualitative thresholds (see 15.4). | Materiality Statement |
| 6 | **Audit Strategy Formulation** – decide on **substantive‑only**, **test‑of‑controls**, or **mixed** approach. | Audit Strategy Document |
| 7 | **Audit Plan Development** – schedule procedures, allocate staff, and set timelines. | Detailed Audit Program |

### 15.3.3 Risk Assessment Procedures  

- **Inquiry** of management and those charged with governance.  
- **Analytical procedures** (trend analysis, ratio analysis).  
- **Observation and inspection** of documents, policies, and internal controls.  
- **Walk‑throughs** of significant transactions from initiation to recording.  

> **Practical Tip:** For CA exams, always **link the identified risk to the specific audit response** (e.g., “high inherent risk in revenue recognition → increase substantive testing of cut‑off”).  

---  

## **15.4 Materiality & Performance Materiality**  

### 15.4.1 Quantitative Benchmarks  

| Benchmark | Typical % of Benchmark |
|-----------|------------------------|
| **Profit before tax (PBT)** | 5 % – 10 % |
| **Total assets** | 0.5 % – 2 % |
| **Revenue** | 0.5 % – 1 % |
| **Equity** | 1 % – 2 % |

**Example 15.1 – Determining Materiality**  

*Company XYZ* – FY 2025  

| Item | Amount (₹) |
|------|------------|
| Revenue | 1,200,00,000 |
| Profit before tax | 80,00,000 |
| Total assets | 5,000,00,000 |
| Equity | 2,500,00,000 |

1. **Revenue benchmark**: 1 % of 1,200,00,000 = **₹12,00,000**  
2. **PBT benchmark**: 5 % of 80,00,000 = **₹4,00,000**  
3. **Total assets benchmark**: 1 % of 5,000,00,000 = **₹50,00,000**  

**Materiality** is the **lowest** of the calculated amounts → **₹4,00,000** (based on PBT).  

### 15.4.2 Qualitative Considerations  

- **Regulatory non‑compliance** (e.g., violation of SEBI norms).  
- **Related‑party transactions**.  
- **Fraud risk** – even small misstatements may be material if they conceal fraud.  

### 15.4.3 Performance Materiality  

Performance materiality (PM) is set **lower than overall materiality** to reduce the risk that the aggregate of uncorrected and undetected misstatements exceeds materiality.  

A common rule of thumb:  

\[
\text{PM} = \text{Materiality} \times (1 - \text{Risk Adjustment Factor})
\]

Typical **Risk Adjustment Factor** = 20 % – 30 % for high‑risk engagements.  

**Example 15.2 – Performance Materiality**  

Using materiality of ₹4,00,000 and a risk adjustment factor of 25 %:  

\[
\text{PM} = 4,00,000 \times (1 - 0.25) = 4,00,000 \times 0.75 = \boxed{₹3,00,000}
\]

---  

## **15.5 Audit Evidence – Types & Gathering Techniques**  

### 15.5.1 Characteristics of Sufficient & Appropriate Evidence  

| Characteristic | Description |
|----------------|-------------|
| **Relevance** | Directly related to the assertion being tested. |
| **Reliability** | Depends on source (external > internal), nature (original documents > copies), and control environment. |
| **Timeliness** | Evidence must be for the period under audit. |
| **Objectivity** | Evidence should be free from bias. |

### 15.5.2 Sources of Evidence  

| Source | Typical Evidence | Reliability Rating* |
|--------|------------------|---------------------|
| **External** | Bank statements, supplier invoices, third‑party confirmations. | **High** |
| **Internal** | Ledger entries, internal reports, management representations. | **Medium** (unless corroborated) |
| **Physical** | Inspection of inventory, fixed assets. | **High** (if observed) |
| **Analytical** | Ratio analysis, trend analysis. | **Variable** (depends on underlying data) |

\*Reliability rating is a qualitative guide; auditors must exercise professional judgment.  

### 15.5.3 Evidence‑Gathering Techniques  

| Technique | When to Use | Key Points |
|-----------|-------------|------------|
| **Inspection** | Verify existence/valuation of assets. | Obtain original documents; note serial numbers. |
| **Observation** | Test controls (e.g., cash counts). | Document date, time, and persons observed. |
| **Inquiry** | Obtain explanations from management. | Follow up with corroborating evidence. |
| **Confirmation** | Verify balances with third parties (banks, customers). | Use **dual‑confirmation** for high‑risk items. |
| **Re‑performance** | Test the accuracy of calculations (e.g., depreciation). | Perform independently and compare. |
| **Analytical Procedures** | Identify unusual fluctuations. | Use statistical techniques where appropriate. |

---  

## **15.6 Audit Sampling – Theory & Application**  

### 15.6.1 Why Sampling?  

- **Cost‑effectiveness** – testing every transaction is impractical.  
- **Statistical inference** – allows auditors to draw conclusions about the population.  

### 15.6.2 Types of Sampling  

| Sampling Type | Description | When Preferred |
|---------------|-------------|----------------|
| **Statistical Sampling** | Uses probability theory to select items and evaluate results. | When a quantitative basis for conclusions is required (e.g., large populations). |
| **Non‑Statistical (Judgmental) Sampling** | Auditor selects items based on professional judgment. | When the population is small or when specific risk items are targeted. |

### 15.6.3 Key Statistical Concepts  

- **Population (N)** – total number of items.  
- **Sample size (n)** – number of items selected.  
- **Confidence Level (C)** – probability that the true error rate lies within the interval (commonly 95 %).  
- **Expected Error Rate (p)** – anticipated proportion of misstatements.  

**Sample Size Formula (for attribute sampling):**  

\[
n = \frac{Z^{2} \times p \times (1-p)}{E^{2}}
\]

where  

- \( Z \) = Z‑score corresponding to confidence level (e.g., 1.96 for 95 %).  
- \( E \) = tolerable error (expressed as a proportion).  

**Example 15.3 – Determining Sample Size**  

Audit of *Accounts Receivable* – 5,000 invoices. Auditor sets:  

- Confidence level = 95 % → \( Z = 1.96 \)  
- Expected error rate \( p = 2\% = 0.02 \)  
- Tolerable error \( E = 5\% = 0.05 \)  

\[
n = \frac{1.96^{2} \times 0.02 \times (1-0.02)}{0.05^{2}} = \frac{3.8416 \times 0.02 \times 0.98}{0.0025} \approx \frac{0.0753}{0.0025} = 30.1
\]

**Result:** **31 invoices** should be examined.  

### 15.6.4 Sampling Steps (Statistical)  

1. **Define the audit objective** (e.g., test existence of receiv

---

## Chapter 16: Corporate and Economic Laws: Governance, Contracts, and Insolvency

# **Chapter 16 – Corporate and Economic Laws: Governance, Contracts, & Insolvency**  
*(Ultimate Finance Textbook – CA‑Level)*  

---

## **Table of Contents**

| **Section** | **Topics Covered** |
|-------------|--------------------|
| 16.1 | **Corporate Governance** – legal framework, board structure, duties, ESG, compliance |
| 16.2 | **Contract Law** – formation, performance, breach, remedies, special contracts (sale, lease, agency) |
| 16.3 | **Insolvency & Bankruptcy** – concepts, processes, liquidation, re‑organisation, priority of claims |
| 16.4 | **Financial Implications & Ratios** – governance impact on valuation, contract risk, insolvency metrics |
| 16.5 | **Exam‑Style Problems & Step‑by‑Step Solutions** – CA‑Final & IPCC level |
| 16.6 | **Key Statutes, Case Laws & References** |
| 16.7 | **Quick Revision Checklist** |

---

## **16.1 Corporate Governance**

### 16.1.1 What is Corporate Governance?

> **Corporate Governance** – *the system of rules, practices and processes by which a company is directed and controlled, balancing the interests of shareholders, management, customers, suppliers, financiers, government and the community.*

---

### 16.1.2 Legal Framework (India)

| **Statute / Regulation** | **Key Provisions** |
|--------------------------|--------------------|
| **Companies Act, 2013** (Sec. 149‑153) | Board composition, independent directors, audit committee, nomination & remuneration committee. |
| **SEBI (Listing Obligations & Disclosure Requirements) Regulations, 2015** | Corporate governance disclosures for listed entities. |
| **Corporate Governance Code (ICAI)** | Ethical standards, professional conduct for chartered accountants. |
| **Companies (Amendment) Act, 2020** | Mandatory ESG disclosures for certain classes of companies. |
| **Insolvency and Bankruptcy Code (IBC), 2016** | Governance implications during distress. |

---

### 16.1.3 Board Structure & Duties  

| **Component** | **Description** |
|---------------|-----------------|
| **Board of Directors** | Ultimate decision‑making body. Must act **in good faith**, **with due diligence**, and **in the best interests of the company**. |
| **Independent Directors (ID)** | Minimum 1/3rd of the board for listed companies; provide unbiased oversight. |
| **Audit Committee (AC)** | Oversees financial reporting, internal controls, auditor independence. |
| **Nomination & Remuneration Committee (NRC)** | Recommends appointments, remuneration policies. |
| **Stakeholder Committee (SC)** – *new under the 2020 amendment* | Represents minority shareholders, employees, and other stakeholders. |

#### **Directors’ Statutory Duties** (Sec. 166, Companies Act, 2013)

| **Duty** | **Explanation** |
|----------|-----------------|
| **Duty of Care** | Exercise **reasonable skill, knowledge and diligence**. |
| **Duty of Loyalty** | Avoid **conflict of interest**; act **in good faith** for the company. |
| **Duty to Act Within Powers** | Follow the **memorandum** and **articles of association**. |
| **Duty to Avoid Misuse of Information** | No insider trading or misuse of confidential data. |
| **Duty to Disclose Interests** | Disclose any **direct/indirect interest** in any contract/arrangement with the company (Sec. 184). |

> **Note:** Breach of any duty attracts **civil liability** (personal liability for damages) and **criminal penalties** (up to 7 years imprisonment & fine).

---

### 16.1.4 ESG – Environmental, Social, Governance  

| **Component** | **Key Reporting Requirement** |
|---------------|------------------------------|
| **Environmental** | Carbon emissions, water usage, waste management (mandatory for listed entities with turnover > ₹5,000 crore). |
| **Social** | Labor practices, community engagement, diversity & inclusion. |
| **Governance** | Board diversity, anti‑corruption policies, whistle‑blower mechanisms. |

**Formula – ESG Score Normalisation**  

\[
\text{ESG}_{\text{Score}} = \frac{\displaystyle\sum_{i=1}^{n} w_i \times s_i}{\displaystyle\sum_{i=1}^{n} w_i}
\]

where  

- \(w_i\) = weight assigned to each pillar (E, S, G)  
- \(s_i\) = normalized sub‑score (0‑100).  

*Example:* A company assigns 40% weight to E, 30% to S, 30% to G. Scores: E = 70, S = 80, G = 60.  

\[
\text{ESG}_{\text{Score}} = \frac{0.4\times70 + 0.3\times80 + 0.3\times60}{0.4+0.3+0.3}= \frac{28+24+18}{1}=70
\]

---

### 16.1.5 Compliance & Penalties  

| **Violation** | **Statutory Penalty** |
|---------------|-----------------------|
| Failure to appoint **Independent Directors** | Fine up to **₹5 lakh** per day of default (Sec. 149). |
| Non‑disclosure of **related party transactions** | **₹10 lakh** fine + **imprisonment up to 2 years** (Sec. 188). |
| Breach of **ESG reporting** (post‑2022) | **₹1 crore** per default & possible **de‑listing**. |
| **Insider trading** (Securities Law) | **₹5 crore** fine & **up to 10 years** imprisonment. |

---

### 16.1.6 Governance Impact on Valuation  

**Adjusted Discounted Cash Flow (ADDCF) Model** – incorporates governance premium.

\[
V = \sum_{t=1}^{n} \frac{FCF_t}{(1 + WACC + GP)^t}
\]

- \(GP\) = **Governance Premium** (basis points added to WACC).  
- Empirical studies suggest **GP = 0.5% – 1.5%** for companies with weak governance.

*Illustrative Example:*  

- Base WACC = 10%  
- Governance premium (weak) = 1.2% → Adjusted discount rate = 11.2%  
- Projected free cash flows (FCF) for 5 years: ₹120, ₹130, ₹140, ₹150, ₹160 crore.  

\[
V = \frac{120}{1.112} + \frac{130}{1.112^2} + \dots + \frac{160}{1.112^5} = ₹ 617.3 \text{ crore}
\]

If governance improves (GP = 0.4%), the valuation rises to **₹ 658.9 crore**, illustrating the financial benefit of robust governance.

---

## **16.2 Contract Law**

### 16.2.1 Definition  

> **Contract** – *a legally enforceable agreement between two or more parties, creating mutual obligations, enforceable by law.*

---

### 16.2.2 Essential Elements (Indian Contract Act, 1872)

| **Element** | **Explanation** |
|-------------|-----------------|
| **Offer** | Clear, communicated intention to be bound on certain terms. |
| **Acceptance** | Unconditional assent to the offer (must be communicated unless the offer is *unilateral*). |
| **Consideration** | Something of value exchanged; must be **lawful** and **real**. |
| **Intention to Create Legal Relations** | Commercial contracts presumed to have this intention. |
| **Capacity** | Parties must be **competent** (age ≥ 18, sound mind, not disqualified). |
| **Free Consent** | No **coercion**, **undue influence**, **fraud**, **misrepresentation**, or **mistake**. |
| **Lawful Object** | Object must not be illegal, immoral, or opposed to public policy. |

---

### 16.2.3 Types of Contracts  

| **Category** | **Key Features** |
|--------------|-----------------|
| **Bilateral** | Mutual promises (e.g., sale of goods). |
| **Unilateral** | Promise in exchange for an act (e.g., reward). |
| **Executed** | Both parties have performed. |
| **Executory** | Performance is pending. |
| **Void** | No legal effect (e.g., illegal object). |
| **Voidable** | Valid until rescinded (e.g., contracts with minors). |
| **Unenforceable** | Valid but cannot be enforced (e.g., statute of limitations). |

---

### 16.2.4 Performance & Discharge  

| **Mode of Discharge** | **Explanation** |
|-----------------------|-----------------|
| **Performance** | Complete fulfillment of obligations. |
| **Agreement** | *Novation*, *accord & satisfaction*, *substituted performance*. |
| **Impossibility** | Performance becomes *illegal* or *physically impossible*. |
| **Lapse of Time** | *Prescription* under Limitation Act, 1963. |
| **Operation of Law** | *Bankruptcy*, *death*, *merger*. |

---

### 16.2.5 Breach & Remedies  

| **Remedy** | **When Applied** | **Key Formula / Computation** |
|------------|------------------|-------------------------------|
| **Damages – Compensatory** | Ordinary breach. | \(\text{Damages} = \text{Loss suffered} - \text{Gain avoided}\) |
| **Specific Performance** | Contracts involving *unique* subject matter (e.g., real estate). |
| **Injunction** | To prevent *continuing* breach. |
| **Rescission** | *Misrepresentation* or *undue influence*. |
| **Quantum Meruit** | When contract is void but services rendered. |
| **Penalty Clause** | Enforceable only if *reasonable* (Sec. 74). |

**Formula – Liquidated Damages (LD) vs. Penalty Test**  

\[
\text{LD is enforceable if } \frac{\text{LD}}{\text{Contract Price}} \leq \theta
\]

where \(\theta\) is the **reasonable estimate** (generally 10‑15% for service contracts). If LD > \(\theta\), it is treated as a **penalty** and may be reduced by the court.

*Example:* Contract price = ₹10,00,000. Liquidated damages stipulated = ₹2,00,000 (20%). Court may deem it excessive and reduce to 12% (₹1,20,000).

---

### 16.2.6 Special Contracts  

#### 16.2.6.1 Sale of Goods (Sale of Goods Act, 1930)

- **Transfer of ownership** occurs when parties intend it (Sec. 18).  
- **Risk** passes with ownership unless otherwise agreed.  

**Formula – Cost‑plus Pricing**  

\[
\text{Selling Price} = \text{Cost Price} + (\text{Cost Price} \times \text{Markup\%})
\]

*Illustration:* Cost = ₹500 per unit, markup = 25% → SP = ₹500 + (0.25×₹500) = ₹625.

#### 16.2.6.2 Lease (Transfer of Property Act, 1882)

- **Lease term** must be expressed in years/months; otherwise, it is a **monthly tenancy**.  

**Formula – Lease Liability (IFRS 16)**  

\[
\text{Liability}_{0} = \sum_{t=1}^{n} \frac{R_t}{(1+r)^t}
\]

where \(R_t\) = lease payment in year *t*, \(r\) = discount rate.

*Example:* Annual lease ₹12 lakh for 5 years, discount rate 8%:  

\[
\text{Liability}_{0}= \frac{12}{1.08}+\frac{12}{1.08^2}+...+\frac{12}{1.08^5}= ₹48.2 \text{ lakh}
\]

#### 16.2.6.3 Agency (Indian Contract Act, 1872)

- **Principal‑Agent relationship** creates fiduciary duties.  
- **Authority** can be *actual*, *implied*, or *apparent*.  

**Key Formula – Agency Commission**  

\[
\text{Commission} = \text{Transaction Value} \times \text{Commission Rate}
\]

*Example:* Agent sells machinery worth ₹2 crore at 2% commission → Commission = ₹4 lakh.

---

### 16.2.7 International Contracts – UNCITRAL Principles  

| **Principle** | **Implication for Indian Companies** |
|---------------|--------------------------------------|
| **Good Faith** | Must act honestly in performance & enforcement. |
| **Force Majeure** | Clause must be *specific*; Indian courts interpret narrowly. |
| **Choice of Law** | Parties may select foreign law, but Indian courts may apply **public policy** test. |

---

## **16.3 Insolvency & Bankruptcy**

### 16.3.1 Core Definitions  

| **Term** | **Definition** |
|----------|----------------|
| **Insol

---

## Chapter 17: Strategic Financial Management and Risk Mitigation

# **Chapter 17 – Strategic Financial Management & Risk Mitigation**  
*Ultimate Finance Textbook – CA‑Level Edition*  

---  

## **Table of Contents**  

| **Section** | **Pages** |
|-------------|-----------|
| 17.1 Introduction to Strategic Financial Management | 1 |
| 17.2 The Strategic Financial Planning Process | 3 |
| 17.3 Capital Structure & Value Creation | 7 |
| 17.4 Dividend Policy – Theory & Practice | 13 |
| 17.5 Working‑Capital Management as a Strategic Tool | 18 |
| 17.6 Risk Landscape: Identification & Classification | 24 |
| 17.7 Quantitative Risk Measurement | 28 |
| 17.8 Risk‑Mitigation Instruments & Strategies | 36 |
| 17.9 Integrated Risk Management (IRM) Framework | 44 |
| 17.10 Corporate Governance & Risk Culture | 51 |
| 17.11 Real‑World Case Studies | 56 |
| 17.12 CA‑Level Exam‑Style Problems & Step‑by‑Step Solutions | 64 |
| 17.13 Summary & Key Take‑aways | 78 |
| 17.14 Suggested Further Reading | 80 |

---  

## 17.1 Introduction to Strategic Financial Management  

Strategic Financial Management (SFM) is the **systematic alignment of a firm’s financial decisions with its long‑term business strategy**. It goes beyond day‑to‑day budgeting, integrating capital allocation, risk appetite, and value‑creation objectives into a coherent roadmap.

> **Strategic Financial Management (SFM)** – *The process of formulating, implementing, and monitoring financial policies and decisions that support an organization’s overall strategic goals, while balancing risk and return.*

### Why SFM Matters for CA Professionals  

* **Value‑Based Decision Making** – CA’s are expected to advise on actions that maximize shareholder wealth, not just compliance.  
* **Risk‑Adjusted Performance** – Modern stakeholders demand that risk be quantified and embedded in performance metrics (e.g., EVA, RAROC).  
* **Regulatory Landscape** – Basel III, IFRS 9, and the Companies Act 2013 (India) require robust risk‑management disclosures.  

---

## 17.2 The Strategic Financial Planning Process  

### 17.2.1 Steps in the SFP Cycle  

| **Step** | **Objective** | **Key Outputs** |
|----------|---------------|-----------------|
| **1. Vision & Mission Alignment** | Translate corporate vision into financial aspirations. | Long‑term financial targets (e.g., 10‑yr ROE ≥ 15%). |
| **2. Environmental Scanning** | Identify macro‑economic, industry, and competitive forces. | PESTEL & Porter’s Five‑Force analysis. |
| **3. Financial Goal Setting** | Set measurable, time‑bound objectives (growth, profitability, liquidity). | KPI matrix, Balanced Scorecard. |
| **4. Strategy Formulation** | Choose growth, stability, or retrenchment strategies and the financing mix. | Strategic options matrix, Capital budgeting shortlist. |
| **5. Resource Allocation** | Allocate capital to projects using NPV, IRR, and risk‑adjusted discount rates. | Capital budget, Funding plan. |
| **6. Implementation & Control** | Execute and monitor; adjust for variances. | Variance analysis, Rolling forecasts. |

### 17.2.2 Integrated Financial Model (IFM)  

A **dynamic spreadsheet model** that links the three core statements (P&L, Balance Sheet, Cash Flow) with strategic levers (capacity, pricing, cost structure).  

**Key equations** (simplified):  

\[
\begin{aligned}
\text{Revenue}_t &= \text{Price}_t \times \text{Quantity}_t \\
\text{EBIT}_t &= \text{Revenue}_t - \text{COGS}_t - \text{SG\&A}_t \\
\text{NOPAT}_t &= \text{EBIT}_t \times (1 - \tau) \\
\text{FCFF}_t &= \text{NOPAT}_t + \text{Depreciation}_t - \Delta \text{WC}_t - \text{CapEx}_t \\
\text{Equity Value} &= \sum_{t=1}^{n} \frac{\text{FCFF}_t}{(1+WACC)^t} + \frac{\text{Terminal Value}}{(1+WACC)^n}
\end{aligned}
\]

> **WACC** – *Weighted Average Cost of Capital, the discount rate that reflects the firm’s blended cost of debt and equity.*

---

## 17.3 Capital Structure & Value Creation  

### 17.3.1 Theoretical Foundations  

| Theory | Core Proposition | Implication for Capital Structure |
|--------|------------------|-----------------------------------|
| **Modigliani‑Miller (MM) Proposition I (No Taxes)** | Firm value is independent of leverage. | No optimal debt‑equity mix. |
| **MM Proposition II (With Taxes)** | Debt provides a tax shield: \(V_L = V_U + T_c D\). | Leverage increases value up to the point where bankruptcy costs outweigh tax benefits. |
| **Trade‑Off Theory** | Firms balance tax shields against financial distress costs. | Existence of an optimal debt ratio \(D^*\). |
| **Pecking‑Order Theory** | Firms prefer internal financing, then debt, then equity. | Capital structure is a by‑product of financing needs, not a target. |
| **Market Timing Theory** | Firms issue equity when market valuations are high. | Capital structure fluctuates with market conditions. |

### 17.3.2 Quantitative Determination of Optimal Leverage  

**Step‑by‑Step Method (CA‑Level)**  

1. **Estimate the Tax Shield Benefit**  

   \[
   \text{Tax Shield} = T_c \times r_d \times D
   \]

2. **Estimate Expected Bankruptcy Cost (EBC)**  

   \[
   \text{EBC} = \frac{1}{2} \times \lambda \times D^2
   \]  

   where \(\lambda\) is the **cost‑of‑distress coefficient** (derived from historical default data).  

3. **Set up the Value‑Maximization Condition**  

   \[
   \frac{dV}{dD} = T_c r_d - \lambda D = 0 \quad \Rightarrow \quad D^* = \frac{T_c r_d}{\lambda}
   \]

4. **Compute the Optimal Debt‑to‑Equity Ratio**  

   \[
   \frac{D^*}{E^*} = \frac{D^*}{V - D^*}
   \]

#### **Illustrative Example**  

*Company XYZ* – Indian manufacturing firm  

| Parameter | Value |
|-----------|-------|
| Corporate tax rate (\(T_c\)) | 25 % |
| Pre‑tax cost of debt (\(r_d\)) | 8 % |
| Cost‑of‑distress coefficient (\(\lambda\)) | 0.04 |

**Solution**  

\[
\begin{aligned}
D^* &= \frac{0.25 \times 0.08}{0.04} = \frac{0.02}{0.04}=0.5 \text{ (₹ bn)}\\
\text{Assume total firm value } V = ₹ 5\text{ bn} \\
E^* &= V - D^* = 5 - 0.5 = ₹ 4.5\text{ bn}\\
\frac{D^*}{E^*} &= \frac{0.5}{4.5}=0.111\; \text{or } 11.1\%
\end{aligned}
\]

**Interpretation:** XYZ should target a **debt ratio of ~11 %** to maximize value, given its tax shield and distress cost assumptions.

### 17.3.3 Practical Considerations  

* **Industry‑specific leverage norms** – e.g., utilities (high) vs. technology (low).  
* **Regulatory caps** – RBI’s Basel III capital adequacy for banks.  
* **Cash‑flow stability** – firms with volatile cash flows should keep debt lower.  

---

## 17.4 Dividend Policy – Theory & Practice  

### 17.4.1 Core Concepts  

| Concept | Definition | Formula |
|---------|------------|---------|
| **Dividend Payout Ratio** | Proportion of earnings paid as dividends. | \(\text{Payout} = \frac{Dividends}{Net\;Income}\) |
| **Dividend Yield** | Return to shareholders from dividends relative to market price. | \(\text{Yield} = \frac{Dividends\;per\;share}{Share\;price}\) |
| **Residual Dividend Model** | Pay dividends from earnings left after funding all positive‑NPV projects. | \(Div = \max\{0, \; Earnings - \text{Capital\;Budget}\}\) |

### 17.4.2 Theories  

* **Bird‑in‑the‑Hand Theory** – Investors prefer certain dividends over uncertain capital gains.  
* **Tax Preference Theory** – In jurisdictions where dividend tax > capital‑gain tax, investors prefer lower payouts.  
* **Agency Theory** – Dividends reduce free cash flow, limiting managerial over‑investment.  

### 17.4.3 Dividend Decision Framework (CA‑Level)  

1. **Forecast Earnings** for the next 3‑5 years.  
2. **Identify Required Capital Expenditure (CapEx)** and **Working‑Capital Needs**.  
3. **Compute Residual Earnings**:  

   \[
   \text{Residual} = \text{Forecasted Earnings} - \text{(CapEx + ΔWC)}
   \]  

4. **Set Target Payout Ratio** based on industry norms and shareholder expectations.  
5. **Adjust for Signalling** – If the firm wants to signal confidence, it may increase payout temporarily.  

#### **Numerical Example**  

*Company ABC* – Indian IT services firm  

| Year | Forecasted Net Income (₹ mn) | CapEx (₹ mn) | ΔWC (₹ mn) |
|------|------------------------------|-------------|-----------|
| 2024 | 1,200 | 150 | 30 |
| 2025 | 1,350 | 180 | 35 |
| 2026 | 1,500 | 200 | 40 |

**Step 1 – Residual Earnings**  

\[
\begin{aligned}
\text{2024 Residual} &= 1,200 - (150+30) = 1,020 \\
\text{2025 Residual} &= 1,350 - (180+35) = 1,135 \\
\text{2026 Residual} &= 1,500 - (200+40) = 1,260
\end{aligned}
\]

Assume target payout ratio = **30 %**.  

**Dividends**  

\[
\begin{aligned}
\text{Div}_{2024} &= 0.30 \times 1,020 = ₹ 306\text{ mn} \\
\text{Div}_{2025} &= 0.30 \times 1,135 = ₹ 340.5\text{ mn} \\
\text{Div}_{2026} &= 0.30 \times 1,260 = ₹ 378\text{ mn}
\end{aligned}
\]

**Result:** The dividend policy is **residual‑based**, ensuring all value‑creating projects are funded first.

---

## 17.5 Working‑Capital Management as a Strategic Tool  

### 17.5.1 Components & Definitions  

| Component | **Definition** | Typical Management Objective |
|-----------|----------------|------------------------------|
| **Cash** | Liquid assets held for day‑to‑day transactions. | Minimize idle cash while avoiding liquidity shortfalls. |
| **Accounts Receivable (A/R)** | Amounts owed by customers. | Reduce collection period (Days Sales Outstanding – DSO). |
| **Inventory** | Raw materials, work‑in‑process, finished goods. | Optimize turnover (Days Inventory Outstanding – DIO). |
| **Accounts Payable (A/P)** | Amounts owed to suppliers. | Extend payment period (Days Payable Outstanding – DPO) without harming supplier relations. |

**Cash Conversion Cycle (CCC)**  

\[
\text{CCC} = \text{DSO} + \text{DIO} - \text{DPO}
\]

### 17.5.2 Quantitative Optimization – The **Operating Cycle Model**  

**Goal:** Minimize **Net Working Capital (NWC)** while maintaining service levels.

\[
\text{NWC} = \text{A/R} + \text{Inventory} - \text{A/P}
\]

**Step‑by‑Step Approach**  

1. **Calculate Current Ratios**  

   \[
   \text{DSO} = \frac{\text{A/R}}{\text{Credit Sales}} \times 365
   \]  

   \[
   \text{DIO} = \frac{\text{Inventory}}{\text{COGS}} \times 365
   \]  

   \[
   \text{DPO} = \frac{\text{A/P}}{\text{Purchases}} \times 365
   \]  

2. **Set Target Benchmarks** (industry averages).  

3

---

## Chapter 18: Macroeconomics, Monetary Policy, and International Finance

# Chapter 18 – Macroeconomics, Monetary Policy, and International Finance  

*Prepared for CA‑Final / CMA / CPA aspirants – a definitive study guide*  

---

## Table of Contents  

| # | Section |
|---|---------|
| 18.1 | **Macroeconomic Foundations** |
| 18.2 | **Aggregate Demand & Aggregate Supply (AD‑AS) Model** |
| 18.3 | **IS‑LM Framework (Closed‑Economy)** |
| 18.4 | **Monetary Policy: Instruments & Transmission** |
| 18.5 | **Inflation, Phillips Curve & Expectations** |
| 18.6 | **Open‑Economy Macroeconomics** |
| 18.7 | **Exchange‑Rate Determination** |
| 18.8 | **Balance of Payments (BoP) & Capital Flows** |
| 18.9 | **Mundell‑Fleming Model & Policy Trilemma** |
| 18.10 | **Foreign‑Exchange Intervention & Sterilisation** |
| 18.11 | **Advanced CA‑Level Problem Solving** |
| 18.12 | **Key Take‑aways & Quick Revision Checklist** |
| 18.13 | **Practice Questions & Answers** |

---  

## 18.1 Macroeconomic Foundations  

### 18.1.1 Definition Box  

| Term | Definition |
|------|------------|
| **Macroeconomics** | The branch of economics that studies the behaviour of an economy as a whole – aggregate output, employment, price level, and the interaction of fiscal and monetary policies. |
| **Monetary Policy** | The set of actions undertaken by a country’s central bank to influence the quantity of money and the cost of credit (interest rates) in order to achieve macro‑economic objectives such as price stability, full employment, and sustainable growth. |
| **Fiscal Policy** | Government decisions on taxation and public expenditure aimed at influencing aggregate demand, output, and employment. |
| **Policy Objectives** | **(i)** Price stability (inflation target), **(ii)** Economic growth (real GDP), **(iii)** Full employment, **(iv)** External balance, **(v)** Financial stability. |

> **Note:** In the Indian context, the Reserve Bank of India (RBI) follows a **flexible inflation targeting** framework (target 4 % ± 2 %).  

---

## 18.2 Aggregate Demand & Aggregate Supply (AD‑AS) Model  

### 18.2.1 Aggregate Demand (AD)  

\[
\boxed{AD = C(Y - T) + I(r) + G + NX(e)}
\]

* **C** – Consumption, a function of disposable income \(Y - T\).  
* **I** – Investment, negatively related to the real interest rate \(r\).  
* **G** – Government expenditure (exogenous).  
* **NX** – Net exports, a function of the real exchange rate \(e\) (price of foreign currency in terms of domestic currency).  

#### Real‑World Example (India, FY 2024‑25)  

| Component | Value (₹ bn) |
|-----------|--------------|
| Consumption (C) | 150,000 |
| Investment (I) | 45,000 |
| Government spending (G) | 30,000 |
| Net exports (NX) | –5,000 |
| **AD** | **220,000** |

> The negative NX reflects a trade deficit, pulling AD down.

### 18.2.2 Aggregate Supply (AS)  

Two regimes are distinguished:

| Regime | Short‑Run AS (SRAS) | Long‑Run AS (LRAS) |
|--------|---------------------|--------------------|
| **Keynesian** | Upward‑sloping; price level influences output via sticky wages. | Vertical at potential output \(Y^{*}\). |
| **Classical** | Horizontal at full‑employment; output fixed, price adjusts. | Same vertical LRAS. |

**SRAS equation (Keynesian):**  

\[
\boxed{Y = Y^{*} + \alpha (P - P^{e})}
\]

where \(P\) is the actual price level, \(P^{e}\) expected price level, and \(\alpha>0\) measures price‑wage rigidity.

### 18.2.3 Policy Implications  

* **Expansionary monetary policy** → lowers \(r\) → raises \(I\) → shifts AD right.  
* **Supply‑side reforms** (e.g., labor market flexibility) → shift LRAS right, reducing inflationary pressure.

---

## 18.3 IS‑LM Framework (Closed‑Economy)  

### 18.3.1 Deriving the IS Curve  

The **goods market equilibrium** condition:

\[
Y = C(Y - T) + I(r) + G
\]

Assume linear forms:  

\[
C = c_{0} + c_{1}(Y - T),\qquad I = i_{0} - i_{1}r
\]

Plugging in and solving for \(Y\) as a function of \(r\):

\[
\boxed{Y = \frac{1}{1-c_{1}}\big[ c_{0} - c_{1}T + i_{0} - i_{1}r + G \big]}
\]

The **IS curve** is downward sloping in \((Y,r)\) space because a higher \(r\) reduces investment and output.

### 18.3.2 Deriving the LM Curve  

Money market equilibrium:

\[
\frac{M}{P} = L(r,Y)
\]

Assume linear money‑demand:  

\[
L = kY - hr
\]

Thus:

\[
\boxed{r = \frac{k}{h}Y - \frac{M}{hP}}
\]

The **LM curve** is upward sloping: higher income raises money demand, pushing up the interest rate for a given money supply.

### 18.3.3 Equilibrium  

Solve the two equations simultaneously.  

**Example (CA‑Level):**  

Given:  

* \(c_{0}=50\), \(c_{1}=0.6\)  
* \(i_{0}=30\), \(i_{1}=10\)  
* \(G=100\), \(T=40\)  
* Money supply \(M=500\), price level \(P=2\)  
* Money‑demand parameters: \(k=0.5\), \(h=20\)  

**Step‑by‑step:**  

1. **IS equation**  

\[
Y = \frac{1}{1-0.6}\big[50 - 0.6(40) + 30 - 10r + 100\big]  
= \frac{1}{0.4}\big[50 - 24 + 30 - 10r + 100\big]  
= 2.5\big[156 - 10r\big] = 390 - 25r
\]

2. **LM equation**  

\[
r = \frac{k}{h}Y - \frac{M}{hP}= \frac{0.5}{20}Y - \frac{500}{20\times2}=0.025Y - 12.5
\]

3. **Substitute LM into IS:**  

\[
Y = 390 - 25\big(0.025Y - 12.5\big) = 390 - 0.625Y + 312.5
\]

\[
Y + 0.625Y = 702.5 \;\Rightarrow\; 1.625Y = 702.5 \;\Rightarrow\; Y^{*}=432.3
\]

4. **Find equilibrium \(r^{*}\):**  

\[
r^{*}=0.025(432.3)-12.5 = 10.81 - 12.5 = -1.69\%
\]

A negative equilibrium rate signals that the assumed parameters are inconsistent with a realistic economy; the central bank would need to **raise the money supply** or **lower taxes** to obtain a positive rate. This illustrates the diagnostic power of the IS‑LM model.

---

## 18.4 Monetary Policy: Instruments & Transmission  

### 18.4.1 Core Instruments  

| Instrument | Mechanism | Typical CA‑Exam Focus |
|------------|-----------|-----------------------|
| **Open‑Market Operations (OMO)** | Buying/selling government securities changes bank reserves → alters money supply. | Compute change in money supply using the **money multiplier**. |
| **Reserve Requirement (RR)** | Mandatory fraction of deposits banks must hold. | \(\displaystyle m = \frac{1}{RR}\). |
| **Discount (Repo) Rate** | Rate at which banks borrow from the central bank. | Impact on short‑term market rates. |
| **Statutory Liquidity Ratio (SLR)** | Minimum liquid assets (govt securities) banks must hold. | Often used in Indian exam questions. |
| **Foreign‑Exchange Intervention** | Buying/selling foreign currency to influence the exchange rate. | Interaction with sterilisation. |

### 18.4.2 Money Multiplier  

\[
\boxed{m = \frac{1}{RR + \theta}}
\]

where \(\theta\) captures **currency‑to‑deposit ratio** (public’s preference for cash).  

**Numerical Example (India, 2023):**  

* Required RR = 4 % → \(RR = 0.04\)  
* Currency‑deposit ratio \(\theta = 0.15\)  

\[
m = \frac{1}{0.04 + 0.15}= \frac{1}{0.19}=5.26
\]

If RBI injects ₹ 100 bn via OMO, the **potential increase in broad money (M2)** is  

\[
\Delta M = m \times \Delta \text{Base Money}=5.26 \times 100 = ₹ 526\text{ bn}
\]

### 18.4.3 Transmission Channels  

| Channel | Description | Key Indicator |
|---------|-------------|---------------|
| **Interest‑Rate Channel** | Policy rate → market rates → consumption & investment. | Yield curve, repo rate. |
| **Credit (Bank‑Lending) Channel** | Changes in banks’ reserves affect loan supply. | Credit‑to‑GDP ratio. |
| **Exchange‑Rate Channel** | Lower rates → capital outflow → depreciation → net‑exports rise. | Real effective exchange rate (REER). |
| **Asset‑Price Channel** | Lower rates boost equity & housing prices → wealth effect. | Stock market index, house price index. |
| **Expectations Channel** | Forward guidance shapes agents’ expectations of future rates. | Survey‑based inflation expectations. |

---

## 18.5 Inflation, Phillips Curve & Expectations  

### 18.5.1 The Phillips Curve  

**Original (static) form:**  

\[
\boxed{\pi_t = \pi_t^{e} - \beta (u_t - u_n)}
\]

* \(\pi_t\) – actual inflation, \(\pi_t^{e}\) – expected inflation.  
* \(u_t\) – unemployment rate, \(u_n\) – natural rate of unemployment.  
* \(\beta>0\) – slope (trade‑off strength).  

**Expectations‑augmented (rational) form:**  

\[
\pi_t = \pi_t^{e} - \beta (u_t - u_n) \quad\text{with}\quad \pi_t^{e}=E_t[\pi_{t+1}]
\]

When expectations are anchored (e.g., by credible inflation targeting), the **long‑run Phillips curve

---

## Chapter 19: Chartered Accountant (CA) Case Studies and Complex Problem Solving Methods

# Chapter 19 – Chartered Accountant (CA) Case Studies & Complex Problem‑Solving Methods  

> **Purpose:** This chapter equips you with a systematic, exam‑ready approach to tackling the most demanding CA‑level case studies. You will learn how to dissect a problem, apply the appropriate accounting standards, and present a polished, professional solution that earns full marks.  

> **How to Use This Chapter**  
> 1. **Read** the theory and methodology sections first.  
> 2. **Study** each case study – note the data, identify the required outputs, and follow the step‑by‑step solution.  
> 3. **Practice** the self‑assessment questions at the end; compare your answer with the model solution.  
> 4. **Create** your own “mini‑case” using the quick‑reference tables for rapid revision before exams.  

---

## 19.1  Introduction – Why Case Studies Matter  

CA examinations test **application** more than recall. Real‑world business decisions are rarely isolated; they involve:

* **Multiple accounting standards** (e.g., IFRS 15, IAS 12, Ind AS 115).  
* **Cross‑functional implications** (tax, audit, finance, management accounting).  
* **Quantitative analysis** (NPV, EVA, variance analysis).  

A well‑structured case study demonstrates:

* **Analytical rigor** – identifying relevant facts, assumptions, and constraints.  
* **Technical competence** – correct calculations, journal entries, and disclosures.  
* **Professional judgement** – applying the “best practice” approach where standards allow choice.  

---

## 19.2  The CA Problem‑Solving Framework  

| Step | Action | What to Look For | Tips for Full Marks |
|------|--------|------------------|---------------------|
| **1. Read & Highlight** | Scan the entire question; underline key figures, dates, and required outputs. | • Time‑frames (e.g., “as of 31 Dec 2025”) <br>• Specific standards referenced | Use a consistent colour code (e.g., red for dates, blue for amounts). |
| **2. Identify the Scope** | List all topics involved (e.g., **Consolidation**, **Deferred Tax**, **Audit Risk**). | • Multiple standards → need a **matrix** of applicability. | Write a short “Scope Table” before calculations. |
| **3. Gather Assumptions** | State any assumptions you make (e.g., tax rate constant, market price stable). | • Missing data → reasonable industry‑average. | Explicitly state assumptions; examiners award marks for transparency. |
| **4. Choose the Methodology** | Select the appropriate analytical tool (e.g., **Horizontal Analysis**, **DCF**, **Variance Analysis**). | • Nature of the problem (valuation → DCF; cost control → variance). | Mention the name of the method and why it fits. |
| **5. Perform Calculations** | Execute step‑by‑step calculations, showing all intermediate figures. | • Use **LaTeX** or clear handwritten work for formulas. | Keep a **working column**; round only at the final answer. |
| **6. Prepare Journal Entries / Disclosures** | Draft the required accounting entries and note the related disclosures. | • IFRS/Ind AS requirement (e.g., **IAS 12** for deferred tax). | Use proper **debit/credit** format and reference the standard. |
| **7. Analyse & Interpret** | Explain the significance of the result (e.g., “NPV > 0 → accept”). | • Link back to business decision. | Use **bold** for key conclusions. |
| **8. Review** | Cross‑check totals, ensure all parts of the question are answered. | • Missing a sub‑question = loss of marks. | Use a checklist at the end of your answer. |

> **Pro‑Tip:** In the exam, allocate **10 %** of your time to **planning** (Steps 1‑3). This prevents costly re‑work later.

---

## 19.3  Case Study 1 – Consolidated Financial Statements (Ind AS 110)

### 19.3.1  Scenario  

**Parent Co.** (P) acquired **80 %** of the voting rights of **Subsidiary Ltd.** (S) on **1 April 2024** for **₹150 million**. The fair value of S’s identifiable net assets at acquisition was **₹120 million** (including a **₹10 million** fair‑value uplift on plant, depreciated over 5 years on a straight‑line basis).  

During the year ending **31 Mar 2025**, the following data are available (all figures in ₹ million):  

| Item | Parent (P) | Subsidiary (S) |
|------|------------|----------------|
| Revenue | 500 | 200 |
| Cost of Goods Sold | 300 | 120 |
| Operating Expenses | 80 | 40 |
| Depreciation (carrying) | 30 | 20 |
| Interest Expense | 15 | 10 |
| Tax Expense (current) | 25 | 12 |
| Dividend received from S | 8 | – |
| Closing cash balance | 70 | 30 |

Additional information:  

* The **non‑controlling interest (NCI)** is 20 % of S’s equity.  
* The **effective tax rate** is 30 % (applied to profit before tax).  
* No intra‑group transactions occurred.  

**Required:**  

1. Prepare the **Consolidated Statement of Profit or Loss** for the year ended 31 Mar 2025.  
2. Compute the **Consolidated Statement of Financial Position** (selected items only).  
3. Show the **goodwill** arising on acquisition and test it for impairment (assume no impairment).  

---

### 19.3.2  Step‑by‑Step Solution  

#### **Step 1 – Compute Goodwill**  

\[
\text{Goodwill} = \underbrace{\text{Consideration transferred}}_{\text{₹150m}} 
+ \underbrace{\text{NCI at fair value}}_{\text{20 % × ₹120m = ₹24m}} 
- \underbrace{\text{Fair value of identifiable net assets}}_{\text{₹120m}}
\]

\[
\boxed{\text{Goodwill} = ₹150m + ₹24m - ₹120m = ₹54m}
\]

> **Note:** Under **Ind AS 103**, goodwill is measured at acquisition date and subsequently tested for impairment (no impairment assumed here).

#### **Step 2 – Adjust for Fair‑Value Uplift on Plant**  

*Uplift* = ₹10 m; useful life = 5 years → **Additional depreciation** = ₹10 m / 5 = **₹2 m per year** (charged to **Depreciation expense**).  

| Entity | Original Depreciation | Additional Depreciation | **Adjusted Depreciation** |
|--------|----------------------|--------------------------|---------------------------|
| P      | 30                   | 0                        | 30 |
| S      | 20                   | 2                        | **22** |

#### **Step 3 – Compute Individual Profit Before Tax (PBT)**  

\[
\text{PBT}_P = \text{Revenue}_P - \text{COGS}_P - \text{OpExp}_P - \text{Dep}_P - \text{Interest}_P
\]

\[
\text{PBT}_P = 500 - 300 - 80 - 30 - 15 = \mathbf{75}
\]

\[
\text{PBT}_S = 200 - 120 - 40 - 22 - 10 = \mathbf{8}
\]

#### **Step 4 – Compute Tax (Current) & Net Profit**  

\[
\text{Tax}_P = 30\% \times 75 = 22.5
\qquad
\text{Tax}_S = 30\% \times 8 = 2.4
\]

\[
\text{Net Profit}_P = 75 - 22.5 = 52.5
\qquad
\text{Net Profit}_S = 8 - 2.4 = 5.6
\]

#### **Step 5 – Consolidation Adjustments**  

1. **Eliminate dividend received** (₹8 m) – intra‑group transaction.  
2. **Allocate profit to NCI**:  

\[
\text{NCI share of S’s profit} = 20\% \times 5.6 = 1.12
\]

3. **Parent’s share of S’s profit** (post‑tax) = 80 % × 5.6 = **4.48**  

4. **Add goodwill amortisation** – **none** (goodwill not amortised under Ind AS).  

#### **Step 6 – Consolidated Statement of Profit or Loss**  

| **Consolidated P&L** (₹ million) |  |
|----------------------------------|---|
| Revenue | 500 + 200 = **700** |
| Cost of Goods Sold | 300 + 120 = **420** |
| **Gross Profit** | **280** |
| Operating Expenses | 80 + 40 = **120** |
| Depreciation (adjusted) | 30 + 22 = **52** |
| **Operating Profit** | 280 – 120 – 52 = **108** |
| Interest Expense | 15 + 10 = **25** |
| **Profit Before Tax** | 108 – 25 = **83** |
| Tax Expense (30 %) | 0.30 × 83 = **24.9** |
| **Profit After Tax** | **58.1** |
| – Share of profit of S attributable to NCI | **1.12** |
| **Profit attributable to equity holders of Parent** | **57.0** |

> **Key Highlight:** The **dividend received** from S is eliminated, not shown as income.

#### **Step 7 – Consolidated Statement of Financial Position (selected items)**  

| **Item** | **Parent** | **Subsidiary** | **Adjustments** | **Consolidated** |
|----------|------------|----------------|-----------------|------------------|
| **Equity – Share Capital** | 200 | 80 | – | **280** |
| **Retained Earnings** (opening) | 60 | 30 | + Profit attributable to Parent (57) – Dividend paid to Parent (8) | **139** |
| **Non‑controlling Interest** | – | – | NCI share of S’s equity (20 % of 80) = 16 | **16** |
| **Goodwill** | – | – | **₹54** (from Step 1) | **54** |
| **Property, Plant & Equipment (net)** | 150 | 70 | + FV uplift (10) – extra depreciation (2) | **228** |
| **Cash & Cash Equivalents** | 70 | 30 | – intra‑group dividend (8) | **92** |
| **Total Assets** | 420 | 200 | + adjustments (goodwill, depreciation) | **672** |
| **Total Equity & Liabilities** | 420 | 200 | + adjustments | **672** |

> **Note:** The **NCI** is presented separately in equity as per **Ind AS 110**.

---

### 19.3.3  Key Take‑aways  

* **Goodwill** is calculated using consideration, NCI, and fair value of net assets.  
* **Additional depreciation** from fair‑value adjustments must be reflected in the profit‑or‑loss.  
* **Intra‑group dividends** are eliminated in the consolidation process.  
* **NCI** is allocated a share of the subsidiary’s profit and equity.  

---

## 19.4  Case Study 2 – Taxation & Deferred Tax (Income Tax Act & Ind AS 12)

### 19.4.1  Scenario  

**ABC Ltd.** prepares its financial statements for FY 2025‑26 (1 Apr 2025 – 31 Mar 2026). The following temporary differences exist at year‑end (₹ million):  

| Temporary Difference | Tax Base | Carrying Amount | Type |
|----------------------|----------|----------------|------|
| Revaluation surplus on land (IAS 16) | 0 | 30

---

