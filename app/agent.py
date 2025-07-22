from google.adk.agents import LlmAgent

# def get_content(content: str):
#     print(type(content))
#     return {"content": content}
root_agent = LlmAgent(
        model='gemini-2.5-flash-preview-05-20',
        name='recruiter_agent',       
        instruction=(
            
            """You are a recruiter. Evaluate this resume and score it from 0 to 10 for the following job:

            Job: Data Scientist
            Requirements:
            - Python and SQL skills
            - Experience with ML or Data Analysis
            - Clear communication

          Return ONLY a score (0-10) and a one-line explanation."""

        )
        #tools=[get_content],
    )
    