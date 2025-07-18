# @title 1. Initialize New Session Service and State
import asyncio # Ensure asyncio is imported
# Import necessary session components
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
import types
from typing import Any, Dict, List, Optional

# root_agent_var_name = 'root_agent' # Default name from Step 3 guide

# if root_agent_var_name:
async def run_async_stateful_conversation():

    # Create a NEW session service instance for this state demonstration
    session_service_stateful = InMemorySessionService()
    print("✅ New InMemorySessionService created for state demonstration.")

    # Define a NEW session ID for this part of the tutorial
    SESSION_ID_STATEFUL = "session_state_demo_001"
    USER_ID_STATEFUL = "user_state_demo"

    # Define initial state data - user prefers Celsius initially
    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }

    # Create the session, providing the initial state
    session_stateful = await session_service_stateful.create_session(
        app_name="Siddharatha applicaiton", # Use the consistent app name
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
        state=initial_state # <<< Initialize state during creation
    )
    print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

    # Verify the initial state was set correctly
    retrieved_session = await session_service_stateful.get_session(app_name="Siddharatha applicaiton",
                                                            user_id=USER_ID_STATEFUL,
                                                            session_id = SESSION_ID_STATEFUL)
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")
        
def get_weather_stateful(city: str, tool_context: ToolContext) -> Optional[Dict[str, Any]]:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")
        
if __name__ == "__main__": # Ensures this runs only when script is executed directly
    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
    try:
        # This creates an event loop, runs your async function, and closes the loop.
        asyncio.run(run_async_stateful_conversation())

        # To test the get_weather_stateful tool function directly, a ToolContext
        # object must be provided, as the function signature requires it.
        # This simulates how the ADK runner provides context to a tool during execution.
        print("\n--- Testing get_weather_stateful directly with a mock context ---")
        # We can initialize a ToolContext with a state dictionary to test different scenarios.
        # The ToolContext is initialized empty, and then its `state` attribute,
        # which is a dictionary, is set directly. This simulates the session
        # state that the ADK would provide during a real agent run.
        # The ToolContext requires an `invocation_context` object that has a `session`
        # attribute, which in turn has a `state` dictionary. We can simulate this
        # structure using `types.SimpleNamespace` for testing.

        # 1. Create a mock session object with the desired state.
        mock_session = types.SimpleNamespace()
        mock_session.state = {"user_preference_temperature_unit": "Fahrenheit"}

        # 2. Create a mock invocation context that holds the mock session.
        mock_invocation_context = types.SimpleNamespace()
        mock_invocation_context.session = mock_session

        # 3. Initialize ToolContext with the fully formed mock invocation context.
        mock_context = ToolContext(invocation_context=mock_invocation_context)
        get_weather_stateful("newyork", tool_context=mock_context)
    except Exception as e:
        print(f"An error occurred: {e}")   