import asyncio
from typing import Any
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types
import time

APP_NAME = "human_in_the_loop"
USER_ID = "1234"
SESSION_ID = "session1234"
    
# Define a long-running tool
def generate_large_report(user_id: str) -> str:
    """
    Simulates a long-running report generation task.
    """
    time.sleep(10)  # Simulate a time-consuming task
    print("generate_large_report called")
    return f"✅ Report for user is ready!"

def normalFunction()-> str:
    print("normalFunction called")
    return f"this is normal function that will execute when the generate large report tool is still excuting"

long_running_tool = LongRunningFunctionTool(func=generate_large_report)    
    
generate_report_agent = Agent(
    # Use a model compatible with function calling
    model="gemini-2.0-flash-001",
    name='generate_report_agent',
    instruction="""
      Helps users generate detailed reports. Till the report is generated execute normalFunction
    """,
    tools=[generate_large_report,normalFunction]
	)    
    
    


# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=generate_report_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text    
    
    return final_response

# # Main async function to run the examples
# async def main():
#     await call_agent_async("a lonely robot finding a friend in a junkyard")
    
    
# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# # If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
if __name__ == "__main__":
    asyncio.run(call_agent_async("Create long report for user_id 1234 and if long_running_tool taking long time execute normalFunction"))
  