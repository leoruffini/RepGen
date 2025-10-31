<!-- 5f9073dd-a733-4136-852d-24722c46a9f9 08b8fffc-bb85-4049-a81b-6bb461089a3e -->
# Real Estate Visit Report Generator MVP

## Architecture Overview

Simple web app: Upload MP3 → Gladia transcription → GPT-5 analysis → Display report

## Implementation Steps

### 1. Environment Configuration

Create `.env` file with API keys:

```
GLADIA_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Create `.gitignore` to protect sensitive files:

```
venv/
.env
__pycache__/
*.pyc
.DS_Store
```

### 2. Dependencies

Create `requirements.txt`:

```
streamlit==1.31.0
openai==2.6.1
python-dotenv==1.0.1
requests==2.31.0
```

### 3. Main Application (`app.py`)

**Core workflow:**

**a) Streamlit UI Setup**

- Title and description
- File uploader (accept MP3 only, max 200MB)
- Process button
- Progress indicators during processing
- Report display area with markdown rendering

**b) Gladia Integration**

```python
def upload_to_gladia(audio_file):
    # POST /v2/upload with multipart/form-data
    # Return audio_url
    
def transcribe_audio(audio_url):
    # POST /v2/pre-recorded with:
    #   - diarization: true
    #   - min_speakers: 1, max_speakers: 5
    # Return transcription result_url and id
    
def poll_transcription(result_url):
    # Poll every 5 seconds until status == "done"
    # Return full transcription JSON
```

**c) GPT-5 Integration**

```python
def extract_essential_data(transcription_json):
    # Extract only the essential data from Gladia response:
    #   - result.transcription.full_transcript
    #   - result.transcription.utterances[] (speaker, start, end, confidence, text)
    #   - Basic metadata (language, duration, speaker_count)
    # Exclude word-by-word timing data to reduce token count
    # Return compact JSON structure
    
def generate_report(transcription_json):
    # Extract essential data first
    # Load prompt from prompt.md
    # Format input with compact JSON
    # Call OpenAI Responses API:
    #   - model: "gpt-5"
    #   - reasoning.effort: "medium"
    #   - input: prompt + compact JSON
    # Return output_text (markdown report)
```

**d) Main Processing Flow**

```python
if st.button("Generate Report"):
    with st.spinner("Uploading audio..."):
        audio_url = upload_to_gladia(uploaded_file)
    
    with st.spinner("Transcribing with speaker diarization..."):
        result_url, job_id = transcribe_audio(audio_url)
        transcription = poll_transcription(result_url)
    
    with st.spinner("Analyzing conversation with GPT-5..."):
        report = generate_report(transcription)
    
    st.success("Report generated!")
    st.markdown(report)
```

### 4. Error Handling

- Validate file type (MP3 only)
- Handle API errors with user-friendly messages
- Add timeouts for polling (max 10 minutes)
- Display connection errors clearly

### 5. README Documentation

Create `README.md` with:

- Project description
- Setup instructions (venv, .env configuration)
- How to run locally: `streamlit run app.py`
- Future deployment to Render

## Key Technical Details

- **GPT-5 Configuration**: model="gpt-5", reasoning.effort="medium"
- **Gladia Diarization**: Auto-detect speakers (min 1, max 5)
- **Responses API**: Use `client.responses.create()` not chat completions
- **Polling Strategy**: Check every 5 seconds, max 120 attempts
- **File Storage**: Transcription JSON saved to `transcriptions/` folder with timestamped filenames

## Files to Create

1. `.env` - API keys configuration
2. `.gitignore` - Exclude sensitive/generated files
3. `requirements.txt` - Python dependencies
4. `app.py` - Main Streamlit application
5. `README.md` - Setup and usage documentation

### To-dos

- [ ] Create project structure, requirements.txt, update .env template, add .gitignore
- [ ] Implement Gladia transcription service with upload, request, and polling logic
- [ ] Implement GPT-5 report generation service using Responses API with prompt.md
- [ ] Build Streamlit interface with upload, progress tracking, and download features
- [ ] Create README with setup instructions and usage guide