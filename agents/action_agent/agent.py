from google.adk.agents import Agent
from tools.local_storage import save_report_locally

action_agent = Agent(
    name="meeting_action_executor",
    model="gemini-2.5-flash",
    description="Saves meeting reports locally",
    
    instruction="""You are a Meeting Action Executor. You receive structured meeting reports 
    and save them to the local filesystem.
    
    YOUR WORKFLOW:
    1. Read the structured report from the session state (key: 'structured_report')
    2. Save the report locally using save_report_locally tool
    3. Confirm the action completed successfully with the file path
    
    Be professional and thorough in your execution.""",
    
    tools=[save_report_locally]
)