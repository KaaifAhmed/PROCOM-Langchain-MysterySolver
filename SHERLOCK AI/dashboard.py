import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# ==========================================
# 🚨 PROTOCOL SWITCH 🚨
USE_RISKY_TOOLS = False  # Set TRUE only if OpenAI is explicitly allowed
# ==========================================

# --- CONFIGURATION ---
st.set_page_config(page_title="SHERLOCK AI", page_icon="🕵️‍♂️", layout="wide")
load_dotenv(override=True)

# --- DYNAMIC ENGINE LOADING ---
if USE_RISKY_TOOLS:
    try:
        from THE_EYE_VISION_OPENAI import VisionAnalyzer
        engine_status = "⚠️ POWER MODE (OpenAI)"
    except ImportError:
        st.error("OpenAI Module not found. Switching to Safe Mode.")
        from THE_EYE_VISION_GROQ import VisionAnalyzer
        engine_status = "✅ SAFE MODE (Groq)"
else:
    from THE_EYE_VISION_GROQ import VisionAnalyzer
    engine_status = "✅ SAFE MODE (Groq)"

from THE_EAR_PRO import AdvancedForensicEar
from THE_BRAIN_PRO import solve_case

# --- INITIALIZE MEMORY ---
if 'stage1_log' not in st.session_state: st.session_state.stage1_log = ""
if 'stage2_log' not in st.session_state: st.session_state.stage2_log = ""
if 'final_report' not in st.session_state: st.session_state.final_report = ""
if 'smart_context' not in st.session_state: st.session_state.smart_context = "" # For the smart chatbot

# Chat Histories
if 'chat_global' not in st.session_state: st.session_state.chat_global = []

# Initialize Vision Engine Once
if 'vision_engine' not in st.session_state:
    st.session_state.vision_engine = VisionAnalyzer()

# --- HELPER: Q&A BOT ---
def ask_bot(context, question, model="llama-3.1-70b-versatile"):
    """Generic Q&A function for all stages"""
    if not context: return "No evidence collected for this stage yet."
    try:
        chat = ChatGroq(model=model, api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""
        CONTEXT:
        {context}
        
        QUESTION: {question}
        
        INSTRUCTIONS:
        Answer purely based on the context above. Be concise and detective-like.
        If the answer isn't in the context, say 'Insufficient Data'.
        """
        return chat.invoke(prompt).content
    except Exception as e: return f"Error: {e}"

# --- SIDEBAR: GLOBAL INTELLIGENCE ---
with st.sidebar:
    st.title("🕵️ Global Intel")
    st.caption(f"Engine: {engine_status}")
    
    # Global Chat (Sees ALL Evidence)
    st.subheader("💬 Master Interrogation")
    g_query = st.text_input("Query ALL Evidence:", key="g_input")
    if st.button("Ask Sherlock"):
        if g_query:
            # Use Smart Context if available (After Verdict), otherwise raw logs
            if st.session_state.smart_context:
                target_context = st.session_state.smart_context
                st.caption("Using: 🧠 Smart Logic Context")
            else:
                target_context = st.session_state.stage1_log + "\n" + st.session_state.stage2_log
                st.caption("Using: 📄 Raw Evidence Logs")
            
            ans = ask_bot(target_context, g_query)
            st.session_state.chat_global.append((g_query, ans))
    
    # Show History
    with st.expander("Global History", expanded=False):
        for q, a in reversed(st.session_state.chat_global):
            st.info(q)
            st.write(a)
            st.divider()
    
    st.divider()
    if st.button("⚠️ WIPE SYSTEM"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# --- MAIN INTERFACE ---
st.title("📂 CASE DASHBOARD")
tab1, tab2, tab3 = st.tabs(["🔊 STAGE 1: AUDIO", "📄 STAGE 2: DOCS", "⚖️ FINAL VERDICT"])

# ================= STAGE 1: AUDIO =================
with tab1:
    st.header("Stage 1: Audio Forensics")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Upload Tapes")
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a"], key="s1_up")
        
        if audio_file:
            if st.button("Analyze Audio", key="s1_btn"):
                with st.spinner("Transcribing..."):
                    # Save temp
                    with open("temp_s1.mp3", "wb") as f: f.write(audio_file.getbuffer())
                    
                    # Process
                    ear = AdvancedForensicEar()
                    text = ear.process("temp_s1.mp3")
                    
                    timestamp = time.strftime("%H:%M")
                    entry = f"\n[AUDIO LOG {timestamp}]:\n{text}\n"
                    st.session_state.stage1_log += entry
                    st.success("Audio transcribed!")
        
        st.text_area("Audio Logs", st.session_state.stage1_log, height=300)

    with col2:
        st.subheader("💬 Audio Q&A")
        s1_q = st.text_input("Ask about the Audio:", key="s1_input")
        if s1_q:
            ans = ask_bot(st.session_state.stage1_log, s1_q)
            st.info(f"Q: {s1_q}")
            st.success(f"A: {ans}")

# ================= STAGE 2: DOCS =================
with tab2:
    st.header("Stage 2: Document & Visual Forensics")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Upload Evidence")
        doc_file = st.file_uploader("Upload Dossier/Photos", type=["pdf", "png", "jpg", "jpeg"], key="s2_up")
        
        if doc_file:
            if st.button("Analyze Evidence", key="s2_btn"):
                with st.spinner(f"Scanning with {engine_status}..."):
                    # Determine type
                    ext = doc_file.name.split(".")[-1].lower()
                    fname = f"temp_s2.{ext}"
                    with open(fname, "wb") as f: f.write(doc_file.getbuffer())
                    
                    # Process using Vision Engine
                    result = st.session_state.vision_engine.process_file(fname, ext)
                    
                    timestamp = time.strftime("%H:%M")
                    entry = f"\n[EVIDENCE LOG {timestamp} - {doc_file.name}]:\n{result}\n"
                    st.session_state.stage2_log += entry
                    st.success("Evidence Processed!")
        
        st.text_area("Forensic Logs", st.session_state.stage2_log, height=300)

    with col2:
        st.subheader("💬 Document Q&A")
        s2_q = st.text_input("Ask about Documents:", key="s2_input")
        if s2_q:
            ans = ask_bot(st.session_state.stage2_log, s2_q)
            st.info(f"Q: {s2_q}")
            st.success(f"A: {ans}")

# ================= STAGE 3: VERDICT =================
with tab3:
    st.header("Stage 3: Final Reasoning")
    
    if st.button("🚀 GENERATE FINAL REPORT", type="primary"):
        # Check if we have evidence
        has_audio = bool(st.session_state.stage1_log.strip())
        has_docs = bool(st.session_state.stage2_log.strip())
        
        if not (has_audio or has_docs):
            st.error("No evidence found! Please complete Stages 1 & 2.")
        else:
            with st.spinner("🧠 Connecting the dots... Constructing Timeline... Identifying Killer..."):
                # Call the Bridge (Brain Pro)
                # It returns: (Report String, Context String)
                report, context = solve_case(
                    st.session_state.stage1_log, 
                    st.session_state.stage2_log
                )
                
                # Store results
                st.session_state.final_report = report
                st.session_state.smart_context = context
                st.balloons()
    
    if st.session_state.final_report:
        st.markdown("### 🕵️‍♂️ FINAL CASE REPORT")
        st.markdown(st.session_state.final_report)
        
        with st.expander("See Underlying Logic (Timeline & Contradictions)"):
            st.text(st.session_state.smart_context)