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

4. Set up your OpenAI Assistant:
   - Go to the [OpenAI platform](https://platform.openai.com/assistants)
   - Create a new assistant focused on car sharing and Cypher queries
   - Make sure the assistant has knowledge of Neo4j and the car sharing domain
   - Copy the Assistant ID for the next step

5. Configure environment variables:
   - Copy `src/.env-example` to `src/.env`
   - Update with your Neo4j Aura credentials
   - Add your OpenAI API key
   - Add your OpenAI Assistant ID

6. Run the application:
   ```
   streamlit run src/app.py
   ```

## Database

The schema and data for an initial load of the database may be found in the respectivate directories. Loading the data is a manual process.


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
