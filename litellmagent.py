import warnings
import asyncio

# The following warning is a known issue in the ADK library and can be safely ignored.
# It occurs because the `SequentialAgent` class in ADK re-defines a field
# that is already present in its parent `BaseAgent` class.
warnings.filterwarnings(
    "ignore",
    message='Field name "config_type" in "SequentialAgent" shadows an attribute in parent "BaseAgent"',
    category=UserWarning,
    module="pydantic._internal._fields",
)
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Define the Ollama model to be used.
# The format is "ollama_chat/model_name"
# Ensure the model is running on your local machine.
ollama_model = LiteLlm(model="ollama_chat/gemma3:1b")

# Create a simple agent using the Ollama model.
# You can give your agent a name and instructions.
ollama_agent = Agent(
    name="LocalOllamaAgent",
    model=ollama_model,
    instruction="You are a helpful assistant that uses a local Ollama model to answer questions."
)

async def main():
    """Sets up the runner and session to interact with the agent."""
    # Define session details
    app_name = "ollama_app"
    user_id = "user1"
    session_id = "session1"

    # Create a session service and a runner
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=ollama_agent, app_name=app_name, session_service=session_service)

    # Prepare the user's message
    query = "What's the capital of France?"
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(f"User: {query}")

    # Run the agent asynchronously and get the response
    final_response = "Agent did not produce a final response."
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text.strip()
            break  # Stop after getting the final response

    # Print the agent's response.
    print(f"Agent: {final_response}")

# Execute the main async function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure your local Ollama server is running and the 'gemma3:1b' model is available.")