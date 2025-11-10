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
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📊 Sales Visit Report Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload an MP3 audio file to generate a structured sales visit report with AI-powered transcription and analysis.</p>', unsafe_allow_html=True)

# Check API keys
api_keys = validate_api_keys()
if not all(api_keys.values()):
    st.error("⚠️ Missing API Keys!")
    missing_keys = [key.upper() for key, available in api_keys.items() if not available]
    st.error(f"Please ensure the following API keys are set in your .env file: {', '.join(missing_keys)}")
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

# Define test mode checkbox early (before it's used)
# This ensures the value is updated before we check it in the main content
with st.sidebar:
    st.header("⚙️ Mode")
    st.session_state.test_mode = st.checkbox(
        "Test Mode",
        value=st.session_state.test_mode,
        key="test_mode_checkbox",
        help="Upload a JSON transcription file directly (bypasses AssemblyAI)"
    )
    st.markdown("---")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.test_mode:
        st.subheader("Upload Transcription JSON")
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=["json"],
            help="Upload a saved transcription JSON file (from transcriptions/ folder)"
        )
    else:
        st.subheader("Upload Audio File")
        uploaded_file = st.file_uploader(
            "Choose an MP3 file",
            type=["mp3"],
            help="Upload the audio recording of the sales visit (MP3 format)"
        )
    
    st.markdown("---")
    st.subheader("Optional Visit Details")
    st.text_input(
        "Customer name (optional)",
        key="customer_name",
        help="Leave blank if unknown."
    )
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
    if uploaded_file is not None:
        file_size_kb = uploaded_file.size / 1024
        file_size_mb = file_size_kb / 1024 if file_size_kb > 1024 else file_size_kb
        size_str = f"{file_size_mb:.2f} MB" if file_size_kb > 1024 else f"{file_size_kb:.1f} KB"
        st.success(f"✓ File uploaded: {uploaded_file.name} ({size_str})")
        
        # Store filename in session state
        st.session_state.audio_filename = uploaded_file.name

with col2:
    st.subheader("Process Steps")
    if st.session_state.test_mode:
        st.markdown("""
        1. 📄 Upload JSON transcription
        2. 🤖 Generate AI report
        3. 📄 Download results
        """)
    else:
        st.markdown("""
        1. 🎤 Upload MP3 audio
        2. 📝 Transcribe with speaker labels
        3. 🤖 Generate AI report
        4. 📄 Download results
        """)

# Generate Report Button
st.markdown("---")

if uploaded_file is not None:
    if st.button("🚀 Generate Report", type="primary", use_container_width=True):
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

# Display Results
if st.session_state.report:
    st.markdown("---")
    st.subheader("📊 Generated Report")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📄 Report", "🎙️ Transcription"])
    
    with tab1:
        # Display visit metadata
        visit_metadata = st.session_state.get('last_visit_metadata')
        if visit_metadata:
            customer_display = visit_metadata.get("customer_name") or "N/A"
            date_value = visit_metadata.get("report_date")
            date_display = date_value.strftime("%Y-%m-%d") if date_value else "N/A"
            salesperson_display = visit_metadata.get("sales_person") or "N/A"
            st.markdown("**Visit Details**")
            st.markdown(
                f"- **Customer:** {customer_display}\n"
                f"- **Date:** {date_display}\n"
                f"- **Salesperson:** {salesperson_display}"
            )

        # Display the report
        st.markdown(st.session_state.report)
        
        # Download button for report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"sales_visit_report_{timestamp}.md"
        
        st.download_button(
            label="⬇️ Download Report (Markdown)",
            data=st.session_state.report,
            file_name=report_filename,
            mime="text/markdown",
            use_container_width=True
        )
    
    with tab2:
        # Display transcription
        if st.session_state.transcription:
            st.subheader("Full Conversation Transcript")
            
            # Show metadata
            metadata = st.session_state.transcription.get('metadata', {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Language", metadata.get('language_code', 'N/A').upper())
            with col2:
                st.metric("Speakers", len(set(u['speaker'] for u in st.session_state.transcription.get('utterances', []))))
            with col3:
                duration = metadata.get('audio_duration')
                if duration:
                    st.metric("Duration", f"{duration/1000:.1f}s")
                else:
                    st.metric("Duration", "N/A")
            
            st.markdown("---")
            
            # Display formatted conversation
            st.markdown("**Speaker-by-Speaker Transcript:**")
            st.text_area(
                "Conversation",
                value=st.session_state.transcription['formatted_conversation'],
                height=400,
                label_visibility="collapsed"
            )
            
            # Download button for transcription
            transcription_filename = f"transcription_{timestamp}.txt"
            st.download_button(
                label="⬇️ Download Transcription (Text)",
                data=st.session_state.transcription['formatted_conversation'],
                file_name=transcription_filename,
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("No transcription data available.")

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

