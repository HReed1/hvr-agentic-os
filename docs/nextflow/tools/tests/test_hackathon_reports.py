import os
import glob
import re

def test_reports_exist():
    assert os.path.exists("docs/nextflow/hackathon/report_1_module_inventory.md"), "Report 1 missing"
    assert os.path.exists("docs/nextflow/hackathon/report_2_diff_report.md"), "Report 2 missing"
    assert os.path.exists("docs/nextflow/hackathon/report_3_validation.md"), "Report 3 missing"

def test_report_1_content():
    with open("docs/nextflow/hackathon/report_1_module_inventory.md", "r") as f:
        content = f.read()
    assert "Remaining Unfixed Modules" in content, "Missing Remaining Unfixed Modules section"
    assert "|" in content, "No markdown table found"

def test_report_2_content():
    with open("docs/nextflow/hackathon/report_2_diff_report.md", "r") as f:
        content = f.read()
    # Expecting report 2 to contain diff blocks with the pattern
    assert "echo '' | gzip >" in content, "Pattern echo '' | gzip > not found in Report 2 diff blocks"

def test_report_3_content():
    with open("docs/nextflow/hackathon/report_3_validation.md", "r") as f:
        content = f.read()
    assert "Status" in content, "Status column not found in Report 3"

def test_no_touch_gz_in_diffs():
    diff_files = glob.glob("docs/nextflow/hackathon/diffs/*.diff")
    assert len(diff_files) > 0, "No diff files found in docs/nextflow/hackathon/diffs/"
    
    for diff_file in diff_files:
        with open(diff_file, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                if re.search(r'touch\s+[^\n]*\.gz', line):
                    assert False, f"Anti-pattern 'touch *.gz' found in added line of {diff_file}: {line}"
