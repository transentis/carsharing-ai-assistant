import os
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
    st.title("Knowledge Graph AI Assistant")
    
    # Initialize session state and verify connections
    try:
        initialize_session_state()
        # Test Neo4j connection
        st.session_state.neo4j_client.execute_query("RETURN 1 as test")
        st.success("Connected to OpenAI Assistant and Neo4j knowledgegraph")
    except Exception as e:
        st.error(f"Error connecting to services: {str(e)}")
        st.info("Please check your API keys and knowledgegraph credentials in the .env file")
        return
    
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show executed queries and reports for assistant messages
            if message["role"] == "assistant":
                # Show executed queries if any
                executed_queries = message.get("executed_queries", [])
                if executed_queries:
                    with st.expander(f"Knowledge Graph Queries Executed ({len(executed_queries)})"):
                        for j, query_data in enumerate(executed_queries):
                            st.write(f"**Query {j+1}:**")
                            st.code(query_data["query"], language="cypher")
                            st.write("**Results:**")
                            st.json(query_data["results"])
                            if j < len(executed_queries) - 1:
                                st.divider()
                
                # Show generated reports if any
                generated_reports = message.get("generated_reports", [])
                if generated_reports:
                    with st.expander(f"Generated Reports ({len(generated_reports)})"):
                        for j, report in enumerate(generated_reports):
                            st.write(f"**Report {j+1}: {report.get('title', 'Untitled Report')}**")
                            st.write(f"Records analyzed: {report.get('records_count', 0)}")
                            
                            col1, col2 = st.columns(2)
                            
                            # Download Typst file
                            if 'typst_file' in report and os.path.exists(report['typst_file']):
                                with col1:
                                    with open(report['typst_file'], 'r') as f:
                                        typst_content = f.read()
                                    st.download_button(
                                        label="📄 Download Typst Source",
                                        data=typst_content,
                                        file_name=f"report_{i}_{j+1}.typ",
                                        mime="text/plain",
                                        key=f"typst_{i}_{j}"
                                    )
                            
                            # Download PDF file
                            if 'pdf_file' in report and os.path.exists(report['pdf_file']):
                                with col2:
                                    with open(report['pdf_file'], 'rb') as f:
                                        pdf_content = f.read()
                                    st.download_button(
                                        label="📋 Download PDF Report",
                                        data=pdf_content,
                                        file_name=f"report_{i}_{j+1}.pdf",
                                        mime="application/pdf",
                                        key=f"pdf_{i}_{j}"
                                    )
                            
                            if 'error' in report:
                                st.error(f"Error generating report: {report['error']}")
                            
                            if j < len(generated_reports) - 1:
                                st.divider()
    
    # User input - always at the bottom
    if prompt := st.chat_input("Ask about your knowledgegraph data or chat about enterprise processes..."):
        # Add user message to chat history and display immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response using unified chat method
        with st.spinner("Processing your request..."):
            # Use the new chat method that handles both conversation and knowledgegraph queries
            response_data = st.session_state.openai_agent.chat_with_knowledgegraph(
                user_message=prompt,
                neo4j_client=st.session_state.neo4j_client,
                thread_id=st.session_state.thread_id
            )
            
            # Update thread ID for conversation continuity
            st.session_state.thread_id = response_data.get("thread_id")
            
            # Get the assistant's response and metadata
            assistant_response = response_data.get("message", "I'm sorry, I couldn't process your request.")
            executed_queries = response_data.get("executed_queries", [])
            generated_reports = response_data.get("generated_reports", [])
            
            # Add assistant response to chat history with metadata
            message_data = {
                "role": "assistant", 
                "content": assistant_response,
                "executed_queries": executed_queries,
                "generated_reports": generated_reports
            }
            st.session_state.messages.append(message_data)
            
            if response_data.get("status") == "error":
                st.session_state.last_error = response_data.get("error", "Unknown error occurred")
        
        # Rerun to refresh the display with new messages
        st.rerun()
    
    # Display errors if any
    if hasattr(st.session_state, 'last_error') and st.session_state.last_error:
        with st.expander("Error Details"):
            st.error(st.session_state.last_error)
        # Clear after displaying
        st.session_state.last_error = None

if __name__ == "__main__":
    main()
