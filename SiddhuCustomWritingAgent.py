# Full runnable code for the StoryFlowAgent example
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from pydantic import BaseModel, Field

# --- Constants ---
APP_NAME = "story_app"
USER_ID = "12345"
SESSION_ID = "123344"
GEMINI_2_FLASH = "gemini-2.0-flash"

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Orchestrator Agent ---
class StoryFlowAgent(BaseAgent):
    """
    Custom agent for a story generation and refinement workflow.

    This agent orchestrates a sequence of LLM agents to generate a story,
    critique it, revise it, check grammar and tone, and potentially
    regenerate the story if the tone is negative.
    """

    # --- Field Declarations for Pydantic ---
    # Declare the agents passed during initialization as class attributes with type hints
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        Initializes the StoryFlowAgent.

        Args:
            name: The name of the agent.
            story_generator: An LlmAgent to generate the initial story.
            critic: An LlmAgent to critique the story.
            reviser: An LlmAgent to revise the story based on criticism.
            grammar_check: An LlmAgent to check the grammar.
            tone_check: An LlmAgent to analyze the tone.
        """
        # Create internal agents *before* calling super().__init__
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # Define the sub_agents list for the framework
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic will validate and assign them based on the class annotations.
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # Pass the sub_agents list directly
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the story workflow.
        Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
        """
        logger.info(f"[{self.name}] Starting story generation workflow.")

        # 1. Initial Story Generation
        logger.info(f"[{self.name}] Running StoryGenerator...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] Event from StoryGenerator: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # Check if story was generated before proceeding
        if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
             logger.error(f"[{self.name}] Failed to generate initial story. Aborting workflow.")
             return # Stop processing if initial story failed

        logger.info(f"[{self.name}] Story state after generator: {ctx.session.state.get('current_story')}")


        # 2. Critic-Reviser Loop
        logger.info(f"[{self.name}] Running CriticReviserLoop...")
        # Use the loop_agent instance attribute assigned during init
        async for event in self.loop_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from CriticReviserLoop: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        logger.info(f"[{self.name}] Story state after loop: {ctx.session.state.get('current_story')}")

        # 3. Sequential Post-Processing (Grammar and Tone Check)
        logger.info(f"[{self.name}] Running PostProcessing...")
        # Use the sequential_agent instance attribute assigned during init
        async for event in self.sequential_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from PostProcessing: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # 4. Tone-Based Conditional Logic
        tone_check_result = ctx.session.state.get("tone_check_result")
        logger.info(f"[{self.name}] Tone check result: {tone_check_result}")

        if tone_check_result == "negative":
            logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] Event from StoryGenerator (Regen): {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event
        else:
            logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")
            pass

        logger.info(f"[{self.name}] Workflow finished.")

# --- Define the individual LLM agents ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""You are a story writer. Write a short story (around 100 words), on the following topic: {topic}""",
    input_schema=None,
    output_key="current_story",  # Key for storing output in session state
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.""",
    input_schema=None,
    output_key="criticism",  # Key for storing criticism in session state
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.""",
    input_schema=None,
    output_key="current_story",  # Overwrites the original story
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.""",
    input_schema=None,
    output_key="tone_check_result", # This agent's output determines the conditional flow
)

# --- Create the custom agent instance ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "a brave kitten exploring a haunted house"}

# --- Setup Runner and Session ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"Initial session state: {session.state}")
    runner = Runner(
        agent=story_flow_agent, # Pass the custom orchestrator agent
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- Function to Interact with the Agent ---
async def call_agent_async(user_input_topic: str):
    """
    Sends a new topic to the agent (overwriting the initial one if needed)
    and runs the workflow.
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("Session not found!")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"Updated session state topic to: {user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"Generate a story about: {user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("Final Session State:")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")


# Main async function to run the examples
async def main():
    await call_agent_async("a lonely robot finding a friend in a junkyard")
    
    
# --- Run the Agent ---
# Note: In Colab, you can directly use 'await' at the top level.
# # If running this code as a standalone Python script, you'll need to use asyncio.run() or manage the event loop.
if __name__ == "__main__":
    asyncio.run(call_agent_async("a lonely robot finding a friend in a junkyard"))

# # Execute the main async function
# try:
#     asyncio.run(main())
# except RuntimeError as e:   
#         raise e  # Re-raise other runtime errors