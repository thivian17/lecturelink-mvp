import json
from typing import Dict
import os

def save_report_locally(
    report_json: str,
    meeting_id: str
) -> Dict[str, str]:
    """
    Saves meeting report to local filesystem.
    
    Args:
        report_json: JSON string of the meeting report
        meeting_id: Unique identifier for the meeting
        
    Returns:
        Dictionary with storage status and path
    """
    try:
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Save the report
        filename = f"reports/{meeting_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_json)
        
        full_path = os.path.abspath(filename)
        
        return {
            "status": "success",
            "message": f"Report saved successfully to {filename}",
            "path": full_path
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }