#!/usr/bin/env python3
"""
Script to import CSV data into Neo4j AuraDB
"""

from src.database.csv_importer import CSVImporter

def main():
    print("Starting CSV data import to Neo4j...")
    
    importer = CSVImporter()
    
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