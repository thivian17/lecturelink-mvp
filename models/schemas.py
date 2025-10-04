from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ActionItem(BaseModel):
    """Represents a single action item from the meeting."""
    task: str = Field(description="Description of the task to be done")
    assignee: Optional[str] = Field(
        description="Person responsible for the task",
        default=None
    )
    deadline: Optional[str] = Field(
        description="Due date for the task",
        default=None
    )
    priority: str = Field(
        description="Priority level: high, medium, or low",
        default="medium"
    )

class MeetingReport(BaseModel):
    """Complete structured meeting report."""
    meeting_title: str = Field(description="Title or subject of the meeting")
    date: str = Field(description="Date of the meeting")
    attendees: List[str] = Field(
        description="List of meeting participants"
    )
    summary: str = Field(
        description="Brief 2-3 sentence summary of the meeting"
    )
    key_topics: List[str] = Field(
        description="Main topics discussed in the meeting"
    )
    action_items: List[ActionItem] = Field(
        description="List of action items and next steps"
    )
    decisions_made: List[str] = Field(
        description="Key decisions reached during the meeting",
        default=[]
    )