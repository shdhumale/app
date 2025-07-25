import time
from google.adk.tools import LongRunningFunctionTool
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Define a long-running function
def long_running_function():
    from time import sleep
    print("Long-running function: Task started")
    sleep(5)  # Simulate long-running operation
    print("Long-running function: Task completed")
    return "long_running_function completed"

def ordinaryfuction():
    print("ordinaryfuction called >>>>>>>>>>>>>>>>>>>>>")
    return "ordinaryfuction called >>>>>>>>>>>>>>>>>>>>>"


# 2️⃣ Wrap it using LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=long_running_function)


# 3️⃣ Create an agent that can use this tool
agent = Agent(
    model="gemini-2.0-flash-001",
    name="file_processor_agent",
    instruction=(
        "You are a long running agent. "        
    ),
    tools=[long_running_tool,ordinaryfuction]
)

APP_NAME = "file_processor_agent"
USER_ID = "1234"
SESSION_ID = "session1234"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# 5️⃣ Helper to invoke the agent
async def call_agent(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    async for event in events:
        if event.content and event.content.parts:
            if text := "".join(part.text or "" for part in event.content.parts):
                print(f"[{event.author}]: {text}")

# 6️⃣ Execute


if __name__ == "__main__":
    asyncio.run(call_agent("if long_running_function is taking long time to execute till then reply using tool ordinaryfuction and when long_running_function completed say Task is completed from my side"))
