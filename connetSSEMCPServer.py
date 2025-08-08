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