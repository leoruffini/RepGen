"""
Utility functions for the Sales Visit Report Generator.

This module provides functions for:
- Transcribing audio files with speaker diarization using AssemblyAI
- Saving transcription data to JSON files
- Generating sales visit reports using OpenAI GPT-5
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API clients
try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False
    print("Warning: AssemblyAI SDK not installed")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI SDK not installed")


def transcribe_audio(audio_file_path: str) -> Dict:
    """
    Transcribe audio file using AssemblyAI with speaker diarization.
    
    Args:
        audio_file_path: Path to the audio file (MP3)
        
    Returns:
        Dictionary containing:
            - formatted_conversation: Simple string format "Speaker A: text\\nSpeaker B: text..."
            - full_transcript: Complete transcript text
            - utterances: List of utterance dictionaries
            - metadata: Additional info (language, duration, etc.)
            
    Raises:
        ValueError: If API key is missing or SDK not available
        Exception: If transcription fails
    """
    if not ASSEMBLYAI_AVAILABLE:
        raise ImportError("AssemblyAI SDK not installed. Install with: pip install assemblyai")
    
    # Get API key
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")
    
    # Configure API
    aai.settings.api_key = api_key
    
    # Configure transcription with speaker diarization
    # Use automatic language detection with Catalan and Spanish as expected languages
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_detection=True,  # Enable automatic language detection
        language_detection_options=aai.LanguageDetectionOptions(
            expected_languages=["ca", "es"],  # Catalan and Spanish
            fallback_language="es"  # Fallback to Spanish if unsure
        ),
        speaker_options=aai.SpeakerOptions(
            min_speakers_expected=2,
            max_speakers_expected=5
        )
    )
    
    # Verify the file before sending
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    file_size = os.path.getsize(audio_file_path)
    print(f"DEBUG: Sending file to AssemblyAI: {audio_file_path}")
    print(f"DEBUG: File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Create transcriber and transcribe
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file_path, config)
    
    # Debug: Print transcription details
    print(f"DEBUG: Transcription ID: {transcript.id}")
    print(f"DEBUG: Status: {transcript.status}")
    
    # Get language detection info
    language_detected = getattr(transcript, 'language_code', 'unknown')
    language_confidence = getattr(transcript, 'language_confidence', 'N/A')
    
    print(f"DEBUG: Language detected: {language_detected}")
    print(f"DEBUG: Language confidence: {language_confidence}")
    
    if transcript.utterances:
        print(f"DEBUG: First utterance: Speaker {transcript.utterances[0].speaker}: {transcript.utterances[0].text[:100]}...")
    
    # Check for errors
    if transcript.status == "error":
        raise Exception(f"Transcription failed: {transcript.error}")
    
    # Format conversation for GPT-5
    formatted_conversation = format_conversation(transcript.utterances)
    
    # Prepare utterances data
    utterances_data = [
        {
            "speaker": utterance.speaker,
            "text": utterance.text,
            "start": utterance.start,
            "end": utterance.end,
            "confidence": utterance.confidence
        }
        for utterance in transcript.utterances
    ]
    
    # Build response
    result = {
        "formatted_conversation": formatted_conversation,
        "full_transcript": transcript.text,
        "utterances": utterances_data,
        "metadata": {
            "language_code": getattr(transcript, 'language_code', 'unknown'),
            "language_confidence": getattr(transcript, 'language_confidence', None),
            "transcript_id": transcript.id,
            "status": transcript.status,
            "audio_duration": getattr(transcript, 'audio_duration', None)
        }
    }
    
    return result


def format_conversation(utterances) -> str:
    """
    Format utterances into a simple conversation string.
    
    Args:
        utterances: List of utterance objects from AssemblyAI
        
    Returns:
        Formatted string: "Speaker A: text\\nSpeaker B: text..."
    """
    conversation_lines = []
    
    for utterance in utterances:
        speaker = utterance.speaker if hasattr(utterance, 'speaker') else "Unknown"
        text = utterance.text if hasattr(utterance, 'text') else ""
        conversation_lines.append(f"Speaker {speaker}: {text}")
    
    return "\n\n".join(conversation_lines)


def load_transcription_from_json(json_data: Dict) -> Dict:
    """
    Load transcription data from a JSON dictionary (test mode).
    
    Args:
        json_data: Dictionary containing transcription data with structure:
            - utterances: List of utterance dicts with speaker, text, start, end, confidence
            - full_transcript: Optional complete transcript text
            - metadata: Optional metadata dict
            
    Returns:
        Dictionary with the same structure as transcribe_audio() returns:
            - formatted_conversation: Simple string format
            - full_transcript: Complete transcript text
            - utterances: List of utterance dictionaries
            - metadata: Additional info
    """
    # Extract utterances
    utterances = json_data.get('utterances', [])
    if not utterances:
        raise ValueError("No utterances found in JSON data")
    
    # Format conversation from utterances (handle dict format)
    conversation_lines = []
    for utterance in utterances:
        speaker = utterance.get('speaker', 'Unknown')
        text = utterance.get('text', '')
        conversation_lines.append(f"Speaker {speaker}: {text}")
    formatted_conversation = "\n\n".join(conversation_lines)
    
    # Get full transcript or generate from utterances
    full_transcript = json_data.get('full_transcript', '')
    if not full_transcript and utterances:
        full_transcript = " ".join(u.get('text', '') for u in utterances)
    
    # Extract metadata
    metadata = json_data.get('metadata', {})
    
    return {
        "formatted_conversation": formatted_conversation,
        "full_transcript": full_transcript,
        "utterances": utterances,
        "metadata": metadata
    }


def save_transcription(transcription_data: Dict, audio_filename: str) -> str:
    """
    Save transcription data to JSON file in transcriptions/ folder.
    
    Args:
        transcription_data: Dictionary with transcription data
        audio_filename: Original audio filename
        
    Returns:
        Path to saved JSON file
    """
    # Create transcriptions directory if it doesn't exist
    os.makedirs("transcriptions", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Remove extension from audio filename
    audio_name = os.path.splitext(audio_filename)[0]
    json_filename = f"transcription_{timestamp}_{audio_name}.json"
    json_filepath = os.path.join("transcriptions", json_filename)
    
    # Save to JSON
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(transcription_data, f, indent=2, ensure_ascii=False)
    
    return json_filepath


def generate_report(formatted_conversation: str) -> str:
    """
    Generate sales visit report using OpenAI GPT-5 Responses API with stored prompt.
    
    Args:
        formatted_conversation: Formatted conversation string with speaker labels
        
    Returns:
        Markdown formatted report
        
    Raises:
        ValueError: If API key or prompt ID is missing or SDK not available
        Exception: If report generation fails
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI SDK not installed. Install with: pip install openai")
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Get stored prompt configuration
    prompt_id = os.getenv("OPENAI_PROMPT_ID")
    prompt_version = os.getenv("OPENAI_PROMPT_VERSION", "1")
    
    if not prompt_id:
        raise ValueError("OPENAI_PROMPT_ID not found in environment variables. Please add it to your .env file.")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Prepare input for GPT-5 - the stored prompt contains all instructions
    input_text = f"""TRANSCRIPCIÓN DE LA VISITA COMERCIAL:

{formatted_conversation}

---

Por favor, genera una ficha post-visita completa siguiendo la plantilla especificada."""
    
    # Generate report using Responses API with stored prompt
    try:
        response = client.responses.create(
            prompt={
                "id": prompt_id,
                "version": prompt_version
            },
            input=input_text,
            text={},
            max_output_tokens=16384,
            store=True
        )
        
        # Check for incomplete response
        if hasattr(response, 'status') and response.status == "incomplete":
            print(f"Warning: Response incomplete ({response.incomplete_details.reason})")
        
        return response.output_text
        
    except Exception as e:
        raise Exception(f"Failed to generate report: {str(e)}")


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that required API keys and configuration are present.
    
    Returns:
        Dictionary with API key and configuration availability status
    """
    return {
        "assemblyai": bool(os.getenv("ASSEMBLYAI_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "openai_prompt": bool(os.getenv("OPENAI_PROMPT_ID"))
    }

