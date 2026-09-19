import pytest
from nodes.router import route_question, Route

def test_route_question_live_data(mocker):
    mock_chain = mocker.patch('nodes.router.router_chain')
    mock_chain.invoke.return_value = Route(decision="live_market_data")
    
    state = {"original_question": "What is the price of Apple?", "memory_context": ""}
    
    result = route_question(state)
    
    assert result["routing_decision"] == "live_market_data"
    assert result["current_question"] == "What is the price of Apple?"
    mock_chain.invoke.assert_called_once_with({"question": "What is the price of Apple?", "memory_context": ""})

def test_route_question_calculation(mocker):
    mock_chain = mocker.patch('nodes.router.router_chain')
    mock_chain.invoke.return_value = Route(decision="calculation")
    
    state = {"original_question": "Calculate the WACC", "memory_context": ""}
    
    result = route_question(state)
    
    assert result["routing_decision"] == "calculation"
    assert result["current_question"] == "Calculate the WACC"
    mock_chain.invoke.assert_called_once_with({"question": "Calculate the WACC", "memory_context": ""})
