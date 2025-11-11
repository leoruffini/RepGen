"""
Sales Visit Report Generator - Streamlit Application

A web application that transcribes sales visit audio recordings with speaker
diarization and generates structured sales visit reports using AI.
"""

import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from utils import (
    transcribe_audio,
    save_transcription,
    generate_report,
    validate_api_keys,
    load_transcription_from_json
)

# Page configuration
st.set_page_config(
    page_title="Sales Visit Report Generator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .top-bar {
        background: linear-gradient(90deg, #1f77b4, #1b8fcb);
        color: #fff;
        padding: 0.75rem 1.25rem;
        border-radius: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
    }
    .top-bar .product-name {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .top-bar .product-version {
        font-size: 0.9rem;
        opacity: 0.85;
    }
    .hero {
        background: #f7f9fc;
        border: 1px solid #e8eef5;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .hero h1 {
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
        color: #1f314f;
    }
    .hero p {
        color: #51627a;
        margin-bottom: 0;
        line-height: 1.5;
    }
    .toggle-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: #eef5fb;
        color: #1f77b4;
        border-radius: 999px;
        padding: 0.4rem 0.85rem;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .summary-card {
        border: 1px solid #dbe5f0;
        background: #ffffff;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-top: 0.75rem;
        box-shadow: 0 4px 12px rgba(31, 79, 120, 0.05);
    }
    .summary-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: #1f314f;
    }
    .summary-list {
        margin: 0;
        padding: 0;
        list-style: none;
    }
    .summary-list li {
        margin-bottom: 0.35rem;
        font-size: 0.9rem;
        color: #51627a;
    }
    .progress-steps {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.5rem 0.9rem;
        border-radius: 999px;
        font-size: 0.85rem;
        border: 1px solid #dbe5f0;
        color: #51627a;
        background: #fff;
    }
    .progress-step.active {
        border-color: #1f77b4;
        color: #1f77b4;
        background: rgba(31, 119, 180, 0.1);
        font-weight: 600;
    }
    .progress-step.done {
        border-color: #3cc77a;
        color: #1e8a52;
        background: rgba(60, 199, 122, 0.1);
    }
    .transcript-message {
        border: 1px solid #e8eef5;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        background: #fbfdff;
        margin-bottom: 0.5rem;
    }
    .transcript-speaker {
        display: block;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.25rem;
    }
    .empty-state {
        text-align: center;
        padding: 1.75rem;
        border: 1px dashed #cbd8e6;
        border-radius: 0.75rem;
        color: #51627a;
        background: rgba(240, 245, 250, 0.6);
    }
    @media (max-width: 900px) {
        .top-bar {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.35rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="top-bar">
        <span class="product-name">📊 Sales Visit Report Generator</span>
        <span class="product-version">Version 1.0 · AI-powered transcription & reporting</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Transform sales visits into structured reports in minutes.</h1>
        <p>Upload your recording, verify the transcript, and download a polished summary ready to share.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Check API keys
api_keys = validate_api_keys()
if not all(api_keys.values()):
    st.error("⚠️ Missing API Keys!")
    missing_keys = [key.upper() for key, available in api_keys.items() if not available]
    st.error(
        f"Please ensure the following API keys are set via your .env file or Streamlit secrets: {', '.join(missing_keys)}"
    )
    st.stop()

# Initialize session state
if 'report' not in st.session_state:
    st.session_state.report = None
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None
if 'test_mode' not in st.session_state:
    st.session_state.test_mode = False
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'report_date' not in st.session_state:
    st.session_state.report_date = datetime.today().date()
if 'sales_person' not in st.session_state:
    st.session_state.sales_person = "Mario Casanova"
if 'last_visit_metadata' not in st.session_state:
    st.session_state.last_visit_metadata = None
if 'last_upload_info' not in st.session_state:
    st.session_state.last_upload_info = None

def render_progress(has_upload: bool, has_transcription: bool, has_report: bool) -> None:
    steps = [
        {
            "label": "Upload",
            "status": "done" if has_upload else "active",
        },
        {
            "label": "Transcription",
            "status": (
                "done" if has_transcription else ("active" if has_upload else "pending")
            ),
        },
        {
            "label": "AI report",
            "status": (
                "done" if has_report else ("active" if has_transcription else "pending")
            ),
        },
        {
            "label": "Download",
            "status": "done" if has_report else "pending",
        },
    ]
    step_html = "".join(
        f"<div class='progress-step {' '.join(s for s in [step['status']] if s != 'pending')}'>{step['label']}</div>"
        for step in steps
    )
    progress_placeholder.markdown(f"<div class='progress-steps'>{step_html}</div>", unsafe_allow_html=True)

progress_placeholder = st.empty()
render_progress(
    has_upload=bool(st.session_state.audio_filename),
    has_transcription=st.session_state.transcription is not None,
    has_report=st.session_state.report is not None
)

# Mode selection and guidance
with st.container():
    toggle_col, info_col = st.columns([1, 3])
    with toggle_col:
        test_mode_toggle = st.checkbox(
            "Test mode",
            value=st.session_state.test_mode,
            key="test_mode_toggle",
            help="Upload a JSON transcription file instead of a new audio recording."
        )
        st.session_state.test_mode = test_mode_toggle
    with info_col:
        chip_text = (
            "Test mode active · Upload a saved transcription JSON to generate a report instantly."
            if st.session_state.test_mode
            else "Standard mode · Upload an MP3 audio file, we handle transcription and reporting."
        )
        st.markdown(f"<span class='toggle-chip'>{chip_text}</span>", unsafe_allow_html=True)

# Upload and visit details form
uploaded_file = None
with st.container():
    form_col, info_col = st.columns([2, 1])
    with form_col:
        with st.form("upload_form"):
            if st.session_state.test_mode:
                st.subheader("Upload transcription JSON")
                uploaded_file = st.file_uploader(
                    "Choose a JSON file",
                    type=["json"],
                    help="Use a transcription exported from a previous run."
                )
            else:
                st.subheader("Upload audio recording")
                uploaded_file = st.file_uploader(
                    "Choose an MP3 file",
                    type=["mp3"],
                    help="High-quality MP3 recordings deliver the best transcription results."
                )

            st.markdown("**Optional visit details**")
            details_col1, details_col2 = st.columns(2)
            with details_col1:
                st.text_input(
                    "Customer name",
                    key="customer_name",
                    help="Leave blank if unknown."
                )
            with details_col2:
                st.date_input(
                    "Date",
                    key="report_date",
                    help="Defaults to today."
                )

            st.text_input(
                "Salesperson",
                key="sales_person",
                help="Defaults to Mario Casanova."
            )

            st.caption("Your files stay on this device until you launch transcription.")

            generate_clicked = st.form_submit_button(
                "🚀 Generate report",
                use_container_width=True
            )

    with info_col:
        file_info = None
        if uploaded_file is not None:
            file_size_kb = uploaded_file.size / 1024
            file_size_mb = file_size_kb / 1024 if file_size_kb > 1024 else file_size_kb
            size_str = f"{file_size_mb:.2f} MB" if file_size_kb > 1024 else f"{file_size_kb:.1f} KB"
            file_info = {
                "name": uploaded_file.name,
                "size": size_str,
                "mode": "JSON transcription" if st.session_state.test_mode else "MP3 audio"
            }
            st.session_state.audio_filename = uploaded_file.name
            st.session_state.last_upload_info = file_info
        elif st.session_state.last_upload_info:
            file_info = st.session_state.last_upload_info

        if file_info:
            st.markdown(
                f"""
                <div class="summary-card">
                    <h4>Ready to process</h4>
                    <ul class="summary-list">
                        <li><strong>File:</strong> {file_info['name']}</li>
                        <li><strong>Size:</strong> {file_info['size']}</li>
                        <li><strong>Mode:</strong> {file_info['mode']}</li>
                    </ul>
                    <p style="font-size:0.85rem;margin-top:0.5rem;color:#6c7d94;">We’ll process this file when you click “Generate report”.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div style="font-size:2rem;">🎧</div>
                    <p><strong>Drop your recording to get started.</strong></p>
                    <p style="font-size:0.9rem;margin-bottom:0;">Upload an MP3 sales visit or switch to test mode to rehearse with a saved transcript.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown(
            """
            <div class="summary-card">
                <h4>Quick tips</h4>
                <ul class="summary-list">
                    <li>Capture visits with minimal background noise.</li>
                    <li>Confirm speaker names before sharing the report.</li>
                    <li>Use test mode to refine prompts without re-recording.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# Trigger report generation when the form is submitted
if generate_clicked:
    if uploaded_file is None:
        st.warning("Please upload a file before generating a report.")
    else:
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if st.session_state.test_mode:
                # Test Mode: Load transcription from JSON
                status_text.text("📄 Loading transcription from JSON...")
                progress_bar.progress(20)
                
                uploaded_file.seek(0)
                try:
                    json_data = json.load(uploaded_file)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON file: {e}")
                
                with st.spinner("Processing transcription data..."):
                    transcription_data = load_transcription_from_json(json_data)
                    st.session_state.transcription = transcription_data
                    progress_bar.progress(40)
                
                status_text.text("✓ Transcription loaded!")
                
                # Show info
                num_utterances = len(transcription_data.get('utterances', []))
                num_speakers = len(set(u['speaker'] for u in transcription_data.get('utterances', [])))
                st.info(f"ℹ️ Loaded {num_speakers} speakers with {num_utterances} utterances from JSON")
                
            else:
                # Normal Mode: Transcribe audio with AssemblyAI
                uploaded_file.seek(0)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                    tmp_file.flush()
                    os.fsync(tmp_file.fileno())
                
                # Verify file was created and has content
                if not os.path.exists(tmp_file_path):
                    raise Exception("Failed to create temporary file")
                
                file_size = os.path.getsize(tmp_file_path)
                if file_size == 0:
                    raise Exception("Uploaded file is empty")
                
                # Step 1: Transcribe audio
                status_text.text(f"🎤 Uploading and transcribing audio ({file_size / 1024 / 1024:.2f} MB)...")
                progress_bar.progress(10)
                
                with st.spinner("Transcribing audio... This may take a few minutes."):
                    transcription_data = transcribe_audio(tmp_file_path)
                    st.session_state.transcription = transcription_data
                    progress_bar.progress(50)
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                status_text.text("✓ Transcription complete!")
                
                # Show detailed info about the transcription for verification
                metadata = transcription_data.get('metadata', {})
                num_utterances = len(transcription_data.get('utterances', []))
                num_speakers = len(set(u['speaker'] for u in transcription_data.get('utterances', [])))
                
                # Display critical information for debugging
                st.success("✅ Transcription Complete!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Speakers", num_speakers)
                with col2:
                    st.metric("Utterances", num_utterances)
                with col3:
                    language = metadata.get('language_code', 'unknown')
                    st.metric("Language", language.upper() if language != 'unknown' else 'N/A')
                with col4:
                    confidence = metadata.get('language_confidence')
                    if confidence is not None:
                        st.metric("Confidence", f"{confidence:.1%}")
                    else:
                        st.metric("Confidence", "N/A")
                
                # Show first few utterances for verification
                st.markdown("**🔍 First 3 Utterances (for verification):**")
                for i, utterance in enumerate(transcription_data.get('utterances', [])[:3], 1):
                    speaker = utterance.get('speaker', '?')
                    text = utterance.get('text', '')[:150]
                    st.caption(f"{i}. **Speaker {speaker}:** {text}{'...' if len(utterance.get('text', '')) > 150 else ''}")
                
                # Show transcript ID for support
                st.info(f"🔑 **Transcript ID:** `{metadata.get('transcript_id', 'N/A')}`")
                
                # Step 2: Save transcription (only in normal mode)
                status_text.text("💾 Saving transcription data...")
                transcription_data['metadata']['original_filename'] = uploaded_file.name
                save_path = save_transcription(transcription_data, uploaded_file.name)
                progress_bar.progress(60)
                st.info(f"💾 Transcription saved: {save_path}")
            
            # Step 3: Generate report (both modes)
            visit_metadata = {
                "customer_name": st.session_state.customer_name.strip(),
                "report_date": st.session_state.report_date,
                "sales_person": st.session_state.sales_person.strip()
            }
            st.session_state.last_visit_metadata = visit_metadata

            metadata_lines = []
            if visit_metadata["customer_name"]:
                metadata_lines.append(f"- Cliente: {visit_metadata['customer_name']}")
            if visit_metadata["report_date"]:
                metadata_lines.append(f"- Fecha: {visit_metadata['report_date'].strftime('%Y-%m-%d')}")
            if visit_metadata["sales_person"]:
                metadata_lines.append(f"- Comercial: {visit_metadata['sales_person']}")

            metadata_section = ""
            if metadata_lines:
                metadata_section = "DETALLES DE LA VISITA:\n" + "\n".join(metadata_lines) + "\n\n"

            conversation_for_report = metadata_section + transcription_data['formatted_conversation']

            status_text.text("🤖 Generating sales visit report with GPT-5...")
            progress_bar.progress(70)
            
            with st.spinner("Analyzing conversation and generating report..."):
                report = generate_report(conversation_for_report)
                st.session_state.report = report
                progress_bar.progress(100)
            
            status_text.text("✓ Report generated successfully!")
            
            # Clean up temporary file (only in normal mode)
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            
            # Success message
            st.success("🎉 Report generated successfully!")
            if 'save_path' in locals():
                st.info(f"📁 Transcription saved to: {save_path}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.error("Please check your API keys and try again.")
            # Clean up temp file if it exists
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

# Update progress indicator
render_progress(
    has_upload=bool(st.session_state.audio_filename),
    has_transcription=st.session_state.transcription is not None,
    has_report=st.session_state.report is not None
)

# Display Results
if st.session_state.report:
    st.markdown("---")
    st.subheader("📊 Results")

    visit_metadata = st.session_state.get('last_visit_metadata')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"sales_visit_report_{timestamp}.md"
    transcription_filename = f"transcription_{timestamp}.txt"

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📄 Report", "🎙️ Transcript"])

    with tab1:
        if visit_metadata:
            customer_display = visit_metadata.get("customer_name") or "N/A"
            date_value = visit_metadata.get("report_date")
            date_display = date_value.strftime("%Y-%m-%d") if date_value else "N/A"
            salesperson_display = visit_metadata.get("sales_person") or "N/A"
            st.markdown(
                f"""
                <div class="summary-card">
                    <h4>Visit details</h4>
                    <ul class="summary-list">
                        <li><strong>Customer:</strong> {customer_display}</li>
                        <li><strong>Date:</strong> {date_display}</li>
                        <li><strong>Salesperson:</strong> {salesperson_display}</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(st.session_state.report)

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="⬇️ Download report (Markdown)",
                data=st.session_state.report,
                file_name=report_filename,
                mime="text/markdown",
                use_container_width=True,
                key="download_report_markdown",
            )
        with dl_col2:
            st.download_button(
                label="⬇️ Download transcript (Text)",
                data=st.session_state.transcription['formatted_conversation']
                if st.session_state.transcription
                else "",
                file_name=transcription_filename,
                mime="text/plain",
                use_container_width=True,
                disabled=st.session_state.transcription is None,
                key="download_transcript_text_summary",
            )

    with tab2:
        if st.session_state.transcription:
            transcription = st.session_state.transcription
            metadata = transcription.get('metadata', {})
            utterances = transcription.get('utterances', [])

            with st.expander("Recording details", expanded=False):
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                with detail_col1:
                    language_code = metadata.get('language_code', 'N/A')
                    st.metric("Language", language_code.upper() if language_code else "N/A")
                with detail_col2:
                    st.metric("Speakers", len(set(u['speaker'] for u in utterances)))
                with detail_col3:
                    duration = metadata.get('audio_duration')
                    st.metric("Duration", f"{duration/1000:.1f}s" if duration else "N/A")

            transcript_container = st.container()
            for idx, utterance in enumerate(utterances):
                speaker = utterance.get('speaker', '?')
                text = (utterance.get('text') or "").strip()
                if not text:
                    continue
                transcript_container.markdown(
                    f"""
                    <div class="transcript-message">
                        <span class="transcript-speaker">Speaker {speaker}</span>
                        <div>{text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.download_button(
                label="⬇️ Download transcript (Text)",
                data=transcription['formatted_conversation'],
                file_name=transcription_filename,
                mime="text/plain",
                use_container_width=True,
                key="download_transcript_text_detail",
            )
        else:
            st.info("No transcription data available.")

    st.markdown(
        """
        <div class="summary-card" style="margin-top:1.5rem;">
            <h4>All set</h4>
            <p style="color:#51627a;margin-bottom:0.75rem;">Need to process another visit? Reset the flow below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Process another file", use_container_width=True):
        st.session_state.report = None
        st.session_state.transcription = None
        st.session_state.audio_filename = None
        st.session_state.last_upload_info = None
        st.session_state.last_visit_metadata = None
        st.rerun()

# Continue sidebar content (checkbox defined above, rest of content below)
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This application uses:
    - **AssemblyAI** for audio transcription with speaker diarization
    - **OpenAI GPT-5** for intelligent report generation
    
    The system automatically identifies different speakers in the conversation
    and generates a structured sales visit report following the Provalix Homes format.
    """)
    
    st.markdown("---")
    
    st.header("📋 Requirements")
    if st.session_state.test_mode:
        st.markdown("""
        - JSON transcription file
        - Format: Saved transcription from previous runs
        """)
    else:
        st.markdown("""
        - MP3 audio file
        - Clear audio quality
        - 2-5 speakers expected
        - Sales visit context
        """)
    
    st.markdown("---")
    
    st.header("🔑 API Status")
    if st.session_state.test_mode:
        # In test mode, only OpenAI is needed
        st.info("Test Mode: Only OpenAI API needed")
        if api_keys.get('openai'):
            st.success("✅ OPENAI")
        else:
            st.error("❌ OPENAI")
    else:
        for api_name, available in api_keys.items():
            status = "✅" if available else "❌"
            st.markdown(f"{status} {api_name.upper()}")
    
    if (st.session_state.test_mode and api_keys.get('openai')) or (not st.session_state.test_mode and all(api_keys.values())):
        st.success("All required API keys configured!")
    
    st.markdown("---")
    st.caption("Sales Visit Report Generator v1.0")
    st.caption("Built with Streamlit, AssemblyAI & OpenAI")

