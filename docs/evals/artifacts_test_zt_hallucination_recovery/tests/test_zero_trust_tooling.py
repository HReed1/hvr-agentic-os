import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from agent_app.zero_trust import _patched_get_tool

class MockFunctionCall:
    def __init__(self, name):
        self.name = name

def test_missing_tool_handled_gracefully():
    function_call = MockFunctionCall(name="missing_tool_123")
    tools_dict = {"existing_tool": None}
    
    tool = _patched_get_tool(function_call, tools_dict)
    
    assert tool is not None
    assert tool.func.__name__ == "missing_tool_123"
    
    result = tool.func()
    assert "[ZERO-TRUST FRAMEWORK ERROR]" in result
    assert "missing_tool_123" in result
    assert "existing_tool" in result
