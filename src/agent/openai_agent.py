import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIAgent:
    def __init__(self, cleanup_on_exit=True):
        load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.cleanup_on_exit = cleanup_on_exit
        self.assistant = self._create_or_get_assistant()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_on_exit:
            self.cleanup_assistant()
    
    def cleanup_assistant(self):
        """Delete the assistant to avoid accumulating unused assistants."""
        if hasattr(self, 'assistant') and self.assistant:
            try:
                self.client.beta.assistants.delete(assistant_id=self.assistant.id)
                print(f"Deleted assistant with ID: {self.assistant.id}")
            except Exception as e:
                print(f"Error deleting assistant: {e}")
    
    def _load_schema(self):
        """Load the knowledgegraph schema from the schema directory."""
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'schema', 'car_sharing_meta_graph.json')
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Schema file not found at {schema_path}")
            return None
    
    def _get_function_definitions(self):
        """Define the functions available to the assistant."""
        schema = self._load_schema()
        schema_text = json.dumps(schema, indent=2) if schema else "Schema not available"
        
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_knowledgegraph",
                    "description": "Generate a Neo4j Cypher query to retrieve data from the knowledgegraph and then fetch that data from the knowledgegraph",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_question": {
                                "type": "string",
                                "description": "The user's question about the car sharing enterprise knowledgegraph data"
                            },
                            "context": {
                                "type": "string", 
                                "description": "Additional context about what specific data is needed"
                            }
                        },
                        "required": ["user_question"]
                    }
                }
            }
        ]
    
    def _create_or_get_assistant(self):
        """Create or reuse an OpenAI assistant with knowledgegraph schema and instructions."""
        assistant_name = "Knowledgegraph AI Assistant"
        
        # First, try to find an existing assistant with the same name
        try:
            assistants = self.client.beta.assistants.list()
            for assistant in assistants.data:
                if assistant.name == assistant_name:
                    print(f"Reusing existing assistant with ID: {assistant.id}")
                    return assistant
        except Exception as e:
            print(f"Error listing assistants: {e}")
        
        # If no existing assistant found, create a new one
        schema = self._load_schema()
        schema_text = json.dumps(schema, indent=2) if schema else "Schema not available"
        
        instructions = f"""You are a knowledgegraph AI assistant that can help with both general conversation and knowledgegraph operations.

You have access to a Neo4j knowledgegraph with the following schema:

node labels and their property keys

    process
        name
        description
    department
        name
        description
    role
        name
        description
    step
        name
        description    
    system
        name
        category
        description

relationships
        department-"is_owner_of"->process
        process-"has_step"->step
        role-"performs"->step
        system-"supports"->step

        
Your capabilities include:
1. **General conversation**: Answer questions, provide explanations, and discuss enterprise process topics
2. **Generating Cypher Queries**:  When asked to generate a cypher query, follow the guidelines for generating cypher queries outlined below
3. **Formating data return from the knowledgegraph**: When asked to format data provided in json format, format the results appropriately         
4. **Knowledgegraph queries**: Use the query_knowledgegraph function when users ask for data from the knowledgegraph. 

Guidelines for generating cypher queries:
- The generated queries must respect the schema provided above.        
- Use proper Neo4j Cypher syntax

When to use the query_knowledgegraph function:
- User asks for specific information from the knowledgegraph

When to chat normally:
- User asks for explanations or interpretations
- User wants to discuss results from knowledgegraph queries
- User needs help understanding results

Be conversational and helpful. If you're not sure whether to query the knowledgegraph, ask the user for clarification."""

        function_tools = self._get_function_definitions()

        try:
            assistant = self.client.beta.assistants.create(
                name=assistant_name,
                instructions=instructions,
                model="gpt-4o",
                tools=function_tools
            )
            print(f"Created new assistant with ID: {assistant.id}")
            return assistant
        except Exception as e:
            print(f"Error creating assistant: {e}")
            raise
    
    def _wait_for_run_completion(self, thread_id, run_id, timeout=60):
        """Wait for a run to complete, polling at 1-second intervals."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            print(run.status)
            if run.status in ["completed", "failed", "cancelled", "expired","requires_action"]:
                return run
            time.sleep(1)
        raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")
    
    def _handle_query_knowledgegraph(self, arguments,neo4j_client,executed_queries):
        """Handle the generate_cypher_query function call."""
        user_question = arguments.get("user_question", "")
        context = arguments.get("context", "")
        
        prompt = user_question
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        # Create a dedicated thread just for Cypher generation
        try:
            query_thread = self.client.beta.threads.create()
            
            # Create a specialized assistant for query generation (or use a simple prompt)
            query_prompt = f"""Generate a Neo4j Cypher query for the car sharing knowledgegraph that will answer this question: {prompt}

