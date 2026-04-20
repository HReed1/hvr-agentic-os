import os

config_path = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/nextflow.config'
modules_config_path = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/conf/modules.config'

with open(config_path, 'r') as f:
    content = f.read()

parts = content.split('\nprocess {')
if len(parts) >= 2:
    base_config = parts[0]
    
    remaining = '\nprocess {' + parts[1]
    last_brace_idx = remaining.rfind('}')
    if "weblog {" in remaining:
        split_idx = remaining.find('\n// -------------------------------------------------------------')
        modules_config_content = remaining[:split_idx]
        base_config_tail = remaining[split_idx:]
    else:
        modules_config_content = remaining
        base_config_tail = ""
        
    with open(modules_config_path, 'w') as f:
        f.write(modules_config_content)
        
    with open(config_path, 'w') as f:
        f.write(base_config + "\n\nincludeConfig 'conf/modules.config'\n" + base_config_tail)
