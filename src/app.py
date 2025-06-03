import streamlit as st
from database.neo4j_client import Neo4jClient
from agent.openai_agent import OpenAIAgent
from utils.assistant_utils import verify_assistant

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "neo4j_client" not in st.session_state:
        st.session_state.neo4j_client = Neo4jClient()
    if "openai_agent" not in st.session_state:
        st.session_state.openai_agent = OpenAIAgent()

def main():
    st.title("Car Sharing Enterprise Chat Assistant")
    
    # Verify connection to OpenAI Assistant
    success, message = verify_assistant()
    if not success:
        st.error(f"Error: {message}")
        st.info("Please update the OPENAI_ASSISTANT_ID in your .env file with your CarSharing Assistant ID")
        return
    
    # Verify connection to Neo4j
    try:
        initialize_session_state()
        st.session_state.neo4j_client.execute_query("RETURN 1 as test")
        st.success("Connected to OpenAI Assistant and Neo4j database")
    except Exception as e:
        st.error(f"Error connecting to Neo4j: {str(e)}")
        st.info("Please check your Neo4j credentials in the .env file")
        return
    
    # Display chat interface
    with st.container():
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # User input
        if prompt := st.chat_input("Ask about the car sharing enterprise ..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Generating Cypher query..."):
                    # Generate Cypher query using OpenAI Assistant
                    cypher_query = st.session_state.openai_agent.generate_cypher_query(prompt)
                    
                    # Show the query (can be commented out in production)
                    with st.expander("View Cypher Query"):
                        st.code(cypher_query, language="cypher")
                
                with st.spinner("Querying database..."):
                    # Execute query against Neo4j
                    result = st.session_state.neo4j_client.execute_query(cypher_query)
                    
                    # Show raw results (can be commented out in production)
                    with st.expander("View Raw Results"):
                        st.json(result)
                
                with st.spinner("Formatting response..."):
                    # Format and display response using OpenAI Assistant
                    response = st.session_state.openai_agent.format_response(prompt, result)
                    st.write(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
