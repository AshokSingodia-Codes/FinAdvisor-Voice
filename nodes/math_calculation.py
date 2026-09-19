import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from graph.state import AgentState
from core.db import chat, get_structured_chat
from tools.calculator import (
    safe_calculate,
    percentage_of,
    percentage_change,
    sum_list,
    strip_currency_and_commas
)

class BasicMathExtraction(BaseModel):
    operation: str = Field(description="The mathematical operation to perform: 'arithmetic', 'percentage_of', 'percentage_change', 'sum_list', or 'none'")
    expression: str = Field(default="", description="The arithmetic expression to evaluate (for 'arithmetic' operation only). Only use numbers and basic operators (+, -, *, /, %). E.g., '12 + 5'.")
    values: List[float] = Field(default_factory=list, description="List of numerical values needed for operations other than 'arithmetic'.")
    
basic_math_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a mathematical extraction agent.
    Read the user's question and determine the basic math operation needed.
    DO NOT perform the math yourself. Simply extract the operation and operands.
    
    Operations and expected values:
    - 'arithmetic': For basic addition, subtraction, multiplication, division. Provide the string formula in the 'expression' field (e.g. '1500 + 320'). Do not use commas in numbers.
    - 'percentage_of': [value, percent] (e.g. for '12% of 50000', values=[50000, 12]).
    - 'percentage_change': [old_value, new_value].
    - 'sum_list': [val1, val2, val3...] for totaling multiple numbers.
    - 'none': If no calculation is possible.
    
    Return the structured extraction.
    """),
    ("human", "{question}")
])

basic_math_chain = basic_math_prompt | get_structured_chat(BasicMathExtraction)

def do_math_calculation(state: AgentState):
    print("---NODE: MATH CALCULATION---")
    question = state["current_question"]
    question = strip_currency_and_commas(question)
    
    try:
        extraction = basic_math_chain.invoke({"question": question})
        op = extraction.operation
        expr = extraction.expression
        vals = extraction.values
        
        result = None
        if op == "arithmetic" and expr:
            result = safe_calculate(expr)
        elif op == "percentage_of" and len(vals) >= 2:
            result = percentage_of(vals[0], vals[1])
        elif op == "percentage_change" and len(vals) >= 2:
            result = percentage_change(vals[0], vals[1])
        elif op == "sum_list" and len(vals) > 0:
            result = sum_list(vals)
            
        if result is not None:
            if isinstance(result, tuple):
                # Format multiple results
                formatted_results = [f"{int(r):,}" if float(r).is_integer() else f"{r:,.2f}" for r in result]
                draft = f"The calculated results are {', '.join(formatted_results)}."
            else:
                # Format single result
                if float(result).is_integer():
                    draft = f"The calculated result is {int(result):,}."
                else:
                    draft = f"The calculated result is {result:,.2f}."
        else:
            draft = "I could not extract the exact numbers required to perform this basic calculation."
            
    except ValueError as ve:
        print(f"Calculator ValueError: {ve}")
        draft = f"I encountered an error during calculation: {ve}"
    except Exception as e:
        print(f"Math calculation error: {e}")
        draft = "An error occurred while attempting to compute the arithmetic."
        
    return {"draft_answer": draft}
