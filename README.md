# Sales Visit Report Generator

An AI-powered web application that transcribes sales visit audio recordings with speaker diarization and automatically generates structured, professional sales visit reports.

## Features

- 🎤 **Audio Transcription**: Upload MP3 files and get accurate transcriptions with speaker identification
- 👥 **Speaker Diarization**: Automatically identifies and labels different speakers in the conversation
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-5 to generate comprehensive sales visit reports
- 📊 **Structured Reports**: Generates detailed reports following the Provalix Homes format
- 💾 **Data Persistence**: Saves transcriptions for future reference
- ⬇️ **Easy Export**: Download reports and transcriptions in convenient formats

## Prerequisites

- Python 3.10 or higher
- API Keys:
  - AssemblyAI API key (get it from [AssemblyAI](https://www.assemblyai.com/))
  - OpenAI API key (get it from [OpenAI Platform](https://platform.openai.com/))

## Setup Instructions

### 1. Clone the Repository

```bash
cd /path/to/RepGen
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

Ensure you have a `.env` file in the project root with your API keys:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

## Running the Application

### Local Development

1. Activate the virtual environment (if not already activated):
   ```bash
   source venv/bin/activate
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

### Using the Application

1. **Upload Audio**: Click the file uploader and select an MP3 file of a sales visit recording
2. **Generate Report**: Click the "Generate Report" button to start processing
3. **View Results**: 
   - Switch between the **Report** tab to see the generated sales visit report
   - Use the **Transcription** tab to view the full conversation transcript with speaker labels
4. **Download**: Use the download buttons to save the report (Markdown) or transcription (Text)

## Project Structure

```
RepGen/
├── app.py                  # Main Streamlit application
├── utils.py                # Helper functions for transcription and report generation
├── requirements.txt        # Python dependencies
├── .env                    # API keys and configuration (not in git)
├── .gitignore             # Git ignore rules
├── transcriptions/        # Saved transcription JSON files
│   └── *.json
├── venv/                  # Virtual environment (not in git)
└── README.md              # This file
```

## Key Components

### `app.py`
Main Streamlit application featuring:
- Clean, intuitive user interface
- File upload handling
- Progress indicators during processing
- Tabbed display for reports and transcriptions
- Download functionality

### `utils.py`
Core utility functions:
- `transcribe_audio()`: Transcribes audio with AssemblyAI speaker diarization
- `save_transcription()`: Saves transcription data to JSON files
- `generate_report()`: Generates reports using OpenAI GPT-5 Responses API with stored prompts
- `validate_api_keys()`: Checks for required API keys and configuration

### Stored Prompt in OpenAI
The report generation prompt is stored in OpenAI's platform for easier maintenance and version control. Update the prompt directly in the OpenAI dashboard without needing to redeploy the application.

## Technical Details

### AssemblyAI Integration
- Uses the AssemblyAI Python SDK for simplicity
- Configured for 2-5 speakers (typical sales visit scenario)
- Returns speaker-labeled utterances with timestamps
- Formats conversations for easy GPT-5 processing

### OpenAI GPT-5 Integration
- Uses the new Responses API (recommended for reasoning models)
- Medium reasoning effort for balanced speed and quality
- Spanish language support for real estate context
- Handles complex multi-section report generation

### File Handling
- Temporarily saves uploaded MP3 files for processing
- Cleans up temporary files after transcription
- Persists transcription JSON with timestamps in `transcriptions/` folder
- Generates downloadable Markdown and text files

## Deployment

### Future: Deploy to Render

This application is designed to be deployed to [Render](https://render.com/) via GitHub integration. Steps will include:

1. Push code to GitHub repository
2. Connect Render to GitHub repo
3. Configure environment variables (API keys) in Render dashboard
4. Deploy as a Web Service
5. Access via provided Render URL

**Note**: Ensure API keys are set as environment variables in Render, not committed to the repository.

## Troubleshooting

### Missing API Keys
If you see an error about missing API keys:
1. Ensure your `.env` file exists in the project root
2. Verify the keys are correctly formatted: `ASSEMBLYAI_API_KEY=your_key_here`
3. Restart the Streamlit application after adding keys

### Import Errors
If you get import errors:
1. Ensure you've activated the virtual environment
2. Reinstall dependencies: `pip install -r requirements.txt`

### Transcription Errors
If transcription fails:
1. Verify your AssemblyAI API key is valid and has available credits
2. Check that the audio file is in MP3 format
3. Ensure audio quality is clear enough for transcription

### Report Generation Errors
If report generation fails:
1. Verify your OpenAI API key is valid and has available credits
2. Check that you have access to GPT-5 model
3. Ensure the transcription completed successfully

## Dependencies

- `streamlit==1.31.0` - Web application framework
- `assemblyai` - Audio transcription with speaker diarization
- `openai` - GPT-5 integration for report generation
- `python-dotenv` - Environment variable management

## License

This project is for internal use by Provalix Homes.

## Support

For issues or questions, please contact the development team.

---

**Built with ❤️ using Streamlit, AssemblyAI, and OpenAI GPT-5**



