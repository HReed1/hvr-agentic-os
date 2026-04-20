#!/bin/bash

# Target the docs directory
TARGET_DIR="docs"

echo "🔍 Scanning $TARGET_DIR for un-prefixed markdown files..."

# Find all markdown files, explicitly excluding the architecture and gemini subdirectories
find "$TARGET_DIR" -type f -name "*.md" | grep -v "docs/architecture/" | grep -v "docs/gemini/" | while read -r filepath; do
    filename=$(basename "$filepath")
    dirpath=$(dirname "$filepath")
    
    # Check if the file already starts with the YYYY-MM-DD_ regex pattern
    if [[ ! "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}_ ]]; then
        
        # Extract the original creation date from the Git commit history
        creation_date=$(git log --diff-filter=A --format=%cs -1 -- "$filepath")
        
        # Fallback to local filesystem modification date if the file is untracked
        if [ -z "$creation_date" ]; then
            if stat -c %y "$filepath" &>/dev/null; then
                creation_date=$(stat -c %y "$filepath" | cut -d' ' -f1)
            else
                creation_date=$(stat -f "%Sm" -t "%Y-%m-%d" "$filepath" 2>/dev/null)
            fi
        fi
        
        if [ -n "$creation_date" ]; then
            new_filepath="${dirpath}/${creation_date}_${filename}"
            
            echo "🔄 Renaming: $filepath -> $new_filepath"
            
            # Use git mv to preserve the file history in version control
            git mv "$filepath" "$new_filepath" 2>/dev/null || mv "$filepath" "$new_filepath"
        else
            echo "⚠️ Could not determine date for $filepath. Skipping."
        fi
    fi
done

echo "✅ Documentation timestamp prefixing complete. Run 'git status' to review the staged moves."
