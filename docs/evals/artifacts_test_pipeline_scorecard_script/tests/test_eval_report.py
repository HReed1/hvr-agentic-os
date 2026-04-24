import os
import importlib.util
import sys

def test_eval_report_structural_integrity():
    file_path = "utils/generate_global_eval_report.py"
    assert os.path.exists(file_path), "Target script missing from workspace"
    
    spec = importlib.util.spec_from_file_location("generate_global_eval_report", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_global_eval_report"] = module
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        assert False, f"Failed to import module due to syntax or dependency error: {e}"
    
    assert hasattr(module, "generate_scorecard"), "Missing generate_scorecard function"
    assert hasattr(module, "EVALS_DIR"), "Missing EVALS_DIR constant"
