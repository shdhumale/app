# rest_api_server.py
from fastmcp import FastMCP, Context
import httpx
import asyncio
from fastmcp import Client
import google.genai as genai
from typing import Any
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

mcp = FastMCP(
    name="RESTful API Wrapper 🌐",
)

BASE_URL = "https://api.restful-api.dev/objects"

APP_NAME = "MCP_SERVER_WITH_ADK_AGENT"
USER_ID = "1234"
SESSION_ID = "session1234"

'''
async def get_objects_by_ids(ids: list[str], ctx: Context):
    query = "&".join([f"id={i}" for i in ids])
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}?{query}")
        print("get_objects_by_ids",resp.json())
    return resp.json()
        
'''
async def get_object_by_id(object_id: str):
   async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/{object_id}")
        print("get_object_by_id",resp.json())
        return resp.json()

call_mcp_server_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="assistant",
    description="This agent is used to send data to FASTMCP client",
    instruction="""Help user to fetch the data from the RESTAPI and send it to the FASTMCP Client.
    When the user asks to fetch data for a specific object ID, use the `get_object_by_id` tool and pass the ID to it.
    """,
    tools=[get_object_by_id],
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    if call_mcp_server_agent:
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
            #print final_response
            print(f"final_response",final_response)
    return final_response
    
@mcp.tool()
async def get_objects_by_id_using_adk_agent(object_id: str,ctx: Context):
    print(f"object_id:::::::::::::::::",object_id)
    final_result = await get_agent_async(f"Fetch the data for object_id {object_id}, pass the id to get_object_by_id tool")
    return final_result

if __name__ == "__main__":
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8001, path="/mcp")
    mcp.run()
