from google.adk.agents import Agent
from models.schemas import MeetingReport
import os

# Analyst Agent - Uses output_schema, NO TOOLS
analyst_agent = Agent(
    name="meeting_analyst",
    model="gemini-2.5-flash",  # Fast and efficient for MVP
    description="Analyzes meeting transcripts and creates structured reports",
    
    instruction="""You are a Meeting Analysis Expert. Your job is to analyze meeting transcripts 
    and create comprehensive, structured reports.
    
    GUIDELINES:
    - Extract the meeting title from context or create a descriptive one
    - Identify all participants mentioned in the transcript
    - Write a concise 2-3 sentence summary
    - List 3-5 key topics that were discussed
    - Extract ALL action items with assignees and deadlines when mentioned
    - Note any important decisions made
    - Use professional, clear language
    
    CRITICAL: You MUST return valid JSON matching the MeetingReport schema. 
    Do not add any text before or after the JSON.
    
    If the transcript mentions previous meetings or context, reference that information
    to make your report more comprehensive.""",
    
    output_schema=MeetingReport,  # Forces structured output
    output_key="structured_report"  # Saves to session state
    
    # NOTE: No tools! output_schema agents cannot use tools
)