# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

import os
import requests
from dotenv import load_dotenv

# Load your GITHUB_PAT
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_PAT")
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def execute_graphql(query: str) -> dict:
    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"GraphQL request failed: {response.status_code} {response.text}")
    return response.json()

def discover_project_ids():
    query = """
    query {
      viewer {
        login
        projectsV2(first: 10) {
          nodes {
            id
            title
            fields(first: 20) {
              nodes {
                ... on ProjectV2Field { id name }
                ... on ProjectV2SingleSelectField { id name }
                ... on ProjectV2IterationField { id name }
              }
            }
          }
        }
      }
    }
    """
    
    print("Fetching Project V2 Data from GitHub...\n")
    result = execute_graphql(query)
    
    projects = result.get("data", {}).get("viewer", {}).get("projectsV2", {}).get("nodes", [])
    
    if not projects:
        print("No Projects V2 found for this user.")
        return

    for project in projects:
        print(f"=========================================")
        print(f"Project Title: {project.get('title')}")
        print(f"Project ID:    {project.get('id')}")
        print(f"-----------------------------------------")
        print("Custom Fields:")
        
        fields = project.get("fields", {}).get("nodes", [])
        for field in fields:
            # GitHub returns some empty nodes for fields that don't match our fragments, so we filter them
            if field: 
                print(f"  - Name: '{field.get('name')}' | ID: {field.get('id')}")
        print(f"=========================================\n")

if __name__ == "__main__":
    discover_project_ids()