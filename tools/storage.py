from google.cloud import storage
import json
from typing import Dict
import os
from datetime import timedelta

def save_report_to_storage(
    report_json: str,
    meeting_id: str
) -> Dict[str, str]:
    """
    Saves meeting report to Google Cloud Storage.
    
    Args:
        report_json: JSON string of the meeting report
        meeting_id: Unique identifier for the meeting
        
    Returns:
        Dictionary with storage status and URL
    """
    try:
        bucket_name = os.getenv('GCS_BUCKET_NAME')
        
        # Initialize storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Create blob (file) in bucket
        blob_name = f"reports/{meeting_id}.json"
        blob = bucket.blob(blob_name)
        
        # Upload the report
        blob.upload_from_string(
            report_json,
            content_type='application/json'
        )
        
        # Generate signed URL (valid for 7 days) - works with uniform access
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )
        
        return {
            "status": "success",
            "message": f"Report saved successfully",
            "url": url
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }