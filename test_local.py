import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from agents.workflow import root_agent
from google.genai import types
from dotenv import load_dotenv
import os

# Force reload environment variables
load_dotenv(override=True)

# Verify SendGrid key is loaded
if not os.getenv('SENDGRID_API_KEY'):
    print("WARNING: SENDGRID_API_KEY not found in environment!")
else:
    print(f"SendGrid key loaded: {os.getenv('SENDGRID_API_KEY')[:10]}...")

async def test_agent():
    # Initialize services
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    
    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service,
        memory_service=memory_service
    )
    
    # Create session
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test-123"
    )
    
    # Test transcript
    test_transcript = """
    Meeting between Alice and Bob on October 3rd, 2025.
    Alice: Let's discuss the Q4 product launch.
    Bob: Agreed. We need to finalize the marketing campaign by next Friday.
    Alice: I'll handle the social media strategy. Bob, can you work on the email campaign?
    Bob: Yes, I'll have the draft ready by Tuesday.
    Alice: Great. We also decided to increase the budget by 15%.
    """
    
    # Run agent
    message = types.Content(
        role='user',
        parts=[types.Part(text=f"Analyze this transcript:\n\n{test_transcript}")]
    )
    
    print("Running agent workflow...")
    print("=" * 60)
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test-123",
        new_message=message
    ):
        # Print all events for debugging
        print(f"\nEvent type: {type(event).__name__}")
        
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"Content: {part.text[:200]}...")  # First 200 chars
        
        # Check if this is the final response
        if hasattr(event, 'is_final_response') and event.is_final_response():
            print("\n" + "=" * 60)
            print("=== FINAL RESPONSE ===")
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text)
            print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_agent())