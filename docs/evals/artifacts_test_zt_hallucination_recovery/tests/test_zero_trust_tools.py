import pytest
import logging
from unittest.mock import MagicMock
from agent_app.zero_trust import _patched_get_tool

class MockFunctionCall:
    def __init__(self, name):
        self.name = name

def test_hallucinated_tool_invocation_trapped(caplog):
    """
    Asserts that the system natively traps, LOGS, and rejects unmapped tool invocations
    without escalating privileges.
    """
    mock_tools = {"valid_tool": MagicMock()}
    mock_fc = MockFunctionCall("missing_tool_123")
    
    with caplog.at_level(logging.WARNING):
        # Execute the patched tool getter directly
        recovered_tool = _patched_get_tool(mock_fc, mock_tools)
        
        # Call the returned recovery function
        result = recovered_tool.func()
        
    assert "[ZERO-TRUST FRAMEWORK ERROR]" in result
    assert "Tool 'missing_tool_123' is physically air-gapped" in result
    
    # Assert that the security violation was explicitly logged
    assert any("missing_tool_123" in record.message for record in caplog.records), "The framework intercepted the tool but failed to explicitly log the violation."
