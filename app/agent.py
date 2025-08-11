from google.adk.agents import Agent
import requests
import json
from typing import Any, Dict, List, Optional
from google.adk.agents import SequentialAgent,ParallelAgent
from dotenv import load_dotenv

load_dotenv()

#1. Basic Agent
base_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)


# 2. Basic Agent with Tool and Multi-Tool Agent for calling RESTAPI

BASE_URL = "https://api.restful-api.dev/objects"

def get_all_objects() -> Optional[List[Dict[str, Any]]]:
    """
    Consumes GET List of all objects: https://api.restful-api.dev/objects
    """
    print("\n--- GET All Objects ---")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all objects: {e}")
        return None

def get_objects_by_ids(ids: List[int]) -> Optional[List[Dict[str, Any]]]:
    """
    Consumes GET List of objects by ids: https://api.restful-api.dev/objects?id=3&id=5&id=10
    Args:
        ids (list): A list of integer IDs.
    """
    print(f"\n--- GET Objects by IDs: {ids} ---")
    params = {'id': ids} # Requests handles list parameters correctly for multiple 'id'
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching objects by IDs: {e}")
        return None

def get_single_object(object_id: str) -> Optional[Dict[str, Any]]:
    """
    Consumes GET Single object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to retrieve.
    """
    print(f"\n--- GET Single Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id}: {e}")
        return None

