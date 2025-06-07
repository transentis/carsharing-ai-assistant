# CarSharing AI Assistant

An AI-powered conversational assistant for car sharing services, built with Streamlit and integrated with Neo4j and OpenAI.

## Features

- Natural language conversational interface
- Custom OpenAI Assistant for generating Cypher queries
- Neo4j database integration for car sharing data
- Streamlit web interface with interactive chat

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/carsharing-ai-assistant.git
   cd carsharing-ai-assistant
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `src/.env-example` to `src/.env`
   - Update with your Neo4j Aura credentials
   - Add your OpenAI API key
   - The OpenAI Assistant will be created automatically when the app starts

5. Run the application:
   ```
   streamlit run src/app.py
   ```

## Database

The schema and data for an initial load of the database may be found in the data directory. 

### Data Import

To import the CSV data into your Neo4j AuraDB:

```bash
just import-data
```

This will load all the carsharing process data including departments, processes, systems, roles, and their relationships.

### Cypher Query Examples

Here are some useful Cypher queries for exploring the data:

#### Load all nodes and relationships (including isolated nodes)
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
```

#### Get all processes
```cypher
MATCH (p:process)
RETURN p.name, p.description
```

#### Get all systems that support the 'Car Rental' process
```cypher
MATCH (p:process {name: 'Car Rental'})-[:has_step]->(s:step)<-[:supports]-(sys:system)
RETURN DISTINCT sys.name, sys.category, sys.description
```

#### Find which department owns each process
```cypher
MATCH (d:department)-[:is_owner_of]->(p:process)
RETURN d.name as department, p.name as process
```

#### Get all roles that perform steps in a specific process
```cypher
MATCH (p:process {name: 'Car Rental'})-[:has_step]->(s:step)<-[:performs]-(r:role)
RETURN r.name as role, s.step as step_name
```

#### Find the complete workflow for a process
```cypher
MATCH (d:department)-[:is_owner_of]->(p:process {name: 'Car Rental'})-[:has_step]->(s:step)
OPTIONAL MATCH (r:role)-[:performs]->(s)
OPTIONAL MATCH (sys:system)-[:supports]->(s)
RETURN d.name as department, p.name as process, s.step as step, 
       r.name as role, sys.name as system
ORDER BY s.step
```


## How It Works

1. User submits a natural language query about the car sharing enterprose
2. The OpenAI Assistant generates a Cypher query based on the user's question
3. The application executes the Cypher query against the Neo4j database
4. Results are passed back to the OpenAI Assistant for formatting
5. The formatted response is displayed to the user

## Troubleshooting

- If you see an error connecting to the OpenAI Assistant, make sure your Assistant ID is correct
- For Neo4j connection issues, verify your database credentials and that the database is running
- Check that your OpenAI API key has sufficient credits and permissions
