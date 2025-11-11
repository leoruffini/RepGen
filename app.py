"""
Generador de informes de visitas comerciales - Aplicación Streamlit

Una aplicación web que transcribe grabaciones de visitas comerciales con diarización
de interlocutores y genera informes estructurados utilizando IA.
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
    page_title="Generador de informes de visitas comerciales",
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
        <span class="product-name">📊 Generador de informes de visitas comerciales</span>
        <span class="product-version">Versión 1.0 · Transcripción e informes con IA</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Convierte tus visitas comerciales en informes estructurados en minutos.</h1>
        <p>Sube tu grabación, revisa la transcripción y descarga un resumen listo para compartir.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Check API keys
api_keys = validate_api_keys()
if not all(api_keys.values()):
    st.error("⚠️ ¡Faltan claves de API!")
    missing_keys = [key.upper() for key, available in api_keys.items() if not available]
    st.error(
        f"Asegúrate de configurar las siguientes claves de API en tu archivo .env o en los secretos de Streamlit: {', '.join(missing_keys)}"
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
            "label": "Subida",
            "status": "done" if has_upload else "active",
        },
        {
            "label": "Transcripción",
            "status": (
                "done" if has_transcription else ("active" if has_upload else "pending")
            ),
        },
        {
            "label": "Informe IA",
            "status": (
                "done" if has_report else ("active" if has_transcription else "pending")
            ),
        },
        {
            "label": "Descarga",
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
            "Modo de prueba",
            value=st.session_state.test_mode,
            key="test_mode_toggle",
            help="Sube un archivo JSON de transcripción en lugar de una nueva grabación de audio."
        )
        st.session_state.test_mode = test_mode_toggle
    with info_col:
        chip_text = (
            "Modo de prueba activo · Sube una transcripción JSON guardada para generar un informe al instante."
            if st.session_state.test_mode
            else "Modo estándar · Sube un archivo de audio MP3; nosotros nos ocupamos de la transcripción y del informe."
        )
        st.markdown(f"<span class='toggle-chip'>{chip_text}</span>", unsafe_allow_html=True)

# Upload and visit details form
uploaded_file = None
with st.container():
    form_col, info_col = st.columns([2, 1])
    with form_col:
        with st.form("upload_form"):
            if st.session_state.test_mode:
                st.subheader("Sube la transcripción en JSON")
                uploaded_file = st.file_uploader(
                    "Elige un archivo JSON",
                    type=["json"],
                    help="Utiliza una transcripción exportada de una ejecución anterior."
                )
            else:
                st.subheader("Sube la grabación de audio")
                uploaded_file = st.file_uploader(
                    "Elige un archivo MP3",
                    type=["mp3"],
                    help="Las grabaciones MP3 de alta calidad ofrecen mejores resultados de transcripción."
                )

            st.markdown("**Detalles de la visita (opcional)**")
            details_col1, details_col2 = st.columns(2)
            with details_col1:
                st.text_input(
                    "Nombre del cliente",
                    key="customer_name",
                    help="Déjalo en blanco si no lo conoces."
                )
            with details_col2:
                st.date_input(
                    "Fecha",
                    key="report_date",
                    help="Por defecto es la fecha de hoy."
                )

            st.text_input(
                "Comercial",
                key="sales_person",
                help="Por defecto: Mario Casanova."
            )

            st.caption("Tus archivos permanecen en este dispositivo hasta iniciar la transcripción.")

            generate_clicked = st.form_submit_button(
                "🚀 Generar informe",
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
                "mode": "Transcripción JSON" if st.session_state.test_mode else "Audio MP3"
            }
            st.session_state.audio_filename = uploaded_file.name
            st.session_state.last_upload_info = file_info
        elif st.session_state.last_upload_info:
            file_info = st.session_state.last_upload_info

        if file_info:
            st.markdown(
                f"""
                <div class="summary-card">
                    <h4>Listo para procesar</h4>
                    <ul class="summary-list">
                        <li><strong>Archivo:</strong> {file_info['name']}</li>
                        <li><strong>Tamaño:</strong> {file_info['size']}</li>
                        <li><strong>Modo:</strong> {file_info['mode']}</li>
                    </ul>
                    <p style="font-size:0.85rem;margin-top:0.5rem;color:#6c7d94;">Procesaremos este archivo cuando hagas clic en “Generar informe”.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div style="font-size:2rem;">🎧</div>
                    <p><strong>Arrastra tu grabación para empezar.</strong></p>
                    <p style="font-size:0.9rem;margin-bottom:0;">Sube una visita comercial en MP3 o cambia al modo de prueba para practicar con una transcripción guardada.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown(
            """
            <div class="summary-card">
                <h4>Consejos rápidos</h4>
                <ul class="summary-list">
                    <li>Graba las visitas con el mínimo ruido de fondo.</li>
                    <li>Confirma los nombres de los interlocutores antes de compartir el informe.</li>
                    <li>Usa el modo de prueba para afinar los prompts sin volver a grabar.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# Trigger report generation when the form is submitted
if generate_clicked:
    if uploaded_file is None:
        st.warning("Sube un archivo antes de generar el informe.")
    else:
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if st.session_state.test_mode:
                # Test Mode: Load transcription from JSON
                status_text.text("📄 Cargando la transcripción desde JSON...")
                progress_bar.progress(20)
                
                uploaded_file.seek(0)
                try:
                    json_data = json.load(uploaded_file)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Archivo JSON no válido: {e}")
                
                with st.spinner("Procesando los datos de la transcripción..."):
                    transcription_data = load_transcription_from_json(json_data)
                    st.session_state.transcription = transcription_data
                    progress_bar.progress(40)
                
                status_text.text("✓ ¡Transcripción cargada!")
                
                # Show info
                num_utterances = len(transcription_data.get('utterances', []))
                num_speakers = len(set(u['speaker'] for u in transcription_data.get('utterances', [])))
                st.info(f"ℹ️ Se cargaron {num_speakers} interlocutores con {num_utterances} intervenciones desde el JSON")
                
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
                    raise Exception("No se pudo crear el archivo temporal")
                
                file_size = os.path.getsize(tmp_file_path)
                if file_size == 0:
                    raise Exception("El archivo subido está vacío")
                
                # Step 1: Transcribe audio
                status_text.text(f"🎤 Cargando y transcribiendo el audio ({file_size / 1024 / 1024:.2f} MB)...")
                progress_bar.progress(10)
                
                with st.spinner("Transcribiendo audio... Puede tardar algunos minutos."):
                    transcription_data = transcribe_audio(tmp_file_path)
                    st.session_state.transcription = transcription_data
                    progress_bar.progress(50)
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                status_text.text("✓ ¡Transcripción completada!")
                
                # Show detailed info about the transcription for verification
                metadata = transcription_data.get('metadata', {})
                num_utterances = len(transcription_data.get('utterances', []))
                num_speakers = len(set(u['speaker'] for u in transcription_data.get('utterances', [])))
                
                # Display critical information for debugging
                st.success("✅ ¡Transcripción completada!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Interlocutores", num_speakers)
                with col2:
                    st.metric("Intervenciones", num_utterances)
                with col3:
                    language = metadata.get('language_code', 'unknown')
                    st.metric("Idioma", language.upper() if language != 'unknown' else 'N/A')
                with col4:
                    confidence = metadata.get('language_confidence')
                    if confidence is not None:
                        st.metric("Confianza", f"{confidence:.1%}")
                    else:
                        st.metric("Confianza", "N/A")
                
                # Show first few utterances for verification
                st.markdown("**🔍 Primeras 3 intervenciones (verificación):**")
                for i, utterance in enumerate(transcription_data.get('utterances', [])[:3], 1):
                    speaker = utterance.get('speaker', '?')
                    text = utterance.get('text', '')[:150]
                    st.caption(f"{i}. **Interlocutor {speaker}:** {text}{'...' if len(utterance.get('text', '')) > 150 else ''}")
                
                # Show transcript ID for support
                st.info(f"🔑 **ID de transcripción:** `{metadata.get('transcript_id', 'N/A')}`")
                
                # Step 2: Save transcription (only in normal mode)
                status_text.text("💾 Guardando los datos de la transcripción...")
                transcription_data['metadata']['original_filename'] = uploaded_file.name
                save_path = save_transcription(transcription_data, uploaded_file.name)
                progress_bar.progress(60)
                st.info(f"💾 Transcripción guardada: {save_path}")
            
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

            status_text.text("🤖 Generando informe de visita comercial con GPT-5...")
            progress_bar.progress(70)
            
            with st.spinner("Analizando la conversación y generando el informe..."):
                report = generate_report(conversation_for_report)
                st.session_state.report = report
                progress_bar.progress(100)
            
            status_text.text("✓ ¡Informe generado correctamente!")
            
            # Clean up temporary file (only in normal mode)
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            
            # Success message
            st.success("🎉 ¡Informe generado correctamente!")
            if 'save_path' in locals():
                st.info(f"📁 Transcripción guardada en: {save_path}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.error("Revisa tus claves de API e inténtalo de nuevo.")
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
    st.subheader("📊 Resultados")

    visit_metadata = st.session_state.get('last_visit_metadata')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"informe_visita_comercial_{timestamp}.md"
    transcription_filename = f"transcripcion_{timestamp}.txt"

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📄 Informe", "🎙️ Transcripción"])

    with tab1:
        if visit_metadata:
            customer_display = visit_metadata.get("customer_name") or "N/A"
            date_value = visit_metadata.get("report_date")
            date_display = date_value.strftime("%Y-%m-%d") if date_value else "N/A"
            salesperson_display = visit_metadata.get("sales_person") or "N/A"
            st.markdown(
                f"""
                <div class="summary-card">
                    <h4>Detalles de la visita</h4>
                    <ul class="summary-list">
                        <li><strong>Cliente:</strong> {customer_display}</li>
                        <li><strong>Fecha:</strong> {date_display}</li>
                        <li><strong>Comercial:</strong> {salesperson_display}</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(st.session_state.report)

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="⬇️ Descargar informe (Markdown)",
                data=st.session_state.report,
                file_name=report_filename,
                mime="text/markdown",
                use_container_width=True,
                key="download_report_markdown",
            )
        with dl_col2:
            st.download_button(
                label="⬇️ Descargar transcripción (Texto)",
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

            with st.expander("Detalles de la grabación", expanded=False):
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                with detail_col1:
                    language_code = metadata.get('language_code', 'N/A')
                    st.metric("Idioma", language_code.upper() if language_code else "N/A")
                with detail_col2:
                    st.metric("Interlocutores", len(set(u['speaker'] for u in utterances)))
                with detail_col3:
                    duration = metadata.get('audio_duration')
                    st.metric("Duración", f"{duration/1000:.1f}s" if duration else "N/A")

            transcript_container = st.container()
            for idx, utterance in enumerate(utterances):
                speaker = utterance.get('speaker', '?')
                text = (utterance.get('text') or "").strip()
                if not text:
                    continue
                transcript_container.markdown(
                    f"""
                    <div class="transcript-message">
                        <span class="transcript-speaker">Interlocutor {speaker}</span>
                        <div>{text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.download_button(
                label="⬇️ Descargar transcripción (Texto)",
                data=transcription['formatted_conversation'],
                file_name=transcription_filename,
                mime="text/plain",
                use_container_width=True,
                key="download_transcript_text_detail",
            )
        else:
            st.info("No hay datos de transcripción disponibles.")

    st.markdown(
        """
        <div class="summary-card" style="margin-top:1.5rem;">
            <h4>Todo listo</h4>
            <p style="color:#51627a;margin-bottom:0.75rem;">¿Necesitas procesar otra visita? Reinicia el flujo a continuación.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Procesar otro archivo", use_container_width=True):
        st.session_state.report = None
        st.session_state.transcription = None
        st.session_state.audio_filename = None
        st.session_state.last_upload_info = None
        st.session_state.last_visit_metadata = None
        st.rerun()

# Continue sidebar content (checkbox defined above, rest of content below)
with st.sidebar:
    st.header("ℹ️ Acerca de")
    st.markdown("""
    Esta aplicación utiliza:
    - **AssemblyAI** para la transcripción de audio con diarización de interlocutores
    - **OpenAI GPT-5** para la generación inteligente de informes
    
    El sistema identifica automáticamente a los distintos interlocutores
    y genera un informe estructurado de la visita comercial siguiendo el formato de Provalix Homes.
    """)
    
    st.markdown("---")
    
    st.header("📋 Requisitos")
    if st.session_state.test_mode:
        st.markdown("""
        - Archivo de transcripción en JSON
        - Formato: transcripción guardada de ejecuciones anteriores
        """)
    else:
        st.markdown("""
        - Archivo de audio MP3
        - Calidad de audio nítida
        - Se esperan de 2 a 5 interlocutores
        - Contexto de visita comercial
        """)
    
    st.markdown("---")
    
    st.header("🔑 Estado de las API")
    if st.session_state.test_mode:
        # In test mode, only OpenAI is needed
        st.info("Modo de prueba: solo necesitas la API de OpenAI")
        if api_keys.get('openai'):
            st.success("✅ OPENAI")
        else:
            st.error("❌ OPENAI")
    else:
        for api_name, available in api_keys.items():
            status = "✅" if available else "❌"
            st.markdown(f"{status} {api_name.upper()}")
    
    if (st.session_state.test_mode and api_keys.get('openai')) or (not st.session_state.test_mode and all(api_keys.values())):
        st.success("¡Todas las claves de API necesarias están configuradas!")
    
    st.markdown("---")
    st.caption("Generador de informes de visitas comerciales v1.0")
    st.caption("Creado con Streamlit, AssemblyAI y OpenAI")