def add_object(name: str, data_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes POST Add object: https://api.restful-api.dev/objects
    Args:
        name (str): The name of the new object.
        data_payload (dict): A dictionary representing the 'data' field of the object.
    """
    print(f"\n--- POST Add Object: {name} ---")
    payload = {
        "name": name,
        "data": data_payload
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        new_object = response.json()
        print(json.dumps(new_object, indent=2))
        return new_object
    except requests.exceptions.RequestException as e:
        print(f"Error adding object: {e}")
        return None

def update_object(object_id: str, name: str, data_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes PUT Update object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to update.
        name (str): The new name for the object.
        data_payload (dict): The new 'data' field for the object.
    """
    print(f"\n--- PUT Update Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    payload = {
        "name": name,
        "data": data_payload
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        updated_object = response.json()
        print(json.dumps(updated_object, indent=2))
        return updated_object
    except requests.exceptions.RequestException as e:
        print(f"Error updating object {object_id}: {e}")
        return None

def partially_update_object(object_id: str, data_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes PATCH Partially update object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to partially update.
        data_to_update (dict): A dictionary containing the fields to update (e.g., {"name": "New Name"}).
    """
    print(f"\n--- PATCH Partially Update Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.patch(url, json=data_to_update, headers=headers)
        response.raise_for_status()
        patched_object = response.json()
        print(json.dumps(patched_object, indent=2))
        return patched_object
    except requests.exceptions.RequestException as e:
        print(f"Error partially updating object {object_id}: {e}")
        return None

def delete_object(object_id: str) -> Optional[Dict[str, Any]]:
    """
    Consumes DELETE object: https://api.restful-api.dev/objects/6
    Args:
        object_id (str): The ID of the object to delete.
    """
    print(f"\n--- DELETE Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        # A successful DELETE often returns 200 OK with a message, or 204 No Content
        # The restful-api.dev returns 200 OK with a success message for DELETE
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error deleting object {object_id}: {e}")
        return None


tool_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash-001",
    description="An agent that can interact with a RESTful API for objects",
    instruction="""
    You are a RestAPI service caller assistant. Call the given tools as per the instruction given by the uses and print the data in json format.
    """,
    tools=[
        get_all_objects,
        get_objects_by_ids,
        get_single_object,
        add_object,
        update_object,
        partially_update_object,
        delete_object,
    ],
)

#root_agent=tool_agent    



# 3. Agent with State
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext



def get_single_object(object_id: str , tool_context: ToolContext) -> Optional[Dict[str, Any]]:
    """
    Consumes GET Single object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to retrieve.
    """
    print(f"\n--- GET Single Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        # Initialize recent_searches if it doesn't exist
        if "recent_searches" not in tool_context.state:
            tool_context.state["recent_searches"] = []
            
        recent_searches = tool_context.state["recent_searches"]
        if object_id not in recent_searches:
            recent_searches.append(object_id)
            tool_context.state["recent_searches"] = recent_searches   
            #print  tool_context.state["recent_searches"]
            print('tool_context.state["recent_searches"] ------------------------->',tool_context.state["recent_searches"]) 
            
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id}: {e}")
        return None
    
stateful_agent = Agent(
    name="stateful_agent",
    model="gemini-2.0-flash-001",
    description="An agent that can interact with a RESTful API for objects",
    instruction="""
    You are a RestAPI service caller assistant. Call the given tools as per the instruction given by the uses and print the data in json format.
    """,
    tools=[
        get_single_object,        
    ],
)


#4. Structured Output Agent
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field



class MobileType(BaseModel):
    mobileType: str = Field(description="Name of the mobile")
    manufactureCompanyName: str = Field(description="Name of the Company that manufacture that mobile")

# Define a function to get value of the objet id enter by the user
def get_single_object(object_id: str , tool_context: ToolContext) -> Optional[Dict[str, Any]]:
    """
    Consumes GET Single object: https://api.restful-api.dev/objects/{object_id}
    Args:
        object_id (str): The ID of the object to retrieve.
    """
    print(f"\n--- GET Single Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id}: {e}")
        return None

structured_agent = LlmAgent(
    name="structured_agent",
    model="gemini-2.0-flash-001",
    description="An agent that can interact with a RESTful API for given objects id and can provide structured output",
    instruction="""
    You are a RestAPI service caller assistant. Call the given tools as per the instruction given by the user and print the data in json format.
    Return Name of the Company that manufacture that mobile in JSON format.
    
    For each object_id, look at the name to make a decision.
    If name contains Google return Name of the Company that manufacture that mobile as Google else if name contains Apple return Name of the Company that manufacture that mobile return Apple
    Otherwise: name
    """,
    output_schema=MobileType,
    output_key="mobile_company_name"
)


# 6. Callback Agent
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any, Optional

# Define a function to get value of the objet id enter by the user
def get_single_object(object_id: str , tool_context: ToolContext) -> Optional[Dict[str, Any]]:
    """
    Consumes GET Single object: https://api.restful-api.dev/objects/{object_id}
    Args:
        object_id (str): The ID of the object to retrieve.
    """
    print(f"\n--- GET Single Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id}: {e}")
        return None

def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    # Initialize tool_usage if it doesn't exist
    if "tool_usage" not in tool_context.state:
        tool_context.state["tool_usage"] = {}
        
    # Track tool usage count
    tool_usage = tool_context.state["tool_usage"]
    tool_name = tool.name
    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
    tool_context.state["tool_usage"] = tool_usage
    
    print(f"[LOG] Running tool: {tool_name}")
    return None

def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    print(f"[LOG] Tool {tool.name} completed")
    return None

# Initialize state before creating the agent
initial_state = {"tool_usage": {}}

callback_agent = Agent(
     name="callback_agent",
    model="gemini-2.0-flash-001",
    description="An agent that can interact with a RESTful API for objects",
    instruction="""
    You are a RestAPI service caller assistant. Call the given tools as per the instruction given by the uses and print the data in json format.
    """,
    tools=[get_single_object],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

#root_agent=callback_agent    

# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

# Code Writer Agent
# Takes the initial specification (from user query) and writes code.
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model="gemini-2.0-flash-001",
    # Change 3: Improved instruction
    instruction="""You are a Python Code Generator.
Based *only* on the user's request, write Python code that fulfills the requirement.
Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
    description="Writes initial Python code based on a specification.",
    output_key="generated_code" # Stores output in state['generated_code']
)

# Code Reviewer Agent
# Takes the code generated by the previous agent (read from state) and provides feedback.
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-2.0-flash-001",
    # Change 3: Improved instruction, correctly using state key injection
    instruction="""You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

**Review Criteria:**
1.  **Correctness:** Does the code work as intended? Are there logic errors?
2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
5.  **Best Practices:** Does the code follow common Python best practices?

**Output:**
Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
If the code is excellent and requires no changes, simply state: "No major issues found."
Output *only* the review comments or the "No major issues" statement.
""",
    description="Reviews code and provides feedback.",
    output_key="review_comments", # Stores output in state['review_comments']
)


# Code Refactorer Agent
# Takes the original code and the review comments (read from state) and refactors the code.
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model="gemini-2.0-flash-001",
    # Change 3: Improved instruction, correctly using state key injection
    instruction="""You are a Python Code Refactoring AI.
Your goal is to improve the given Python code based on the provided review comments.

  **Original Code:**
  ```python
  {generated_code}
  ```

  **Review Comments:**
  {review_comments}

**Task:**
Carefully apply the suggestions from the review comments to refactor the original code.
If the review comments state "No major issues found," return the original code unchanged.
Ensure the final code is complete, functional, and includes necessary imports and docstrings.

**Output:**
Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
    description="Refactors code based on review comments.",
    output_key="refactored_code", # Stores output in state['refactored_code']
)


# --- 2. Create the SequentialAgent ---
# This agent orchestrates the pipeline by running the sub_agents in order.
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)


# For ADK tools compatibility, the root agent must be named `root_agent`
#root_agent = code_pipeline_agent


# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

#LoopAgent example

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions

# --- Constants ---
APP_NAME = "doc_writing_app_v3" # New App Name
USER_ID = "dev_user_01"
SESSION_ID_BASE = "loop_exit_tool_session" # New Base Session ID
GEMINI_MODEL = "gemini-2.0-flash"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  # Return empty dict as tools should typically return JSON-serializable output
  return {}

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: Ask for a slightly more developed start
    instruction=f"""You are a Creative Writing Assistant tasked with starting a story.
    Write the *first draft* of a short story (aim for 2-4 sentences).    
""",
    description="Writes the initial document draft based on the topic, aiming for some initial substance.",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction=f"""You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences). Your goal is balanced feedback.
    Review the document for clarity and improve to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
   if the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
    Respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else. 
