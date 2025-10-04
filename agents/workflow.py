from google.adk.agents import SequentialAgent
from agents.analyst_agent.agent import analyst_agent
from agents.action_agent.agent import action_agent

# Sequential Workflow - Orchestrates the two agents
meeting_workflow = SequentialAgent(
    name="meeting_transcription_workflow",
    description="Complete workflow: analyze transcript → execute actions",
    
    sub_agents=[
        analyst_agent,    # Runs FIRST - creates structured report
        action_agent      # Runs SECOND - executes actions with tools
    ]
)

# This is the root agent that ADK will run
root_agent = meeting_workflow