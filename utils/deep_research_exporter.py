import os
import io
import re
import argparse
import zipfile
import textwrap
from bs4 import BeautifulSoup
from markdownify import markdownify as md

import google.auth
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_drive_service():
    try:
        credentials, project = google.auth.default(scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        return service
    except DefaultCredentialsError:
        print("\n[!] FATAL: Google Application Default Credentials not found or missing Drive scopes.")
        print("Please run the following command to authenticate your local developer environment:")
        print("    gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.readonly\n")
        exit(1)

def sanitize_filename(name):
    """Make the Google Doc title filesystem-friendly."""
    s = str(name).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def export_gdoc_to_markdown(service, file_id, file_name, output_base_dir):
    """
    Downloads a Google Doc as a Zip (HTML + localized images),
    Unzips it, converts the HTML to Markdown, and saves the output.
    """
    safe_name = sanitize_filename(file_name)
    doc_dir = os.path.join(output_base_dir, safe_name)
    os.makedirs(doc_dir, exist_ok=True)
    images_dir = os.path.join(doc_dir, 'images')
    
    print(f"\n[*] Exporting '{file_name}' ({file_id})...")
    
    # 1. Request the Zip archive of the document Web-Page view
    request = service.files().export_media(fileId=file_id, mimeType='application/zip')
    
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    print(f"[-] Successfully downloaded stream. Extracting assets...")
    fh.seek(0)
    
    html_content = None
    
    # 2. Extract contents directly to the designated document folder
    with zipfile.ZipFile(fh, 'r') as z:
        for file_info in z.infolist():
            if file_info.filename.endswith('.html'):
                html_content = z.read(file_info).decode('utf-8')
            elif file_info.filename.startswith('images/'):
                # Write the image to the local images directory
                z.extract(file_info, path=doc_dir)

    if not html_content:
        print(f"[!] Warning: No HTML content found in export pipeline for {file_name}.")
        return

    # 3. Clean and convert to Markdown
    print(f"[-] Compiling layout and mappings to Markdown format...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Prevent table of contents links from looking ugly by removing their anchors
    for a in soup.find_all('a'):
        if not a.get('href') or a.get('href').startswith('#'):
            a.unwrap()
            
    # Markdownify will natively map '<img src="images/XXX">' to '![...](images/XXX)'
    markdown_text = md(str(soup), heading_style="ATX", escape_asterisks=False, bullets="-")
    
    # Strip excessive newlines inserted by Google Docs blocks
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    
    output_md_path = os.path.join(doc_dir, f"{safe_name}.md")
    with open(output_md_path, 'w') as f:
        f.write(markdown_text)
        
    print(f"[✓] Complete! Markdown written to: {output_md_path}")

from googleapiclient.errors import HttpError

def process_folder(folder_id, output_dir):
    service = get_drive_service()
    
    try:
        # List all Google Docs inside the target folder
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            print(f"No Google Docs found in folder ID: {folder_id}.")
            return

        print(f"Found {len(items)} Google Docs for Research extraction pipeline.")
        
        for item in items:
            export_gdoc_to_markdown(service, item['id'], item['name'], output_dir)
    except HttpError as e:
        if e.status_code == 403 and "insufficient authentication scopes" in str(e).lower():
            print("\n[!] FATAL: Your Application Default Credentials lack Google Drive access scopes.")
            print("Please authorize your local environment by running this specific command:")
            print("    gcloud auth application-default login --scopes=\"https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive.readonly\"\n")
            exit(1)
        else:
            raise

def process_offline_zip(zip_path, output_dir):
    """Processes a manually downloaded Web Page (.zip) from Google Docs."""
    if not os.path.exists(zip_path):
        print(f"[!] Target zip file not found: {zip_path}")
        return
        
    base_name = os.path.basename(zip_path).replace('.zip', '')
    safe_name = sanitize_filename(base_name)
    doc_dir = os.path.join(output_dir, safe_name)
    os.makedirs(doc_dir, exist_ok=True)
    
    print(f"\n[*] Processing offline extract '{base_name}'...")
    html_content = None
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        for file_info in z.infolist():
            if file_info.filename.endswith('.html'):
                html_content = z.read(file_info).decode('utf-8')
            elif file_info.filename.startswith('images/'):
                z.extract(file_info, path=doc_dir)

    if not html_content:
        print(f"[!] Warning: No HTML content found inside offline zip {base_name}.")
        return

    print(f"[-] Compiling layout and mappings to Markdown format...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Strip any massive CSS blocks Google embeds in the <head>
    for element in soup(["style", "script"]):
        element.decompose()
        
    for a in soup.find_all('a'):
        if not a.get('href') or a.get('href').startswith('#'):
            a.unwrap()
            
    markdown_text = md(str(soup), heading_style="ATX", escape_asterisks=False, bullets="-")
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    
    output_md_path = os.path.join(doc_dir, f"{safe_name}.md")
    with open(output_md_path, 'w') as f:
        f.write(markdown_text)
        
    print(f"[✓] Complete! Markdown written to: {output_md_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Deep Research Export Utility")
    parser.add_argument("--folder_id", help="The Google Drive Folder ID containing the reports (Requires OAuth setup).")
    parser.add_argument("--zip_file", help="Path to a manually downloaded Google Docs Web Page (.zip).")
    parser.add_argument("--output", default="docs/research", help="The output directory.")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.zip_file:
        process_offline_zip(args.zip_file, args.output)
    elif args.folder_id:
        process_folder(args.folder_id, args.output)
    else:
        print("Please provide either --folder_id or --zip_file.")
        exit(1)
    
    print("\n[★] Batch Deep Research extraction complete.")