""",
    description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    output_key=STATE_CRITICISM
)


# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.
    Analyze the 'Critique/Suggestions'.
    IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.
    ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'. Output *only* the refined document text.

    Do not add explanations. Either output the refined document OR call the exit_loop function.
""",
    description="Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)


# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
# root_agent = SequentialAgent(
#     name="IterativeWritingPipeline",
#     sub_agents=[
#         initial_writer_agent, # Run first to create initial doc
#         refinement_loop       # Then run the critique/refine loop
#     ],
#     description="Writes an initial document and then iteratively refines it with critique using an exit tool."
# )

#parallel Agent example

# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
# --- 1. Define Researcher Sub-Agents (to run in parallel) ---

def add(object_id1: str,object_id2: str):
    """

    Args:
        object_id1 (str): First number
        object_id2 (str): Second number
		
    """
    print(f"\n--- {object_id1} --- {object_id2}")
   
    try:
        return int(object_id1) + int(object_id2)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id1} and {object_id2}: {e}")
        return None
    
def Subtract(object_id1: str,object_id2: str):
    """
      Args:
        object_id1 (str): First number
        object_id2 (str): Second number
		
    """
    print(f"\n--- {object_id1} --- {object_id2}")
   
    try:
        return int(object_id1) - int(object_id2)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id1} and {object_id2}: {e}")
        return None
    
def Multiply(object_id1: str,object_id2: str):
    """

    Args:
        object_id1 (str): First number
        object_id2 (str): Second number
		
    """
    print(f"\n--- {object_id1} --- {object_id2}")
   
    try:
        return int(object_id1) * int(object_id2)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id1} and {object_id2}: {e}")
        return None
            
