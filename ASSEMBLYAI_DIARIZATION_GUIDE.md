# AssemblyAI Speaker Diarization Guide

## Overview

AssemblyAI provides speaker diarization capabilities that can detect multiple speakers in an audio file and identify what each speaker said. When enabled, the API returns a list of utterances, where each utterance corresponds to an uninterrupted segment of speech from a single speaker.

## Key Features

- **Speaker Detection**: Automatically detects multiple speakers in audio files
- **Utterance Segmentation**: Returns turn-by-turn transcripts with speaker labels
- **Speaker Limits**: Default range is 1-10 speakers, can be customized
- **Not Compatible**: Speaker Diarization doesn't support multichannel transcription (enabling both will result in an error)

## API Endpoints

### Base URL
```
https://api.assemblyai.com
```

### Key Endpoints
1. **Upload Audio**: `POST /v2/upload` - Upload local audio file
2. **Create Transcript**: `POST /v2/transcript` - Start transcription with diarization
3. **Get Transcript**: `GET /v2/transcript/{transcript_id}` - Poll for results

## Python SDK (Recommended)

### Installation
```bash
pip install -U assemblyai
```

### Basic Usage

```python
import assemblyai as aai

# Set API key
aai.settings.api_key = "<YOUR_API_KEY>"

# Define audio file (local path or URL)
audio_file = "./my-audio.mp3"
# OR
audio_file = "https://example.org/audio.mp3"

# Configure transcription with speaker diarization
config = aai.TranscriptionConfig(
    speaker_labels=True,
)

# Transcribe audio
transcriber = aai.Transcriber()
transcript = transcriber.transcribe(audio_file, config)

# Access utterances
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
```

### Advanced Configuration

#### Set Expected Number of Speakers
```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=5,  # Only use if you're certain about speaker count
)
```

#### Set Speaker Range
```python
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speaker_options=aai.SpeakerOptions(
        min_speakers_expected=3,
        max_speakers_expected=5
    ),
)
```

## Python (requests library)

### Step 1: Upload Audio File
```python
import requests

base_url = "https://api.assemblyai.com"
headers = {
    "authorization": "<YOUR_API_KEY>"
}

# Upload local file
with open("./my-audio.mp3", "rb") as f:
    response = requests.post(
        base_url + "/v2/upload",
        headers=headers,
        data=f
    )
    upload_url = response.json()["upload_url"]
```

### Step 2: Create Transcript with Diarization
```python
# Create transcript request
data = {
    "audio_url": upload_url,
    "speaker_labels": True,  # Enable speaker diarization
    # Optional: Set speaker expectations
    # "speakers_expected": 3,
    # OR use speaker_options
    # "speaker_options": {
    #     "min_speakers_expected": 2,
    #     "max_speakers_expected": 5
    # }
}

# Submit transcription request
url = base_url + "/v2/transcript"
response = requests.post(url, json=data, headers=headers)
transcript_id = response.json()['id']
```

### Step 3: Poll for Results
```python
import time

polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"

while True:
    transcription_result = requests.get(polling_endpoint, headers=headers).json()
    
    if transcription_result['status'] == 'completed':
        # Access utterances
        utterances = transcription_result.get('utterances', [])
        for utterance in utterances:
            print(f"Speaker {utterance['speaker']}: {utterance['text']}")
            print(f"  Start: {utterance['start']}ms, End: {utterance['end']}ms")
            print(f"  Confidence: {utterance['confidence']}")
        break
    
    elif transcription_result['status'] == 'error':
        raise RuntimeError(f"Transcription failed: {transcription_result['error']}")
    
    else:
        time.sleep(3)  # Wait 3 seconds before polling again
```

## API Request Parameters

### Speaker Diarization Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `speaker_labels` | boolean | **Required** - Enable Speaker Diarization |
| `speakers_expected` | number | Set exact number of speakers (only use if certain) |
| `speaker_options` | object | Set range of possible speakers |
| `speaker_options.min_speakers_expected` | number | Minimum number of speakers (default: 1) |
| `speaker_options.max_speakers_expected` | number | Maximum number of speakers (default: 10) |

