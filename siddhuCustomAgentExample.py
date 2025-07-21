import asyncio
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

class MyCustomAgent(BaseAgent):
    """
    An example of a custom agent in Google ADK.
    This agent demonstrates basic interaction and state management.
    """
    name: str = "MyCustomAgent"
    description: str = "A custom agent that processes user input and responds."

    async def _run_async_impl(self, ctx: InvocationContext):
        """
        Implements the core logic of the custom agent.
        This method is called when the agent is invoked.
        """
        # Access user input from the context
        # user_input = ""
        # if ctx.new_message and ctx.new_message.parts:
        #     user_input = ctx.new_message.parts[0].text
        user_input = ctx.user_content.parts[0].text
        # Perform custom logic based on the input
        if "hello" in user_input.lower():
            response_content = "Hello there! How can I help you today?"
        else:
            response_content = f"You said: '{user_input}'. I'm a custom agent and can process this further."

        # Update session state if necessary
        ctx.session.state["last_response"] = response_content

        # Yield an Event to send a response back
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=response_content)])
        )

# To use this agent, you would typically integrate it within an ADK application
# and potentially set up a runner to handle interactions.
# For example:

async def main():
    my_agent = MyCustomAgent()
    session_service = InMemorySessionService()
    # It's good practice to provide an app_name to the Runner.
    runner = Runner(agent=my_agent, session_service=session_service, app_name="MyCustomApp")

    # To run a query (in a simplified interactive environment):
    user_query = "hi, custom agent!"
    user_id = "user123"
    session_id = "session456"

    # Create a session first
    await session_service.create_session(
        app_name="MyCustomApp", user_id=user_id, session_id=session_id
    )

    # The user query is passed as new_message
    content = types.Content(parts=[types.Part(text=user_query)], role="user")
    print (content)

    print(f"--- Running query: {user_query} ---")
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent > {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())