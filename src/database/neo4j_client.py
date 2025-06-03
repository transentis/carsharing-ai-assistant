import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

class Neo4jClient:
    def __init__(self):
        load_dotenv()
        
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        self.driver = GraphDatabase.driver(
            self.uri, 
            auth=(self.username, self.password)
        )
    
    def execute_query(self, query, params=None):
        """
        Execute a Cypher query against the Neo4j database
        
        Args:
            query (str): The Cypher query to execute
            params (dict, optional): Parameters for the query
            
        Returns:
            list: Query results
        """
        if params is None:
            params = {}
            
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Error executing Neo4j query: {e}")
            return []
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver is not None:
            self.driver.close()
            
    def __del__(self):
        self.close()