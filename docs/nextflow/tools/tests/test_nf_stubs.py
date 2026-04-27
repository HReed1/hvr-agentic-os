import os
import glob
import pytest
import re

REPO_DIR = "tmp-repo"

def get_all_modules():
    base_dir = f"{REPO_DIR}/modules/nf-core"
    if not os.path.exists(base_dir):
        return []
    mods = []
    for d in os.listdir(base_dir):
        if os.path.exists(os.path.join(base_dir, d, "main.nf")):
            mods.append(d)
    return sorted(mods)

TARGET_MODULES = get_all_modules()

def get_module_paths(mod_name):
    p1 = f"{REPO_DIR}/modules/nf-core/{mod_name}/main.nf"
    if os.path.exists(p1):
        return [p1]
    return []

def _get_file_content(mod_name):
    paths = get_module_paths(mod_name)
    if not paths:
        pytest.skip(f"Module {mod_name} not found")
    with open(paths[0], "r") as f:
        return f.read()

def _has_versions_topic(content):
    output_match = re.search(r'\boutput:(.*?)(?=\b(?:when|script|stub):)', content, re.DOTALL)
    if not output_match:
        return False
    return bool(re.search(r'topic:\s*[\'"]?versions[\'"]?', output_match.group(1)))

def _clean_versions(version_string):
    lines = []
    for line in version_string.splitlines():
        if line.strip():
            lines.append(line.strip())
    return "\n".join(lines)

def _assert_versions_match(mod_name, script_block, stub_block):
    ver_match_script = re.search(r'(cat\s+<<-?\s*[\'"]?END_VERSIONS[\'"]?\s*>\s*versions\.yml.*?END_VERSIONS)', script_block, re.DOTALL)
    ver_match_stub = re.search(r'(cat\s+<<-?\s*[\'"]?END_VERSIONS[\'"]?\s*>\s*versions\.yml.*?END_VERSIONS)', stub_block, re.DOTALL)
    
    if ver_match_script:
        assert ver_match_stub is not None, f"versions.yml block missing in stub for {mod_name}"
        script_ver_cleaned = _clean_versions(ver_match_script.group(1))
        stub_ver_cleaned = _clean_versions(ver_match_stub.group(1))
        assert script_ver_cleaned == stub_ver_cleaned, f"versions.yml block in stub does not match script for {mod_name}"

@pytest.mark.parametrize("mod_name", TARGET_MODULES)
def test_stub_block_exists(mod_name):
    """
    Proof of Existence: Validates that the literal 'stub:' block is defined 
    in the module's main.nf file, ensuring the module has stub support.
    """
    content = _get_file_content(mod_name)
    assert "stub:" in content, f"stub: block missing in {mod_name}"

@pytest.mark.parametrize("mod_name", TARGET_MODULES)
def test_no_touch_gz_in_stub(mod_name):
    """
    Proof of Safe Output Mocking: Extracts the stub block and guarantees
    that `touch` is never used to create .gz files, which would corrupt 
    downstream alignment and compression workflows.
    """
    content = _get_file_content(mod_name)
    stub_match = re.search(r'\bstub:\s*(.*?)(?=\n\s*\w+:|\z)', content, re.DOTALL)
    if not stub_match:
        pytest.skip("No stub block to test")
        
    stub_block = stub_match.group(1)
    assert not re.search(r'touch\s+[^\n]*\.gz(?:\s|$)', stub_block), f"Found touch *.gz in {mod_name} stub"
    
@pytest.mark.parametrize("mod_name", TARGET_MODULES)
def test_versions_yml_matching(mod_name):
    """
    Proof of Payload Parity: Verifies that if versions.yml is statically 
    echoed inside the script block, the exact same emission string (matching 1:1) 
    is present inside the stub block to prevent MultiQC downstream failures.
    """
    content = _get_file_content(mod_name)
    has_topic = _has_versions_topic(content)
    
    stub_match = re.search(r'\bstub:(.*?)\z', content, re.DOTALL)
    if not stub_match:
        pytest.skip("No stub block")
        
    stub_block = stub_match.group(1)
    
    if not has_topic and 'path "versions.yml"' in content:
        assert "versions.yml" in stub_block, f"versions.yml not emitted in stub for {mod_name}"
        script_match = re.search(r'\bscript:(.*?)(?=\b(?:stub):|\z)', content, re.DOTALL)
        if script_match and "versions.yml" in script_match.group(1):
            _assert_versions_match(mod_name, script_match.group(1), stub_block)
