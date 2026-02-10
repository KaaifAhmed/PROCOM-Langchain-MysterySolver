
# 🕵️‍♂️ SHERLOCK AI (v2.0)

**Autonomous Forensic Reasoning Engine** using LangChain & Groq (Llama 3).

## ⚡ Quick Setup

### 1. Installation

Open your terminal in the project folder:

```bash
# 1. Create & Activate Virtual Env
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

```

### 2. Configuration

Create a file named **`.env`** and add your key:

```env
GROQ_API_KEY=gsk_your_key_here

```

### 3. Launch

```bash
# Optional: Verify system status
python diagnostics.py

# Run the Dashboard
streamlit run dashboard.py

```

---

## 🕵️‍♂️ How to Use

1. **Stage 1 (Audio):** Upload interview tapes (`.mp3`). Click **Transcribe**.
2. **Stage 2 (Docs):** Upload dossiers/photos (`.pdf`, `.jpg`). Click **Analyze**.
3. **Stage 3 (Verdict):** Click **Generate Final Report**. The AI will solve the case.
4. **Chat:** Use the **Sidebar** to interrogate the AI about the evidence.

---

## ⚠️ Troubleshooting

* **Module Not Found?** Run `pip install -r requirements.txt` again.
* **Engine Not Found?** Don't move files. Keep `dashboard.py` and `engine.py` in the same folder.
* **Crash/Hang?** Check your `GROQ_API_KEY` in the `.env` file.
