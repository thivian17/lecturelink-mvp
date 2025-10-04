from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import os
from typing import Dict

def transcribe_audio(audio_file_path: str) -> Dict[str, str]:
    """
    Transcribes audio file using Google Speech-to-Text.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Dictionary with transcript and status
    """
    try:
        # Initialize Speech client
        client = speech.SpeechClient()
        
        # Read audio file
        with open(audio_file_path, 'rb') as audio_file:
            content = audio_file.read()
        
        # Configure audio
        audio = speech.RecognitionAudio(content=content)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True,
            enable_speaker_diarization=True,  # Identifies different speakers
            diarization_speaker_count=2,  # Adjust based on your needs
        )
        
        # Perform transcription
        response = client.recognize(config=config, audio=audio)
        
        # Extract transcript
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        
        return {
            "status": "success",
            "transcript": transcript.strip()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "transcript": "",
            "error_message": str(e)
        }