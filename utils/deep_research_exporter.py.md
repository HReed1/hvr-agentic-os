# Deep Research Exporter (`deep_research_exporter.py`)

## Overview
This utility automates the extraction and transformation of Google Docs containing deep research reports entirely into localized, offline Markdown structures (`.md`) bound with their embedded images intact.

## Functionality
- **API Connectivity Mode (`--folder_id`)**: Authenticates via `gcloud auth application-default` using the Google Drive `v3` API. Iterates over a target folder, dynamically requesting a Web-Page Zip export (`application/zip`) for each document.
- **Offline Mode (`--zip_file`)**: Accepts a manually downloaded Google Doc `.zip` archive.
- **Markdown Conversion Engine**: 
    - Extracts the embedded `images/` directory locally.
    - Scrapes the core `html` payload using `BeautifulSoup`.
    - Sanitizes away raw embedded `<style>` and `<script>` CSS injections typical of Google Docs.
    - Utilizes `markdownify` to build ATX-style headings and convert paths seamlessly to standard Markdown link references.
- **Output**: Dumps the constructed `.md` alongside its relevant images directory inside `docs/research/`.
