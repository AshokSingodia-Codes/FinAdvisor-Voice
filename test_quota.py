import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
try:
    print("Testing openai/gpt-oss-120b quota...")
    llm = ChatGroq(model_name="openai/gpt-oss-120b", max_tokens=10, timeout=10)
    response = llm.invoke("Hi")
    print("SUCCESS: 120b worked.")
except Exception as e:
    print(f"FAILED 120b: {e}")
    try:
        print("Testing openai/gpt-oss-20b quota...")
        llm_20 = ChatGroq(model_name="openai/gpt-oss-20b", max_tokens=10, timeout=10)
        response = llm_20.invoke("Hi")
        print("SUCCESS: 20b worked.")
    except Exception as e2:
        print(f"FAILED 20b: {e2}")
