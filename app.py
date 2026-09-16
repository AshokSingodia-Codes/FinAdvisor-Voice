import streamlit as st
import tempfile
import os
from gtts import gTTS
from groq import Groq
from graph.workflow import app_graph
from config.settings import settings

st.set_page_config(layout="wide", page_title="FinAdvisor-X Chat")

# Initialize Groq Client for Whisper Audio Transcription
groq_client = Groq(api_key=settings.GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Settings) ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    voice_mode = st.toggle("🔊 Voice Assistant Mode", value=True, help="If unmuted, the AI will speak its responses aloud.")
    st.markdown("---")
    st.markdown("### 🌙 Theme")
    st.markdown("Use the **⋮ menu** in the top right -> **Settings** -> **Theme** to switch between Light & Dark mode.")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("🎙️ FinAdvisor-X")
st.markdown("*(Powered by Groq, Llama-3.3, and LangGraph)*")

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")
        if "trace" in msg and msg["trace"] is not None:
            with st.expander("Agent Reasoning Trace"):
                st.write(msg["trace"])

# --- INPUT AREA (ChatGPT Style) ---
# Place text and audio inputs near each other
col1, col2 = st.columns([1, 10])
with col1:
    user_audio = st.audio_input("🎤", label_visibility="collapsed")
with col2:
    user_text = st.chat_input("Message FinAdvisor-X...")

query = None

if user_text:
    query = user_text
elif user_audio:
    with st.spinner("Transcribing your voice..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(user_audio.getvalue())
            tmp_audio_path = tmp_audio.name
            
        with open(tmp_audio_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
              file=(tmp_audio_path, file.read()),
              model="whisper-large-v3",
              response_format="text"
            )
        query = transcription
        os.remove(tmp_audio_path)

# --- PROCESS NEW QUERY ---
if query:
    # 1. Display User Message Instantly
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query, "audio": None, "trace": None})
    
    # 2. Agent Thinking Phase
    with st.chat_message("assistant"):
        with st.status("🧠 Agent is thinking...", expanded=True) as status:
            final_state = {}
            # Stream the graph to show live step-by-step progress
            for output in app_graph.stream({"original_question": query}):
                for node_name, state in output.items():
                    status.write(f"✅ Completed step: **{node_name.replace('_', ' ').title()}**")
                    final_state = state
            
            result_state = final_state
            status.update(label="Response Ready!", state="complete", expanded=False)

        # 3. Final Output
        answer = result_state.get("final_answer")
        verification_status = result_state.get('verification_passed', False)
        
        if not verification_status and not answer:
            answer = result_state.get("draft_answer", "Sorry, I could not generate an answer.") + "\n\n*(Note: This answer failed verification!)*"
        
        st.write(answer)
        
        # 4. Trace Logic
        trace = (
            f"**Routing Decision:** {result_state.get('routing_decision')}\n\n"
            f"**Verification Passed:** {verification_status}\n\n"
            f"**Retrieved Chunks:** {len(result_state.get('retrieved_context', []))}"
        )
        with st.expander("Agent Reasoning Trace"):
            st.write(trace)
        
        # 5. TTS Voice Generation (if enabled)
        audio_bytes = None
        if voice_mode:
            with st.spinner("Generating Voice..."):
                clean_text = answer.replace("*", "")
                tts = gTTS(text=clean_text, lang='en', tld='us')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_tts:
                    tts.save(tmp_tts.name)
                    tmp_tts_path = tmp_tts.name
                    
                with open(tmp_tts_path, "rb") as f:
                    audio_bytes = f.read()
                
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                os.remove(tmp_tts_path)
        
        # Save to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer,
            "audio": audio_bytes,
            "trace": trace
        })
