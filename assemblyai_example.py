"""
Example: AssemblyAI Speaker Diarization Implementation

This script demonstrates how to use AssemblyAI to get diarized transcriptions
from audio files, including both Python SDK and direct API approaches.
"""

import os
import time
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Approach 1: Using AssemblyAI Python SDK (Recommended)
# ============================================================================

try:
    import assemblyai as aai
    
    def transcribe_with_sdk(
        audio_file_path: str,
        min_speakers: int = 1,
        max_speakers: int = 10,
        speakers_expected: Optional[int] = None
    ) -> Dict:
        """
        Transcribe audio using AssemblyAI Python SDK with speaker diarization.
        
        Args:
            audio_file_path: Path to local audio file or URL
            min_speakers: Minimum number of speakers expected
            max_speakers: Maximum number of speakers expected
            speakers_expected: Exact number of speakers (if known)
        
        Returns:
            Dictionary containing transcription results with utterances
        """
        # Set API key
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")
        
        aai.settings.api_key = api_key
        
        # Configure transcription
        if speakers_expected:
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                speakers_expected=speakers_expected
            )
        else:
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                speaker_options=aai.SpeakerOptions(
                    min_speakers_expected=min_speakers,
                    max_speakers_expected=max_speakers
                )
            )
        
        # Transcribe
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file_path, config)
        
        # Extract and format results
        result = {
            "id": transcript.id,
            "status": transcript.status,
            "text": transcript.text,
            "language_code": transcript.language_code,
            "utterances": [
                {
                    "speaker": utterance.speaker,
                    "text": utterance.text,
                    "start": utterance.start,
                    "end": utterance.end,
                    "confidence": utterance.confidence,
                    "words": [
                        {
                            "text": word.text,
                            "start": word.start,
                            "end": word.end,
                            "confidence": word.confidence,
                            "speaker": word.speaker
                        }
                        for word in utterance.words
                    ] if utterance.words else []
                }
                for utterance in transcript.utterances
            ]
        }
        
        return result

except ImportError:
    print("AssemblyAI SDK not installed. Install with: pip install assemblyai")
    transcribe_with_sdk = None


# ============================================================================
# Approach 2: Using requests library (Direct API)
# ============================================================================

import requests

def upload_audio_file(file_path: str, api_key: str) -> str:
    """
    Upload audio file to AssemblyAI.
    
    Args:
        file_path: Path to local audio file
        api_key: AssemblyAI API key
    
    Returns:
        Upload URL
    """
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": api_key}
    
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{base_url}/v2/upload",
            headers=headers,
            data=f
        )
    
    response.raise_for_status()
    return response.json()["upload_url"]


def create_transcript(
    audio_url: str,
    api_key: str,
    min_speakers: int = 1,
    max_speakers: int = 10,
    speakers_expected: Optional[int] = None
) -> str:
    """
    Create transcription request with speaker diarization.
    
    Args:
        audio_url: URL of audio file (upload URL or public URL)
        api_key: AssemblyAI API key
        min_speakers: Minimum number of speakers expected
        max_speakers: Maximum number of speakers expected
        speakers_expected: Exact number of speakers (if known)
    
    Returns:
        Transcript ID
    """
    base_url = "https://api.assemblyai.com"
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    
    # Build request payload
    data = {
        "audio_url": audio_url,
        "speaker_labels": True
    }
    
    if speakers_expected:
        data["speakers_expected"] = speakers_expected
    else:
        data["speaker_options"] = {
            "min_speakers_expected": min_speakers,
            "max_speakers_expected": max_speakers
        }
    
    # Submit transcription request
    response = requests.post(
        f"{base_url}/v2/transcript",
        json=data,
        headers=headers
    )
    
    response.raise_for_status()
    return response.json()["id"]


