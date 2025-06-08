import os
from .neo4j_client import Neo4jClient

class CSVImporter:
    def __init__(self, github_repo="transentis/knowledgegraph-ai-assistant", branch="main"):
        self.client = Neo4jClient()
        self.github_repo = github_repo
        self.branch = branch
        self.base_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/data"
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    def import_all_data(self):
        """Import all CSV data into Neo4j database"""
        try:
            # Clear existing data
            self.clear_database()
            
            # Create constraints
            self.create_constraints()
            
            # Import entities
            self.import_departments()
            self.import_processes()
            self.import_systems()
            self.import_roles()
            self.import_steps()
            
            # Import relationships
            self.import_process_department_relationships()
            self.import_process_step_relationships()
            self.import_role_step_relationships()
            self.import_step_system_relationships()
            
            print("Data import completed successfully!")
            
        except Exception as e:
            print(f"Error during import: {e}")
            raise
    
    def clear_database(self):
        """Clear all nodes, relationships, and constraints"""
        # Clear all nodes and relationships
        query = "MATCH (n) DETACH DELETE n"
        try:
            self.client.execute_query(query)
            print("✅ Database data cleared successfully")
        except Exception as e:
            print(f"❌ Failed to clear database data: {e}")
            raise
        
        # Clear all constraints
        try:
            # Get all constraints
            constraints_query = "SHOW CONSTRAINTS"
            constraints_result = self.client.execute_query(constraints_query)
            
            constraint_count = 0
            for constraint in constraints_result:
                constraint_name = constraint.get('name')
                if constraint_name:
                    try:
                        drop_query = f"DROP CONSTRAINT {constraint_name}"
                        self.client.execute_query(drop_query)
                        constraint_count += 1
                    except Exception as e:
                        print(f"⚠️  Warning: Could not drop constraint {constraint_name}: {e}")
            
            print(f"✅ {constraint_count} constraints cleared successfully")
        except Exception as e:
            print(f"❌ Failed to clear constraints: {e}")
            raise
    
    def create_constraints(self):
        """Create NODE KEY constraints for entity IDs (provides uniqueness + Bloom optimization)"""
        # Key constraints for Neo4j Bloom (makes name field primary in display and provides uniqueness)
        key_constraints = [
            "CREATE CONSTRAINT department_key IF NOT EXISTS FOR (d:department) REQUIRE d.name IS NODE KEY",
            "CREATE CONSTRAINT process_key IF NOT EXISTS FOR (p:process) REQUIRE p.name IS NODE KEY",
            "CREATE CONSTRAINT system_key IF NOT EXISTS FOR (s:system) REQUIRE s.name IS NODE KEY", 
            "CREATE CONSTRAINT role_key IF NOT EXISTS FOR (r:role) REQUIRE r.name IS NODE KEY",
            "CREATE CONSTRAINT step_key IF NOT EXISTS FOR (st:step) REQUIRE st.name IS NODE KEY"
        ]
        
        constraint_count = 0
        
        # Create key constraints (these provide both uniqueness and Bloom benefits)
        for key_constraint in key_constraints:
            try:
                self.client.execute_query(key_constraint)
                constraint_count += 1
            except Exception as e:
                if "equivalent constraint already exists" not in str(e).lower():
                    print(f"⚠️  Warning: Could not create key constraint: {e}")
                else:
                    constraint_count += 1
        
        print(f"✅ {constraint_count}/{len(key_constraints)} NODE KEY constraints created successfully")
    
    def import_departments(self):
        """Import departments from CSV"""
        file_path = f"{self.base_url}/department.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        CREATE (d:department {{
            name: row.Name,
            description: row.Description
        }})
        """
        try:
            self.client.execute_query(query)
            print("✅ Departments imported successfully")
        except Exception as e:
            print(f"❌ Failed to import departments: {e}")
            raise
    
    def import_processes(self):
        """Import processes from CSV"""
        file_path = f"{self.base_url}/process.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        CREATE (p:process {{
            name: row.Name,
            description: row.Description
        }})
        """
        try:
            self.client.execute_query(query)
            print("✅ Processes imported successfully")
        except Exception as e:
            print(f"❌ Failed to import processes: {e}")
            raise
    
    def import_systems(self):
        """Import systems from CSV"""
        file_path = f"{self.base_url}/system.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        CREATE (s:system {{
            category: row.Category,
            name: row.Name,
            description: row.Description
        }})
        """
        try:
            self.client.execute_query(query)
            print("✅ Systems imported successfully")
        except Exception as e:
            print(f"❌ Failed to import systems: {e}")
            raise
    
    def import_roles(self):
        """Import roles from CSV"""
        file_path = f"{self.base_url}/role.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        CREATE (r:role {{
            name: row.Name,
            description: row.Description
        }})
        """
        try:
            self.client.execute_query(query)
            print("✅ Roles imported successfully")
        except Exception as e:
            print(f"❌ Failed to import roles: {e}")
            raise
    
    def import_steps(self):
        """Import process steps from CSV"""
        file_path = f"{self.base_url}/process_step.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        CREATE (st:step {{
            name: row.Step,
            description: row.Description
        }})
        """
        try:
            self.client.execute_query(query)
            print("✅ Steps imported successfully")
        except Exception as e:
            print(f"❌ Failed to import steps: {e}")
            raise
    
    def import_process_department_relationships(self):
        """Import process-department relationships"""
        file_path = f"{self.base_url}/process_department.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        MATCH (p:process {{name: row.Process}})
        MATCH (d:department {{name: row.Department}})
        CREATE (d)-[:is_owner_of]->(p)
        """
        try:
            self.client.execute_query(query)
            print("✅ Process-Department relationships imported successfully")
        except Exception as e:
            print(f"❌ Failed to import Process-Department relationships: {e}")
            raise
    
    def import_process_step_relationships(self):
        """Import process-step relationships"""
        file_path = f"{self.base_url}/process_step.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        MATCH (p:process {{name: row.Process}})
        MATCH (st:step {{name: row.Step}})
        CREATE (p)-[:has_step]->(st)
        """
        try:
            self.client.execute_query(query)
            print("✅ Process-Step relationships imported successfully")
        except Exception as e:
            print(f"❌ Failed to import Process-Step relationships: {e}")
            raise
    
    def import_role_step_relationships(self):
        """Import role-step relationships"""
        file_path = f"{self.base_url}/role_step.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        MATCH (r:role {{name: row.Role}})
        MATCH (st:step {{name: row.Step}})
        CREATE (r)-[:performs]->(st)
        """
        try:
            self.client.execute_query(query)
            print("✅ Role-Step relationships imported successfully")
        except Exception as e:
            print(f"❌ Failed to import Role-Step relationships: {e}")
            raise
    
    def import_step_system_relationships(self):
        """Import step-system relationships"""
        file_path = f"{self.base_url}/step_system.csv"
        query = f"""
        LOAD CSV WITH HEADERS FROM '{file_path}' AS row
        MATCH (st:step {{name: row.Step}})
        MATCH (s:system {{name: row.System}})
        CREATE (s)-[:supports]->(st)
        """
        try:
            self.client.execute_query(query)
            print("✅ Step-System relationships imported successfully")
        except Exception as e:
            print(f"❌ Failed to import Step-System relationships: {e}")
            raise
    
    def close(self):
        """Close the database connection"""
        self.client.close()
