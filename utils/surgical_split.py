import os
import re

CONTENT_DIR = "hvr-informatics/src/content"
SIM_DIR = "hvr-informatics/src/simulations"

def surgical_split():
    if not os.path.exists(SIM_DIR):
        os.makedirs(SIM_DIR)
        
    for filename in os.listdir(CONTENT_DIR):
        if not filename.endswith('.md'):
            continue
            
        commit_hash = filename.split('_')[-1].replace('.md', '')
        filepath = os.path.join(CONTENT_DIR, filename)
        
        with open(filepath, 'r') as file:
            content = file.read()
            
        parts = re.split(r'(?:##|###)\s*4\.\s*The Reader Simulation', content, flags=re.IGNORECASE)
        # Fallback for dynamic titles if numbering is missing:
        if len(parts) == 1:
            parts = re.split(r'(?:##|###)\s*Interactive Engineering Challenge', content, flags=re.IGNORECASE)
        if len(parts) == 1:
            parts = re.split(r'(?:##|###)\s*The Reader Simulation', content, flags=re.IGNORECASE)

        if len(parts) > 1:
            narrative_content = parts[0].strip()
            simulation_content = parts[1].strip() # Everything to EOF
            
            # Write simulation file
            sim_filepath = os.path.join(SIM_DIR, f"sim_{commit_hash}.md")
            with open(sim_filepath, 'w') as sim_file:
                sim_file.write(f"# Simulation Lab: {commit_hash}\n\n")
                sim_file.write(simulation_content)
                
            # Inject link into main file
            link_injection = f"\n\n*Deep dive into the syntax: [Proceed to the Simulation Lab ➔](/simulations/{commit_hash})*\n\n"
            with open(filepath, 'w') as file:
                file.write(narrative_content + link_injection)
            
            print(f"✅ Extracted simulation for {commit_hash} -> {sim_filepath}")
        else:
            print(f"⚠️ No simulation boundary found in {filename}")

if __name__ == "__main__":
    print("Executing The Surgical Split (Section 4 to EOF)...")
    surgical_split()
