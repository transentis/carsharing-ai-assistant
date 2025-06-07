# CarSharing AI Assistant justfile
# Run tasks with: just <command>

# Default command when just is called without arguments
default:
    @just --list

# Run the Streamlit app
run:
    source venv/bin/activate && cd src && streamlit run app.py

# Install dependencies
install:
    pip install -r requirements.txt

# Setup a virtual environment and install dependencies
setup:
    python -m venv venv
    . venv/bin/activate && pip install -r requirements.txt

# Run the app in debug mode with verbose logging
debug:
    cd src && streamlit run app.py --logger.level=debug

# Check connections to OpenAI and Neo4j
check:
    cd src && python -c "from utils.assistant_utils import verify_assistant; success, msg = verify_assistant(); print(f'OpenAI Assistant: {msg}'); from database.neo4j_client import Neo4jClient; client = Neo4jClient(); result = client.execute_query('RETURN 1 as test'); print(f'Neo4j: Connected successfully')"

# Import CSV data into Neo4j database
import-data:
    python import_data.py