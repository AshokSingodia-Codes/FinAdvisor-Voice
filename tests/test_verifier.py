import pytest
from nodes.verifier import verify_answer, Verification

def test_verify_answer_safe_abstention(mocker):
    mock_chain = mocker.patch('nodes.verifier.verifier_chain')
    mock_chain.invoke.return_value = Verification(
        is_supported=True,
        numerical_consistency=True,
        citation_consistency=True,
        reasoning="Assistant correctly stated that the data is not available without fabricating numbers."
    )
    
    state = {
        "verifier_enabled": True,
        "draft_answer": "I do not have access to audited revenues for this unlisted company.",
        "retrieved_context": [],
        "original_question": "What were the revenues of Blue Horizon BioTech?"
    }
    
    res = verify_answer(state)
    assert res["verification_passed"] is True
    assert "[Verification Notice]" not in res["final_answer"]

def test_verify_answer_hallucinated_company_numbers(mocker):
    mock_chain = mocker.patch('nodes.verifier.verifier_chain')
    mock_chain.invoke.return_value = Verification(
        is_supported=False,
        numerical_consistency=False,
        citation_consistency=False,
        reasoning="Draft claims Apple revenue was $999B which is not in context."
    )
    
    state = {
        "verifier_enabled": True,
        "draft_answer": "Apple's 2024 revenue was $999B.",
        "retrieved_context": ["Total net sales: $391,035 million"],
        "original_question": "What was Apple's revenue in 2024?"
    }
    
    res = verify_answer(state)
    assert res["verification_passed"] is False
    assert "[Verification Notice]" in res["final_answer"]

def test_verify_answer_skipped_when_disabled():
    state = {
        "verifier_enabled": False,
        "draft_answer": "Any draft answer",
        "retrieved_context": [],
        "original_question": "Any question"
    }
    res = verify_answer(state)
    assert res["verification_passed"] is True
    assert res["final_answer"] == "Any draft answer"
