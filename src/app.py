import streamlit as st
from database.neo4j_client import Neo4jClient
from agent.openai_agent import OpenAIAgent

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "neo4j_client" not in st.session_state:
        st.session_state.neo4j_client = Neo4jClient()
    if "openai_agent" not in st.session_state:
        st.session_state.openai_agent = OpenAIAgent()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

def main():
    st.title("Car Sharing Enterprise Chat Assistant")
    
    # Initialize session state and verify connections
    try:
        initialize_session_state()
        # Test Neo4j connection
        st.session_state.neo4j_client.execute_query("RETURN 1 as test")
        st.success("Connected to OpenAI Assistant and Neo4j database")
    except Exception as e:
        st.error(f"Error connecting to services: {str(e)}")
        st.info("Please check your API keys and database credentials in the .env file")
        return
    
    # Display chat interface
    with st.container():
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # User input
        if prompt := st.chat_input("Ask about the car sharing enterprise or chat about your data..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response using unified chat method
            with st.chat_message("assistant"):
                with st.spinner("Processing your request..."):
                    # Use the new chat method that handles both conversation and database queries
                    response_data = st.session_state.openai_agent.chat_with_database(
                        user_message=prompt,
                        neo4j_client=st.session_state.neo4j_client,
                        thread_id=st.session_state.thread_id
                    )
                    
                    # Update thread ID for conversation continuity
                    st.session_state.thread_id = response_data.get("thread_id")
                    
                    # Display the assistant's response
                    assistant_response = response_data.get("message", "I'm sorry, I couldn't process your request.")
                    st.write(assistant_response)
                    
                    # Show executed queries if any
                    executed_queries = response_data.get("executed_queries", [])
                    if executed_queries:
                        with st.expander(f"Database Queries Executed ({len(executed_queries)})"):
                            for i, query_data in enumerate(executed_queries):
                                st.write(f"**Query {i+1}:**")
                                st.code(query_data["query"], language="cypher")
                                st.write("**Results:**")
                                st.json(query_data["results"])
                                if i < len(executed_queries) - 1:
                                    st.divider()
                    
                    # Show error information if there was an issue
                    if response_data.get("status") == "error":
                        with st.expander("Error Details"):
                            st.error(response_data.get("error", "Unknown error occurred"))
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    main()
