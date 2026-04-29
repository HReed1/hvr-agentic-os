#!/usr/bin/env bash
# restore_edam_comments.sh
#
# Restores EDAM ontology comments (e.g., "# TSV", "# YAML") that are stripped
# by `nf-core modules lint --fix` due to YAML serialization limitations.
#
# Usage: ./restore_edam_comments.sh <module_name>
# Example: ./restore_edam_comments.sh emmtyper
#
# This script compares the meta.yml in the working tree against upstream/master
# and restores any inline comments on EDAM ontology lines that were stripped.

set -euo pipefail

MODULE="${1:?Usage: $0 <module_name>}"
META_FILE="modules/nf-core/${MODULE}/meta.yml"

if [[ ! -f "$META_FILE" ]]; then
    echo "ERROR: $META_FILE not found. Run from nf-core-modules repo root." >&2
    exit 1
fi

# Check if upstream/master has this file
if ! git show "upstream/master:${META_FILE}" &>/dev/null; then
    echo "INFO: No upstream version of $META_FILE — skipping EDAM comment restoration."
    exit 0
fi

# Extract EDAM lines with comments from upstream
CHANGES=0
while IFS= read -r line; do
    # Get the EDAM URI and comment from upstream
    uri=$(echo "$line" | sed 's/^.*edam: \(http[^ ]*\).*/\1/')
    comment=$(echo "$line" | sed 's/^.*edam: http[^ ]* \(#.*\)/\1/')
    
    if [[ -z "$comment" ]] || [[ "$comment" == "$line" ]]; then
        continue
    fi

    # Check if local file has the URI without the comment
    if grep -q "edam: ${uri}$" "$META_FILE"; then
        # Restore the comment
        sed -i '' "s|edam: ${uri}$|edam: ${uri} ${comment}|" "$META_FILE"
        echo "RESTORED: ${uri} ${comment}"
        CHANGES=$((CHANGES + 1))
    fi
done < <(git show "upstream/master:${META_FILE}" | grep "edam:.*#")

if [[ $CHANGES -eq 0 ]]; then
    echo "OK: No EDAM comments needed restoration."
else
    echo "RESTORED: $CHANGES EDAM comment(s) in $META_FILE"
fi