# Researcher 1: Addition Of two values
researcher_agent_1 = LlmAgent(
    name="AddtionOfTwovalues",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in addition of two values provided by the user.
""",
    description="Agent that add two values.",
    tools=[add],
    # Store result in state for the merger agent
    output_key="researcher_agent_1_output_key"
)

# Researcher 2: Substraction Of two values
researcher_agent_2 = LlmAgent(
    name="SubstrationOfTwovalues",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in substration of two values provided by the user.
""",
    description="Agent that substract two values.",
    tools=[Subtract],
    # Store result in state for the merger agent
    output_key="researcher_agent_2_output_key"
)

# Researcher 3: Multiplicaiton of two values
researcher_agent_3 = LlmAgent(
    name="MultiplicaitonOfTwovalues",
    model=GEMINI_MODEL,
    instruction="""You are an AI Research Assistant specializing in multiple two values provided by the user.
""",
    description="Agent that multiply two values.",
    tools=[Multiply],
    # Store result in state for the merger agent
    output_key="researcher_agent_3_output_key"
)



# --- 2. Create the ParallelAgent (Runs researchers concurrently) ---
# This agent orchestrates the concurrent execution of the researchers.
# It finishes once all researchers have completed and stored their results in state.
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="Runs multiple research agents in parallel to gather information."
)

# --- 3. Define the Merger Agent (Runs *after* the parallel agents) ---
# This agent takes the results stored in the session state by the parallel agents
# and synthesizes them into a single, structured response with attributions.
merger_agent = LlmAgent(
    name="ParallelFormatAgent",
    model=GEMINI_MODEL,  # Or potentially a more powerful model if needed for synthesis
    instruction="""You are an AI Assistant responsible for combining research findings into a structured report.

**Input Summaries:**

*   **Addition:**
    {researcher_agent_1_output_key}

*   **Substract:**
    {researcher_agent_2_output_key}

*   **Multiply:**
    {researcher_agent_3_output_key}

""",
    description="Combines research findings from parallel agents into a structured, cited report, strictly grounded on provided inputs.",
    # No tools needed for merging
    # No output_key needed here, as its direct response is the final output of the sequence
)


# --- 4. Create the SequentialAgent (Orchestrates the overall flow) ---
# This is the main agent that will be run. It first executes the ParallelAgent
# to populate the state, and then executes the MergerAgent to produce the final output.
parallel_pipeline_agent = SequentialAgent(
    name="ParallelPipeline",
    # Run parallel research first, then merge
    sub_agents=[parallel_research_agent, merger_agent],
    description="Coordinates parallel the results."
)

#root_agent = parallel_pipeline_agent

#storing the data in session or store so that other Agent can also take it.
agent_A = LlmAgent(name="AgentA", model=GEMINI_MODEL,instruction="Find the capital of France.", output_key="capital_city")
agent_B = LlmAgent(name="AgentB", model=GEMINI_MODEL, instruction="Tell me about the city stored in {capital_city}.")

pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])

#root_agent=pipeline


# Conceptual Setup: LLM Transfer

booking_agent = LlmAgent(name="Booker", description="Handles flight and hotel bookings.")
info_agent = LlmAgent(name="Info", description="Provides general information and answers questions.")

coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    instruction="You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
    description="Main coordinator.",
    # AutoFlow is typically used implicitly here
    sub_agents=[booking_agent, info_agent]
)
# If coordinator receives "Book a flight", its LLM should generate:
# FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
# ADK framework then routes execution to booking_agent.
#root_agent=coordinator


# Conceptual Setup: Agent as a Tool
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import agent_tool
from pydantic import BaseModel

# Define a target agent (could be LlmAgent or custom BaseAgent)
class ImageGeneratorAgent(BaseAgent): # Example custom agent
    name: str = "ImageGen"
    description: str = "Generates an image based on a prompt."
    # ... internal logic ...
    async def _run_async_impl(self, ctx): # Simplified run logic
        prompt = ctx.session.state.get("image_prompt", "default prompt")
        print("Generating prompt ...",prompt)
        # ... generate image bytes ...
        image_bytes = b"..."
        yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))

