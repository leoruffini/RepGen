# AssemblyAI Speaker Diarization - Quick Reference

## Summary

I've gathered comprehensive information about using AssemblyAI for speaker diarization. Here's what you need to know:

## Key Points

1. **Enabling Diarization**: Set `speaker_labels: true` in your transcription request
2. **Response Format**: Returns an `utterances` array with turn-by-turn speech segments
3. **Speaker Labels**: Speakers are labeled as "A", "B", "C", etc.
4. **Speaker Limits**: Default range is 1-10 speakers (can be customized)
5. **Not Compatible**: Can't use with multichannel transcription

## Quick Start (Python SDK)

```python
import assemblyai as aai

aai.settings.api_key = "<YOUR_API_KEY>"

config = aai.TranscriptionConfig(
    speaker_labels=True,
    speaker_options=aai.SpeakerOptions(
        min_speakers_expected=2,
        max_speakers_expected=5
    )
)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe("./audio.mp3", config)

# Access utterances
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
```

## Response Structure

Each utterance contains:
- `speaker`: Speaker label ("A", "B", etc.)
- `text`: Transcript text
- `start`: Start time in milliseconds
- `end`: End time in milliseconds
- `confidence`: Confidence score
- `words`: Array of word-level timing data

## Files Created

1. **ASSEMBLYAI_DIARIZATION_GUIDE.md** - Comprehensive documentation guide
2. **assemblyai_example.py** - Practical example code with both SDK and API approaches

## Next Steps

1. Install AssemblyAI SDK: `pip install assemblyai`
2. Get your API key from: https://assemblyai.com/dashboard
3. Review the example code in `assemblyai_example.py`
4. Check the full guide in `ASSEMBLYAI_DIARIZATION_GUIDE.md`

## Integration with Your Project

Based on your existing project structure (Real Estate Visit Report Generator), you can replace the Gladia integration with AssemblyAI. The key differences:

- **Gladia**: Uses `diarization: true` parameter
- **AssemblyAI**: Uses `speaker_labels: true` parameter
- **Response Format**: Both return utterances arrays, but field names may differ slightly

The main advantage of AssemblyAI is:
- More mature Python SDK
- Better documentation
- More flexible speaker range configuration



