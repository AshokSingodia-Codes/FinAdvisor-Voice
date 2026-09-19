import os
import time
from dotenv import load_dotenv
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

def generate_textbook():
    print("Initializing LLM for Textbook Generation...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in .env")
        return
        
    chat = ChatGroq(
        temperature=0.3,
        model_name="openai/gpt-oss-120b",
        api_key=api_key,
        max_retries=3
    )
    
    # Massively expanded syllabus to cover Basic to Advanced + CA (Chartered Accountant) Level topics
    syllabus = [
        "Chapter 1: Personal Finance and Wealth Management Basics",
        "Chapter 2: The Time Value of Money and Advanced Annuities",
        "Chapter 3: Introduction to Accounting Principles and Bookkeeping",
        "Chapter 4: Advanced Financial Reporting (IFRS & US GAAP)",
        "Chapter 5: Corporate Finance: Cost of Capital, Capital Structure, and Dividend Policy",
        "Chapter 6: Advanced Capital Budgeting and Risk Analysis",
        "Chapter 7: Equity Valuation Models (DCF, DDM, FCFE/FCFF, Relative Valuation)",
        "Chapter 8: Fixed Income Securities: Pricing, Duration, Convexity, and Term Structure",
        "Chapter 9: Derivatives Pricing: Options, Futures, Forwards, and Swaps",
        "Chapter 10: Advanced Derivatives: Black-Scholes-Merton, Binomial Trees, and The Greeks",
        "Chapter 11: Portfolio Management and Asset Pricing Models (CAPM, APT)",
        "Chapter 12: Mergers, Acquisitions, and Corporate Restructuring",
        "Chapter 13: Direct Taxation: Corporate Tax Planning and Wealth Tax",
        "Chapter 14: Indirect Taxation: GST, Value Added Taxes, and Customs Duty",
        "Chapter 15: Principles of Auditing and Assurance Engagements",
        "Chapter 16: Corporate and Economic Laws: Governance, Contracts, and Insolvency",
        "Chapter 17: Strategic Financial Management and Risk Mitigation",
        "Chapter 18: Macroeconomics, Monetary Policy, and International Finance",
        "Chapter 19: Chartered Accountant (CA) Case Studies and Complex Problem Solving Methods"
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert financial textbook author and a Chartered Accountant (CA) instructor.
        Your task is to write a highly detailed, comprehensive chapter for an ultimate finance textbook.
        
        RULES:
        1. Format the output entirely in Markdown.
        2. Provide clear, bolded definitions for all key terms.
        3. Include complex mathematical formulas using LaTeX formatting.
        4. Provide concrete, real-world examples with numbers to illustrate concepts.
        5. For advanced topics, include step-by-step methodologies to solve complex CA-level exam problems.
        6. The chapter should be extremely thorough, acting as a definitive study guide.
        """),
        ("human", "Please write {chapter} in full detail.")
    ])
    
    chain = prompt | chat
    
    output_dir = "Annual Report"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "Ultimate_Finance_Knowledge_Base.md")
    
    print(f"Starting Generation. The book will be saved to: {output_file}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# The Ultimate Finance & CA Knowledge Base\n\n")
        
        for chapter in syllabus:
            print(f"Generating: {chapter}...")
            try:
                response = chain.invoke({"chapter": chapter})
                f.write(f"## {chapter}\n\n")
                f.write(response.content)
                f.write("\n\n---\n\n")
                print(f"[SUCCESS] Completed {chapter}")
                time.sleep(2)
            except Exception as e:
                print(f"[ERROR] Error generating {chapter}: {e}")
                
    print(f"Textbook generation complete! File saved at {output_file}")

if __name__ == "__main__":
    generate_textbook()
