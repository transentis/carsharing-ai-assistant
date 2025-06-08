# Knowledge Graph AI Assistant

An AI-powered conversational assistant for knowledge graphs containing information about the structures and processes of an enterprise.

This is a simple demo app, built with Streamlit and integrated with Neo4j and OpenAI.

Most of the code was written by Claude Code, with a little prompting from Oliver Grasl.

## Features

- Natural language conversational interface
- Custom OpenAI Assistant for generating Cypher queries
- Neo4j knowledge graph integration for enterprise process data
- Streamlit web interface with interactive chat
- **Report generation**: Generate professional PDF reports from knowledge graph data using Typst markup language

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/transentis/knowledgegraph-ai-assistant.git
   cd knowledgegraph-ai-assistant
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

4. Install Just (command runner):
   ```bash
   # On macOS
   brew install just
   
   # On Linux
   curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin
   
   # On Windows
   scoop install just
   # or
   cargo install just
   ```
   
   Alternatively, you can run commands directly with Python instead of using `just`.

5. Install Typst (for report generation):
   ```bash
   # On macOS
   brew install typst
   
   # On Linux
   curl -fsSL https://typst.community/typst-install/install.sh | sh
   
   # On Windows
   winget install --id Typst.Typst
   # or
   cargo install --git https://github.com/typst/typst --locked typst-cli
   ```
   
   Note: Typst is required only if you want to generate PDF reports. The assistant will work without it for regular queries.

6. Configure environment variables:
   - Copy `src/.env-example` to `src/.env`
   - Update with your Neo4j Aura credentials
   - Add your OpenAI API key
   - The OpenAI Assistant will be created automatically when the app starts

7. Run the application:
   ```
   streamlit run src/app.py
   ```

## Database

The schema and data for an initial load of the database may be found in the data directory. 

### Data Import

To import the CSV data into your Neo4j AuraDB:

**Using Just:**
```bash
just import-data
```

**Or directly with Python:**
```bash
python import_data.py
```

This will load all the enterprise process data including departments, processes, systems, roles, and their relationships from the current repository.

You can also specify a different repository or branch:

**Using Just:**
```bash
just import-data "your-username/your-fork"
```

**Or directly with Python:**
```bash
python import_data.py --repo "your-username/your-fork" --branch "development"
```

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

1. User submits a natural language query about their enterprise processes
2. The OpenAI Assistant generates a Cypher query based on the user's question
3. The application executes the Cypher query against the Neo4j knowledgegraph
4. Results are passed back to the OpenAI Assistant for formatting
5. The formatted response is displayed to the user

For report generation:
1. User asks for a "report" or "document" about specific data
2. The assistant queries the knowledgegraph and formats results using Typst markup
3. A professional PDF report is generated and made available for download
4. Both the source Typst file and compiled PDF are provided

## Example Report Prompts

Try these prompts to generate professional reports from your knowledgegraph:

- "Generate a report on all departments and their processes"
- "Create a document showing which systems support each process step"
- "I need a formatted summary of all roles and their responsibilities"
- "Generate a report about all processes and their departments"
- "Create a document listing all systems that support the 'Car Rental' process"
- "I want a report showing the complete workflow for each process"

## Troubleshooting

- If you see an error connecting to the OpenAI Assistant, make sure your Assistant ID is correct
- For Neo4j connection issues, verify your database credentials and that the database is running
- Check that your OpenAI API key has sufficient credits and permissions