image_agent = ImageGeneratorAgent()
image_tool = agent_tool.AgentTool(agent=image_agent) # Wrap the agent

# Parent agent uses the AgentTool
artist_agent = LlmAgent(
    name="Artist",
    model="gemini-2.0-flash",
    instruction="Create a prompt and use the ImageGen tool to generate the image.",
    tools=[image_tool] # Include the AgentTool
)
# Artist LLM generates a prompt, then calls:
# FunctionCall(name='ImageGen', args={'image_prompt': 'a cat wearing a hat'})
# Framework calls image_tool.run_async(...), which runs ImageGeneratorAgent.
# The resulting image Part is returned to the Artist agent as the tool result.

#root_agent=artist_agent

# Conceptual Code: Iterative Code Refinement
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# Agent to generate/refine code based on state['current_code'] and state['requirements']
code_refiner = LlmAgent(
    name="CodeRefiner",
    model="gemini-2.0-flash",
    instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
    output_key="current_code" # Overwrites previous code in state
)

# Agent to check if the code meets quality standards
quality_checker = LlmAgent(
    name="QualityChecker",
    model="gemini-2.0-flash",
    instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
    output_key="quality_status"
)

# Custom agent to check the status and escalate if 'pass'
class CheckStatusAndEscalate(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("quality_status", "fail")
        should_stop = (status == "pass")
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

refinement_loop = LoopAgent(
    name="CodeRefinementLoop",
    max_iterations=5,
    sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
)
# Loop runs: Refiner -> Checker -> StopChecker
# State['current_code'] is updated each iteration.
# Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
#root_agent=refinement_loop

from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

stream_agent = Agent(
   # A unique name for the agent.
   name="basic_search_agent",
   # The Large Language Model (LLM) that agent will use.
   # Please fill in the latest model id that supports live from
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
   model="gemini-2.0-flash-exp",  # for example: model="gemini-2.0-flash-live-001" or model="gemini-2.0-flash-live-preview-04-09" or "gemini-2.0-flash-001"
   # A short description of the agent's purpose.
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="You are an expert researcher. You always stick to the facts.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search]
)


#root_agent=stream_agent

#Connecting External MCPServer

import warnings
warnings.filterwarnings(
    "ignore",
    message='Field name "config_type" in "SequentialAgent" shadows an attribute in parent "BaseAgent"',
    category=UserWarning,
    module="pydantic._internal._fields"
)
import asyncio
from fastmcp import Client
from typing import Any
from google.genai import types
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def get_mcp_data(object_id: str) -> dict:
    """Fetches an object by its ID from the MCP server."""
    print(f"Tool 'get_mcp_data' called with object_id: {object_id}")
    async with Client("http://127.0.0.1:8001/mcp") as client:
        single = await client.call_tool("get_object_by_id", {"object_id": object_id})
        print("Fetched single:", single)
        return single
        
call_mcp_server_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    description="This agent is used to get data using FASTMCP client by calling the FASTMCP server ",
    instruction="""Help user to fetch the data from the FASTMCP Server using FASTMCP Client.
    When the user asks to fetch data for a specific object ID, use the `get_mcp_data` tool and pass the ID to it.
    """,
    tools=[get_mcp_data],
)
    
 
#root_agent=call_mcp_server_agent    

#connecting local MCP

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Example: Define a command to run a local MCP server.
# In this case, we're assuming there's a script 'mcp_server.py'
# that you can run with a Python interpreter.
server_command = 'python'
server_args = ['my_server.py']

# Define the connection parameters for the stdio server.
stdio_connection_params = StdioServerParameters(
    command=server_command,
    args=server_args
)

# Create an MCPToolset instance with the stdio connection parameters.
# The toolset will handle the connection and tool discovery.
mcp_toolset = MCPToolset(
    connection_params=stdio_connection_params
)

