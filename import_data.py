#!/usr/bin/env python3
"""
Script to import CSV data into Neo4j AuraDB
"""

import argparse
from src.database.csv_importer import CSVImporter

def main():
    parser = argparse.ArgumentParser(description="Import CSV data into Neo4j AuraDB")
    parser.add_argument(
        "--repo", 
        default="transentis/knowledgegraph-ai-assistant",
        help="GitHub repository in format 'owner/repo' (default: transentis/knowledgegraph-ai-assistant)"
    )
    parser.add_argument(
        "--branch",
        default="main", 
        help="Git branch to import from (default: main)"
    )
    
    args = parser.parse_args()
    
    print(f"Starting CSV data import to Neo4j from {args.repo}...")
    
    importer = CSVImporter(github_repo=args.repo, branch=args.branch)
    
    try:
        importer.import_all_data()
        print("\n✅ Import completed successfully!")
        print("\nYou can now query your data using Cypher queries like:")
        print("MATCH (d:department) RETURN d.name, d.description")
        print("MATCH (d:department)-[:is_owner_of]->(p:process) RETURN d.name, p.name")
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        
    finally:
        importer.close()

if __name__ == "__main__":
    main()