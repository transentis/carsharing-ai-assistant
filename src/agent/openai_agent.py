import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIAgent:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        
        if not self.assistant_id:
            raise ValueError("OPENAI_ASSISTANT_ID environment variable is required")
    
    def _wait_for_run_completion(self, thread_id, run_id, timeout=60):
        """Wait for a run to complete, polling at 1-second intervals."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                return run
            time.sleep(1)
        raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")
    
    def generate_cypher_query(self, user_prompt):
        """
        Generate a Cypher query based on the user's prompt using the OpenAI Assistant
        
        Args:
            user_prompt (str): The user's question regarding content in the car sharing database
            
        Returns:
            str: A Cypher query to extract relevant information
        """
        try:
            # Create a thread for this conversation
            thread = self.client.beta.threads.create()
            
            # Add the user's message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Generate a Neo4j Cypher query for the car sharing database that will answer this question: " + user_prompt +
                "\n\nBe aware that all nodes, relationships and their properties are capitalized, e.g. it should be Process and not process and Name and not name."+
                "\n\nWhenever you generate a Neo4j Cypher query, provide ONLY the Cypher query with no other text, explanation, or formatting."
            )
            
            # Run the assistant on the thread
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
            )
            
            # Wait for the run to complete
            run = self._wait_for_run_completion(thread.id, run.id)
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Extract the Cypher query from the assistant's response
            assistant_message = next((m for m in messages.data if m.role == "assistant"), None)
            if assistant_message and assistant_message.content:
                cypher_query = assistant_message.content[0].text.value.strip()
                
                # Log the generated query for debugging
                print(f"Generated Cypher query: {cypher_query}")
                
                return cypher_query
            else:
                raise ValueError("No response from assistant")
                
        except Exception as e:
            print(f"Error generating Cypher query: {e}")
            return "MATCH (d:Department) RETURN d.Name LIMIT 25"  # Fallback query
    
    def format_response(self, user_prompt, query_results):
        """
        Format the database query results into a natural language response
        
        Args:
            user_prompt (str): The original user question
            query_results (list): Results from the Neo4j query
            
        Returns:
            str: A natural language response to the user's question
        """
        try:
            # Create a thread for this response
            thread = self.client.beta.threads.create()
            
            # Add a message with the query results to the thread
            message_content = f"User question: {user_prompt}\n\nDatabase results: {json.dumps(query_results)}\n\n"
            message_content += "Please provide a helpful, conversational response to the user's question based on these database results."
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message_content
            )
            
            # Run the assistant on the thread
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
            )
            
            # Wait for the run to complete
            run = self._wait_for_run_completion(thread.id, run.id)
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Extract the response
            assistant_message = next((m for m in messages.data if m.role == "assistant"), None)
            if assistant_message and assistant_message.content:
                return assistant_message.content[0].text.value
            else:
                raise ValueError("No response from assistant")
                
        except Exception as e:
            print(f"Error formatting response: {e}")
            return "I'm sorry, I encountered an issue processing your request. Please try again."
