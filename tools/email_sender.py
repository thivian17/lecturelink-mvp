from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from typing import Dict, List
import json

def send_report_email(
    recipient_emails: List[str],
    report_json: str,
    meeting_title: str
) -> Dict[str, str]:
    """
    Sends meeting report via email using SendGrid.
    
    Args:
        recipient_emails: List of email addresses
        report_json: JSON string of the meeting report
        meeting_title: Title of the meeting
        
    Returns:
        Dictionary with send status
    """
    try:
        # Parse the report
        report = json.loads(report_json)
        
        # Create HTML email body
        html_content = f"""
        <html>
        <body>
            <h2>{report['meeting_title']}</h2>
            <p><strong>Date:</strong> {report['date']}</p>
            <p><strong>Attendees:</strong> {', '.join(report['attendees'])}</p>
            
            <h3>Summary</h3>
            <p>{report['summary']}</p>
            
            <h3>Key Topics</h3>
            <ul>
                {''.join([f'<li>{topic}</li>' for topic in report['key_topics']])}
            </ul>
            
            <h3>Action Items</h3>
            <ul>
                {''.join([
                    f"<li><strong>{item['task']}</strong> - "
                    f"Assigned to: {item.get('assignee', 'Unassigned')} - "
                    f"Priority: {item['priority']}</li>"
                    for item in report['action_items']
                ])}
            </ul>
            
            <h3>Decisions Made</h3>
            <ul>
                {''.join([f'<li>{decision}</li>' for decision in report.get('decisions_made', [])])}
            </ul>
        </body>
        </html>
        """
        
        # Send email
        message = Mail(
            from_email='noreply@sendgrid.net',  
            to_emails=recipient_emails,
            subject=f"Meeting Report: {meeting_title}",
            html_content=html_content
        )
        
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        return {
            "status": "success",
            "message": f"Report sent to {len(recipient_emails)} recipients"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }