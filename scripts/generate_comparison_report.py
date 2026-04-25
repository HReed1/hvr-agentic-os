import os
import glob
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_eval_file(filepath):
    data = {
        "result": "UNKNOWN",
        "inferences": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "exists": False
    }
    
    if not os.path.exists(filepath):
        return data
        
    data["exists"] = True
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "**Result: [PASS]**" in content:
        data["result"] = "PASS"
    elif "**Result: [FAIL]**" in content:
        data["result"] = "FAIL"
        
    inf_match = re.search(r"\*\*Total LLM Inferences:\*\* `?(\d+)`?", content)
    if inf_match:
        data["inferences"] = int(inf_match.group(1))
        
    # Example string: - **solo_agent**: 5 inferences [In: 1,000 | Out: 500]
    total_in = 0
    total_out = 0
    token_matches = re.finditer(r"\[In:\s*([\d,]+)\s*\|\s*Out:\s*([\d,]+)\]", content)
    for match in token_matches:
        total_in += int(match.group(1).replace(',', ''))
        total_out += int(match.group(2).replace(',', ''))
        
    data["tokens_in"] = total_in
    data["tokens_out"] = total_out
    
    return data

def build_scorecard():
    tasks = ["test_compare_small", "test_compare_medium", "test_compare_large", "test_compare_fullstack"]
    
    markdown = "# Head-to-Head: Autonomous Swarm vs Solo God-Mode\n\n"
    markdown += "| Benchmark Task | Swarm Verdict | Swarm Inferences | Swarm Tokens (In / Out) | Solo Verdict | Solo Inferences | Solo Tokens (In / Out) |\n"
    markdown += "|---|---|---|---|---|---|---|\n"
    
    for task in tasks:
        # Search for the latest eval matching this task for both modes
        swarm_files = glob.glob(os.path.join(BASE_DIR, "docs", "evals", f"*_{task}_swarm_eval.md"))
        solo_files = glob.glob(os.path.join(BASE_DIR, "docs", "evals", f"*_{task}_solo_eval.md"))
        
        swarm_files.sort(key=os.path.getmtime, reverse=True)
        solo_files.sort(key=os.path.getmtime, reverse=True)
        
        swarm_data = parse_eval_file(swarm_files[0]) if swarm_files else parse_eval_file("")
        solo_data = parse_eval_file(solo_files[0]) if solo_files else parse_eval_file("")
        
        swarm_v = "✅ " + swarm_data["result"] if swarm_data["result"] == "PASS" else "❌ " + swarm_data["result"]
        solo_v = "✅ " + solo_data["result"] if solo_data["result"] == "PASS" else "❌ " + solo_data["result"]
        
        if not swarm_data["exists"]: swarm_v = "N/A"
        if not solo_data["exists"]: solo_v = "N/A"
        
        s_inf = str(swarm_data["inferences"]) if swarm_data["exists"] else "-"
        s_tok = f"{swarm_data['tokens_in']:,} / {swarm_data['tokens_out']:,}" if swarm_data["exists"] else "-"
        
        solo_inf = str(solo_data["inferences"]) if solo_data["exists"] else "-"
        solo_tok = f"{solo_data['tokens_in']:,} / {solo_data['tokens_out']:,}" if solo_data["exists"] else "-"
        
        name = task.replace("test_compare_", "").capitalize()
        markdown += f"| {name} | {swarm_v} | {s_inf} | {s_tok} | {solo_v} | {solo_inf} | {solo_tok} |\n"
        
    out_path = os.path.join(BASE_DIR, "docs", "comparisons", "HEAD_TO_HEAD_SCORECARD.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, "w") as f:
        f.write(markdown)
        
    print(f"[SCORECARD] Generated successfully: {out_path}")

if __name__ == "__main__":
    build_scorecard()
