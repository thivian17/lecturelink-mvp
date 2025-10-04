import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from agents.workflow import root_agent
from tools.transcription import transcribe_audio
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
import uuid
import tempfile
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LectureLink - Meeting Transcription",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ LectureLink - AI Meeting Transcription")
st.markdown("Upload audio, get structured reports with action items!")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize services
@st.cache_resource
def initialize_services():
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    
    runner = Runner(
        agent=root_agent,
        app_name="lecturelink_app",
        session_service=session_service,
        memory_service=memory_service
    )
    
    return runner, session_service

runner, session_service = initialize_services()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Upload a meeting recording and AI will analyze it!")
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    if os.path.exists("reports"):
        report_count = len([f for f in os.listdir("reports") if f.endswith('.json')])
        st.metric("Reports Generated", report_count)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Audio")
    
    # File uploader
    audio_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'ogg'],
        help="Supported: WAV, MP3, M4A, OGG"
    )
    
    if audio_file:
        st.audio(audio_file)
        
        # Optional meeting details
        with st.expander("📝 Meeting Details (Optional)"):
            meeting_title = st.text_input("Meeting Title", placeholder="Auto-generated if left blank")
            attendees = st.text_area("Attendees (one per line)", placeholder="Alice\nBob\nCarol")
        
        # Process button
        if st.button("🚀 Analyze Meeting", type="primary", use_container_width=True):
            
            with st.spinner("🔄 Processing..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                        tmp_file.write(audio_file.read())
                        tmp_path = tmp_file.name
                    
                    # Step 1: Transcribe audio
                    progress = st.progress(0)
                    status = st.empty()
                    
                    status.info("🎤 Step 1/3: Transcribing audio...")
                    progress.progress(33)
                    
                    transcription_result = transcribe_audio(tmp_path)
                    
                    if transcription_result['status'] != 'success':
                        st.error(f"❌ Transcription failed: {transcription_result.get('error_message')}")
                        st.stop()
                    
                    transcript = transcription_result['transcript']
                    
                    # Step 2: Analyze
                    status.info("🤖 Step 2/3: Analyzing transcript with AI...")
                    progress.progress(66)
                    
                    # Prepare context
                    context_parts = [f"Transcript:\n{transcript}"]
                    if meeting_title:
                        context_parts.insert(0, f"Meeting Title: {meeting_title}")
                    if attendees:
                        attendee_list = [a.strip() for a in attendees.split('\n') if a.strip()]
                        context_parts.insert(1 if meeting_title else 0, f"Attendees: {', '.join(attendee_list)}")
                    
                    user_message = "\n\n".join(context_parts)
                    
                    # Run agent
                    async def run_agent():
                        # Get or create session
                        session_id = st.session_state.session_id
                        
                        try:
                            await session_service.create_session(
                                app_name="lecturelink_app",
                                user_id="streamlit_user",
                                session_id=session_id
                            )
                        except:
                            pass  # Session might already exist
                        
                        # Run
                        content = types.Content(
                            role='user',
                            parts=[types.Part(text=user_message)]
                        )
                        
                        final_response = None
                        async for event in runner.run_async(
                            user_id="streamlit_user",
                            session_id=session_id,
                            new_message=content
                        ):
                            if hasattr(event, 'is_final_response') and event.is_final_response():
                                if hasattr(event, 'content') and event.content and event.content.parts:
                                    final_response = event.content.parts[0].text
                        
                        return final_response
                    
                    response = asyncio.run(run_agent())
                    
                    # Step 3: Complete
                    status.success("✅ Step 3/3: Analysis complete!")
                    progress.progress(100)
                    
                    # Store results
                    st.session_state.last_response = response
                    st.session_state.transcript = transcript
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    # Success message
                    st.success("🎉 Meeting analyzed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("🐛 Debug Info"):
                        st.code(traceback.format_exc())

with col2:
    st.header("📊 Results")
    
    if 'last_response' in st.session_state:
        
        # Show the report path
        st.success(st.session_state.last_response)
        
        # Try to load and display the report
        try:
            # Find the most recent report
            if os.path.exists("reports"):
                reports = sorted(
                    [f for f in os.listdir("reports") if f.endswith('.json')],
                    key=lambda x: os.path.getmtime(os.path.join("reports", x)),
                    reverse=True
                )
                
                if reports:
                    latest_report = reports[0]
                    report_path = os.path.join("reports", latest_report)
                    
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    # Display structured report
                    st.markdown("### 📋 Meeting Report")
                    
                    # Summary card
                    st.info(f"**{report_data['meeting_title']}**\n\n{report_data['summary']}")
                    
                    # Metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Attendees", len(report_data['attendees']))
                    with col_b:
                        st.metric("Topics", len(report_data['key_topics']))
                    with col_c:
                        st.metric("Action Items", len(report_data['action_items']))
                    
                    # Tabs for different sections
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📝 Summary", "👥 Attendees", "💡 Topics", "✅ Actions", "🎯 Decisions"
                    ])
                    
                    with tab1:
                        st.markdown(f"**Date:** {report_data['date']}")
                        st.markdown(report_data['summary'])
                    
                    with tab2:
                        for attendee in report_data['attendees']:
                            st.markdown(f"- {attendee}")
                    
                    with tab3:
                        for topic in report_data['key_topics']:
                            st.markdown(f"- {topic}")
                    
                    with tab4:
                        for item in report_data['action_items']:
                            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item['priority'], "⚪")
                            st.markdown(f"{priority_emoji} **{item['task']}**")
                            if item.get('assignee'):
                                st.markdown(f"  - Assigned to: {item['assignee']}")
                            if item.get('deadline'):
                                st.markdown(f"  - Deadline: {item['deadline']}")
                            st.markdown("")
                    
                    with tab5:
                        if report_data.get('decisions_made'):
                            for decision in report_data['decisions_made']:
                                st.markdown(f"- {decision}")
                        else:
                            st.info("No specific decisions recorded")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json.dumps(report_data, indent=2),
                        file_name=latest_report,
                        mime="application/json"
                    )
                    
                    # Show transcript
                    with st.expander("📜 View Transcript"):
                        if 'transcript' in st.session_state:
                            st.text_area("Transcript", st.session_state.transcript, height=200)
        
        except Exception as e:
            st.error(f"Could not load report: {e}")
            
    else:
        st.info("👆 Upload an audio file to get started!")
        
        # Show sample
        st.markdown("### 🎯 What You'll Get:")
        st.markdown("""
        - **Structured Summary** - Concise overview of the meeting
        - **Key Topics** - Main discussion points
        - **Action Items** - Tasks with assignees and deadlines
        - **Decisions Made** - Important conclusions
        - **Full Transcript** - Complete text version
        """)

# Footer
st.markdown("---")
st.markdown("Built with Google ADK, Streamlit, and Gemini 2.5 | LectureLink MVP")