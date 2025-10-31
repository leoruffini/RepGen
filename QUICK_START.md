# Quick Start Guide

## Getting Started in 3 Steps

### 1. Ensure Your Environment is Ready

Your virtual environment should already be set up. If not, activate it:

```bash
source venv/bin/activate
```

### 2. Verify API Keys

Make sure your `.env` file contains both API keys:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Upload**: Click "Choose an MP3 file" and select your sales visit recording
2. **Generate**: Click the "🚀 Generate Report" button
3. **Wait**: The process takes a few minutes:
   - First, the audio is transcribed with speaker labels
   - Then, GPT-5 analyzes the conversation and generates the report
4. **Review**: 
   - View the generated report in the "Report" tab
   - View the full transcription in the "Transcription" tab
5. **Download**: Use the download buttons to save your files

## What to Expect

### Processing Time
- **Transcription**: 1-3 minutes (depends on audio length)
- **Report Generation**: 30-60 seconds
- **Total**: ~2-5 minutes for typical sales visit

### Output Files

1. **Report** (Markdown format):
   - Structured sales visit analysis
   - Client profile and needs
   - Budget and financing information
   - Next steps and recommendations

2. **Transcription** (Text format):
   - Speaker-labeled conversation
   - Full dialogue with speaker identification

3. **JSON** (Saved automatically in `transcriptions/`):
   - Complete transcription data with timestamps
   - Metadata (language, confidence scores, etc.)

## Tips for Best Results

### Audio Quality
- Use clear audio recordings
- Minimize background noise
- Ensure speakers are audible

### File Format
- Only MP3 files are supported
- Recommended: 128 kbps or higher quality

### Expected Scenario
- 2-5 speakers (salesperson + 1-4 customers/visitors)
- Sales visit context (real estate property viewing)
- Spanish or Catalan language (will be normalized to Spanish)

## Troubleshooting

### "Missing API Keys" Error
- Check that `.env` file exists in the project root
- Verify API keys are properly formatted
- Restart the Streamlit app after adding keys

### "Module not found" Error
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Slow Transcription
- This is normal for longer audio files
- AssemblyAI processing can take 1-3 minutes
- Don't close the browser while processing

### Report Generation Fails
- Ensure OpenAI API key has access to GPT-5
- Check that you have sufficient API credits
- Verify the transcription completed successfully

## Example Workflow

```bash
# 1. Navigate to project
cd /Users/leoruffini/Code/RepGen

# 2. Activate environment
source venv/bin/activate

# 3. Run app
streamlit run app.py

# 4. In browser:
#    - Upload your MP3 file
#    - Click "Generate Report"
#    - Wait for processing
#    - Download results
```

## Next Steps

- Review the generated report for accuracy
- Edit/customize the prompt in OpenAI's dashboard to adjust report format
- Save important transcriptions from the `transcriptions/` folder
- Prepare for Render deployment (see README.md)

---

For detailed documentation, see [README.md](README.md)