### cURL Example

```bash
curl https://api.assemblyai.com/v2/transcript \
  --header "Authorization: <YOUR_API_KEY>" \
  --header "Content-Type: application/json" \
  --data '{
    "audio_url": "YOUR_AUDIO_URL",
    "speaker_labels": true,
    "speaker_options": {
      "min_speakers_expected": 2,
      "max_speakers_expected": 5
    }
  }'
```

## Response Structure

### Utterances Array

The response includes an `utterances` array containing turn-by-turn transcript data:

```json
{
  "utterances": [
    {
      "confidence": 0.95,
      "end": 3500,
      "speaker": "A",
      "start": 1000,
      "text": "Hello, how are you today?",
      "words": [
        {
          "text": "Hello",
          "start": 1000,
          "end": 1500,
          "confidence": 0.98,
          "speaker": "A"
        },
        {
          "text": "how",
          "start": 1500,
          "end": 1800,
          "confidence": 0.96,
          "speaker": "A"
        }
        // ... more words
      ]
    },
    {
      "confidence": 0.92,
      "end": 6000,
      "speaker": "B",
      "start": 4000,
      "text": "I'm doing great, thanks!",
      "words": [...]
    }
  ]
}
```

### Utterance Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `speaker` | string | Speaker label (e.g., "A", "B", "C") |
| `text` | string | The transcript text for this utterance |
| `start` | number | Starting time in milliseconds |
| `end` | number | Ending time in milliseconds |
| `confidence` | number | Confidence score for the transcript |
| `words` | array | Array of word-level timing and confidence data |

### Word Object Fields (within utterances)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | The word text |
| `start` | number | Starting time in milliseconds |
| `end` | number | Ending time in milliseconds |
| `confidence` | number | Confidence score for the word |
| `speaker` | string | Speaker who uttered this word |

## Best Practices

1. **Polling Strategy**: Poll every 3 seconds until status is `completed` or `error`
2. **Webhooks**: Consider using webhooks instead of polling for better efficiency
3. **Speaker Count**: Only set `speakers_expected` if you're certain about the number
4. **Speaker Range**: Use `speaker_options` to narrow the range if you know it (improves accuracy)
5. **Default Range**: Default is 1-10 speakers; setting higher max than necessary may hurt accuracy
6. **Multichannel**: Remember that speaker diarization doesn't work with multichannel transcription

## Integration Example for Real Estate Visit Reports

Based on your project structure, here's how you might integrate AssemblyAI:

```python
import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_with_diarization(audio_file_path):
    """
    Transcribe audio file with speaker diarization.
    
    Returns:
        dict: Transcription result with utterances
    """
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speaker_options=aai.SpeakerOptions(
            min_speakers_expected=2,  # Commercial + Client
            max_speakers_expected=5   # Multiple clients possible
        )
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file_path, config)
    
    # Extract essential data
    result = {
        "full_transcript": transcript.text,
        "utterances": [
            {
                "speaker": utterance.speaker,
                "text": utterance.text,
                "start": utterance.start,
                "end": utterance.end,
                "confidence": utterance.confidence
            }
            for utterance in transcript.utterances
        ],
        "language": transcript.language_code,
        "status": transcript.status
    }
    
    return result
```

## Limitations & Notes

- **Maximum Speakers**: Default maximum is 10 speakers
- **Multichannel**: Not compatible with multichannel transcription
- **Accuracy**: Setting `max_speakers_expected` higher than necessary may reduce accuracy
- **File Upload**: Uploaded files are deleted after transcription completes or 24 hours after upload
- **Processing Time**: Transcription is asynchronous; use polling or webhooks

## References

- [AssemblyAI API Reference](https://www.assemblyai.com/docs/api-reference/overview)
- [Speaker Diarization Documentation](https://www.assemblyai.com/docs/speech-to-text/pre-recorded-audio/speaker-diarization)
- [Python SDK Documentation](https://www.assemblyai.com/docs/getting-started/transcribe-an-audio-file)