# Initialize your LlmAgent and provide the MCPToolset as a tool.
# This makes the tools from the MCP server available to the agent.
my_agent = LlmAgent(
    model='gemini-2.0-flash',  # Specify the model you want to use
    name='my_mcp_agent',
    instruction='I am a helpful agent that can use the tools from my MCP server.',
    tools=[mcp_toolset]
)

# You can now use this 'my_agent' in your application with the Runner.
# The Runner will manage the lifecycle of the agent and its tools.

#Connecting local MCP server
import warnings
warnings.filterwarnings(
    "ignore",
    message='Field name "config_type" in "SequentialAgent" shadows an attribute in parent "BaseAgent"',
    category=UserWarning,
    module="pydantic._internal._fields"
)
import asyncio
from fastmcp import Client
from typing import Any
from google.genai import types
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def get_mcp_data(object_id: str) -> dict:
    """Fetches an object by its ID from the MCP server."""
    print(f"Tool 'get_mcp_data' called with object_id: {object_id}")
    async with Client("restapi-mcp-server.py") as client:
        single = await client.call_tool("get_object_by_id", {"object_id": object_id})
        print("Fetched single:", single)
        return single
        
call_local_mcp_server_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    description="This agent is used to get data using FASTMCP client by calling the FASTMCP server ",
    instruction="""Help user to fetch the data from the FASTMCP Server using FASTMCP Client.
    When the user asks to fetch data for a specific object ID, use the `get_mcp_data` tool and pass the ID to it.
    """,
    tools=[get_mcp_data],
)

#root_agent=call_local_mcp_server_agent


#calling MCPServer having integrated ADK agent

import asyncio
from fastmcp import Client
from typing import Any
from google.genai import types
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def get_mcp_data(object_id: str) -> dict:
    """Fetches an object by its ID from the MCP server."""
    print(f"Tool 'get_mcp_data' called with object_id: {object_id}")
    # async with Client("restapi-mcp-server.py") as client:
    #     single = await client.call_tool("get_object_by_id", {"object_id": object_id})
    #     print("Fetched single:", single)
    #     return single
    async with Client("http://127.0.0.1:8001/mcp") as client:
        single = await client.call_tool("get_objects_by_ids_using_adk_agent")
        print("Fetched single:", single)
        return single
        
call_local_mcp_adk_server_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    description="This agent is used to get data using FASTMCP client by calling the FASTMCP server ",
    instruction="""Help user to fetch the data from the FASTMCP Server using FASTMCP Client.
    When the user asks to fetch data for a specific object ID, use the `get_mcp_data` tool and pass the ID to it.
    """,
    tools=[get_mcp_data],
)

#root_agent=call_local_mcp_adk_server_agent


#calling restapi-mcp-adk-server having integrated ADK agent

import asyncio
from fastmcp import Client
from typing import Any
from google.genai import types
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def get_mcp_adk_data(object_id: str) -> dict:
    """Fetches an object by its ID from the MCP server."""
    print(f"Tool 'get_mcp_data' called with object_id: {object_id}")
    # async with Client("restapi-mcp-server.py") as client:
    #     single = await client.call_tool("get_object_by_id", {"object_id": object_id})
    #     print("Fetched single:", single)
    #     return single
    async with Client("restapi-mcp-adk-server.py") as client:
        single = await client.call_tool("get_objects_by_id_using_adk_agent", {"object_id": object_id})
        print("Fetched single:", single)
        return single
        
call_local_mcp_adk_server_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    description="This agent is used to get data using FASTMCP client by calling the FASTMCP server ",
    instruction="""Help user to fetch the data from the FASTMCP Server using FASTMCP Client.
    When the user asks to fetch data for a specific object ID, use the `get_mcp_data` tool and pass the ID to it.
    """,
    tools=[get_mcp_adk_data],
)

root_agent=call_local_mcp_adk_server_agent