def poll_transcript(
    transcript_id: str,
    api_key: str,
    poll_interval: int = 3,
    max_attempts: int = 200
) -> Dict:
    """
    Poll transcript status until completion.
    
    Args:
        transcript_id: Transcript ID from create_transcript
        api_key: AssemblyAI API key
        poll_interval: Seconds to wait between polls
        max_attempts: Maximum number of polling attempts
    
    Returns:
        Complete transcript result
    """
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": api_key}
    polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"
    
    attempts = 0
    while attempts < max_attempts:
        response = requests.get(polling_endpoint, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        status = result.get("status")
        
        if status == "completed":
            return result
        elif status == "error":
            error_msg = result.get("error", "Unknown error")
            raise RuntimeError(f"Transcription failed: {error_msg}")
        
        attempts += 1
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Transcription did not complete after {max_attempts} attempts")


def transcribe_with_api(
    audio_file_path: str,
    min_speakers: int = 1,
    max_speakers: int = 10,
    speakers_expected: Optional[int] = None,
    is_url: bool = False
) -> Dict:
    """
    Transcribe audio using direct API calls with speaker diarization.
    
    Args:
        audio_file_path: Path to local audio file or URL
        min_speakers: Minimum number of speakers expected
        max_speakers: Maximum number of speakers expected
        speakers_expected: Exact number of speakers (if known)
        is_url: If True, treat audio_file_path as URL (skip upload)
    
    Returns:
        Dictionary containing transcription results with utterances
    """
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")
    
    # Upload file if it's a local path
    if is_url:
        audio_url = audio_file_path
    else:
        print("Uploading audio file...")
        audio_url = upload_audio_file(audio_file_path, api_key)
    
    # Create transcript
    print("Creating transcript with speaker diarization...")
    transcript_id = create_transcript(
        audio_url,
        api_key,
        min_speakers,
        max_speakers,
        speakers_expected
    )
    
    print(f"Transcript ID: {transcript_id}")
    print("Polling for results...")
    
    # Poll for results
    result = poll_transcript(transcript_id, api_key)
    
    # Format and return
    return {
        "id": result.get("id"),
        "status": result.get("status"),
        "text": result.get("text"),
        "language_code": result.get("language_code"),
        "utterances": result.get("utterances", [])
    }


# ============================================================================
# Example Usage
# ============================================================================

def format_utterances_for_display(utterances: List[Dict]) -> str:
    """
    Format utterances for readable display.
    
    Args:
        utterances: List of utterance dictionaries
    
    Returns:
        Formatted string
    """
    output = []
    for utterance in utterances:
        speaker = utterance.get("speaker", "Unknown")
        text = utterance.get("text", "")
        start_ms = utterance.get("start", 0)
        end_ms = utterance.get("end", 0)
        confidence = utterance.get("confidence", 0)
        
        start_sec = start_ms / 1000
        end_sec = end_ms / 1000
        
        output.append(
            f"[{start_sec:.1f}s - {end_sec:.1f}s] Speaker {speaker} "
            f"(confidence: {confidence:.2f}):\n{text}\n"
        )
    
    return "\n".join(output)


if __name__ == "__main__":
    # Example: Using Python SDK
    if transcribe_with_sdk:
        print("=" * 60)
        print("Example 1: Using AssemblyAI Python SDK")
        print("=" * 60)
        
        # Replace with your audio file path
        audio_file = "./example.mp3"
        
        if os.path.exists(audio_file):
            try:
                result = transcribe_with_sdk(
                    audio_file,
                    min_speakers=2,
                    max_speakers=5
                )
                
                print(f"\nStatus: {result['status']}")
                print(f"Language: {result['language_code']}")
                print(f"\nFull Transcript:\n{result['text']}\n")
                print(f"\nSpeaker Utterances:\n")
                print(format_utterances_for_display(result['utterances']))
                
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Audio file not found: {audio_file}")
    
    # Example: Using Direct API
    print("\n" + "=" * 60)
    print("Example 2: Using Direct API Calls")
    print("=" * 60)
    
    # Example with URL
    example_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"
    
    try:
        result = transcribe_with_api(
            example_url,
            min_speakers=1,
            max_speakers=10,
            is_url=True
        )
        
        print(f"\nStatus: {result['status']}")
        print(f"Language: {result['language_code']}")
        print(f"\nNumber of utterances: {len(result['utterances'])}")
        
        if result['utterances']:
            print("\nFirst few utterances:")
            for utterance in result['utterances'][:3]:
                print(f"Speaker {utterance['speaker']}: {utterance['text'][:100]}...")
    
    except Exception as e:
        print(f"Error: {e}")



