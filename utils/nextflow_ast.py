def extract_dsl2_block(content, target_process):
    """
    Extracts an entire nested DSL2 process block using bracket matching,
    preventing mid-closure regex failures.
    """
    if target_process.startswith("process ") or target_process.startswith("workflow "):
        start_token = target_process
    else:
        start_token = f"process {target_process} {{"
    start_idx = content.find(start_token)
    if start_idx == -1:
        return None
    
    bracket_count = 0
    in_block = False
    
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            bracket_count += 1
            in_block = True
        elif content[i] == '}':
            bracket_count -= 1
        
        if in_block and bracket_count == 0:
            return content[start_idx:i+1]
            
    return None