Use the schema defined in the instructions.

Important rules:
- Don't LIMIT the results
- Provide ONLY the Cypher query with no other text, explanations or formatting
- Don't use ```cypher blocks, just the raw query"""

            self.client.beta.threads.messages.create(
                thread_id=query_thread.id,
                role="user",
                content=query_prompt
            )
            
            # Run assistant to generate query
            run = self.client.beta.threads.runs.create(
                thread_id=query_thread.id,
                assistant_id=self.assistant.id,
            )
            
            # Wait for completion
            run = self._wait_for_run_completion(query_thread.id, run.id)
            
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(thread_id=query_thread.id, limit=1)
                assistant_message = messages.data[0]
                cypher_query = assistant_message.content[0].text.value.strip()
                
                # Clean up any formatting artifacts
                cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
                
                print(f"Generated Cypher query: {cypher_query}")

                query_results = neo4j_client.execute_query(cypher_query)
                
                executed_queries.append({
                   "query": cypher_query,
                   "results": query_results
                })
                                
                # Return both query and results to the assistant
                results_summary = f"Query executed: {cypher_query}\n\nResults: {json.dumps(query_results, indent=2)}"
                
                                
                return results_summary
            else:
                raise Exception(f"Knowledgegraph query failed with status: {run.status}")
                
        except Exception as e:
            print(f"Error querying knowledgegraph: {e}")
           
            return "No data collected"
    
    def _handle_function_call(self, function_name, arguments,neo4j_client,executed_queries):
        """Route function calls to appropriate handlers."""
        if function_name == "query_knowledgegraph":
            return self._handle_query_knowledgegraph(arguments,neo4j_client,executed_queries)
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def chat_with_knowledgegraph(self, user_message, neo4j_client, thread_id=None):
        """
        Enhanced chat method that integrates knowledgegraph operations.
        
        Args:
            user_message (str): The user's message
            neo4j_client: Neo4j client instance for executing knowledgegraph queries
            thread_id (str, optional): Existing thread ID to continue conversation
            
        Returns:
            dict: Response containing message, any query results, and thread_id
        """
        executed_queries = []
        
        try:
            # Create or use existing thread
            if thread_id:
                thread = self.client.beta.threads.retrieve(thread_id)
            else:
                thread = self.client.beta.threads.create()
            
            # Add user message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant.id,
            )
            
            # Wait for completion and handle function calls
            while True:
                run = self._wait_for_run_completion(thread.id, run.id)
                
                if run.status == "requires_action":
                    # Handle function calls
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        print(f"Function called: {function_name} with args: {arguments}")
                        
                        try:
                            result = self._handle_function_call(function_name, arguments,neo4j_client,executed_queries)
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": str(result)
                            })
                                
                        except Exception as e:
                            error_msg = f"Error executing {function_name}: {str(e)}"
                            print(error_msg)
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": error_msg
                            })
                    
                    # Submit tool outputs and continue
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    continue
                
                elif run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run {run.status}: {run.last_error}")
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id, limit=1)
            assistant_message = messages.data[0]
            
            response_text = assistant_message.content[0].text.value
            
            return {
                "message": response_text,
                "thread_id": thread.id,
                "executed_queries": executed_queries,
                "status": "success"
            }
            
        except Exception as e:
            print(f"Error in chat_with_knowledgegraph: {e}")
            return {
                "message": "I'm sorry, I encountered an error processing your request. Please try again.",
                "thread_id": thread_id,
                "executed_queries": executed_queries,
                "status": "error",
                "error": str(e)
            }
    
    
   
