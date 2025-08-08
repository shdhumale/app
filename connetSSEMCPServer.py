import warnings

# The following warning is a known issue in the ADK library and can be safely ignored.
# It occurs because the `SequentialAgent` class in ADK re-defines a field
# that is already present in its parent `BaseAgent` class.
warnings.filterwarnings(
    "ignore",
    message='Field name "config_type" in "SequentialAgent" shadows an attribute in parent "BaseAgent"',
    category=UserWarning,
    module="pydantic._internal._fields"
)
# from google.adk import MCPToolset, SseServerParams
# from fastmcp import Client

# #pip install google-adk==0.3.0 mcp[cli]==1.5.0 requests
# #pip install google-adk mcp[cli] requests
# # Define the MCP server endpoint
# mcp_server_url = "http://127.0.0.1:8000/mcp"  # Replace with your MCP server URL

# # Create the MCP toolset using SSE
# mcp_toolset = MCPToolset(
#     server_params=SseServerParams(
#         server_url=mcp_server_url,
#         toolset_name="external_tools"  # Optional: name for the toolset
#     )
# )

# # Define your agent with the MCP toolset
# agent = Agent(
#     name="MyADKAgent",
#     tools=[mcp_toolset]
# )

# # Run the agent
# if __name__ == "__main__":
#     agent.run()

##Wrong code start
# from google_adk.llm_agent import LlmAgent
# from google_adk.mcp.toolset import MCPToolset
# from google_adk.mcp.server_parameters import StdioServerParameters # or SseServerParams for remote
 
# # Configure the connection to your MCP server
# server_params = StdioServerParameters(
#   command=["python", "local_mcp/server.py"], # Replace with your server command
#   # ... other parameters like arguments, etc.
# )
 
# # Initialize the MCPToolset
# mcp_toolset = MCPToolset(server_parameters=server_params)
 
# # Initialize the LlmAgent, passing in the toolset
# llm_agent = LlmAgent(
#   mcp_toolset=mcp_toolset,
#   # ... other agent configurations like LLM, prompt, etc.
# )
 
# # Now you can use the agent, and it will automatically use the connected tools!
 
 
# =========================
 
# # File agent.py
 
# import asyncio
# import json
# from typing import Any
 
# from dotenv import load_dotenv
# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.artifacts.in_memory_artifact_service import (
#     InMemoryArtifactService,  # Optional
# )
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.adk.tools.mcp_tool.mcp_toolset import (
#     MCPToolset,
#     SseServerParams,
# )
# from google.genai import types
# from rich import print
# load_dotenv()
 
# async def get_tools_async():
#     """Gets tools from the File System MCP Server."""
#     tools, exit_stack = await MCPToolset.from_server(
#         connection_params=SseServerParams(
#             url="http://localhost:8001/sse",
#         )
#     )
#     print("MCP Toolset created successfully.")
#     return tools, exit_stack
 
# async def get_agent_async():
#     """Creates an ADK Agent equipped with tools from the MCP Server."""
#     tools, exit_stack = await get_tools_async()
#     print(f"Fetched {len(tools)} tools from MCP server.")
#     root_agent = LlmAgent(
#         model="gemini-2.0-flash",
#         name="assistant",
#         instruction="""Help user extract and summarize the article from wikipedia link.
#         Use the following tools to extract wikipedia article:
#         - extract_wikipedia_article
 
#         Once you retrieve the article, always summarize it in a few sentences for the user.
#         """,
#         tools=tools,
#     )
#     return root_agent, exit_stack
 
# root_agent = get_agent_async()
 
# ==============
 
# from adk.agent import Agent
# from adk.mcp import MCPTool
 
# # Define the external MCP server URL
# MCP_SERVER_URL = "http://localhost:8000"  # Replace with your actual MCP server URL
 
# # Create the agent
# agent = Agent(
#     name="UtilityAgent",
#     description="An agent that provides weather updates and currency conversion using an external MCP server.",
#     tools=[
#         MCPTool(
#             url=MCP_SERVER_URL,
#             tools=["get_weather_info", "convert_currency"]
#         )
#     ]
# )
 
# # Run the agent
# if __name__ == "__main__":
#     agent.run()
##Wrong code end

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

APP_NAME = "CALL_MCP_SERVER"
USER_ID = "1234"
SESSION_ID = "session1234"

async def get_mcp_data(object_id: str) -> dict:
    """Fetches an object by its ID from the MCP server."""
    print(f"Tool 'get_mcp_data' called with object_id: {object_id}")
    async with Client("http://127.0.0.1:8000/mcp") as client:
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
    
# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=call_mcp_server_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner
 
async def get_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "Agent did not produce a final response."
    async for event in events:
        # You can uncomment the following line to see the full event flow for debugging
        # print(f"DEBUG Event: {event.model_dump_json(indent=2, exclude_none=True)}")
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    
    return final_response

 
if __name__ == "__main__":
    final_result = asyncio.run(get_agent_async("Fetch the data for object_id 2"))
    print(f"\n--- Script Finished ---\nFinal returned value: {final_result}")