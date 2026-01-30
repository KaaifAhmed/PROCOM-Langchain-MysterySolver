import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from detective_data_loader import get_audio_text, get_documents_text, get_clues_text

load_dotenv()

# --- MODEL SPECIALIZATION ---
# 1. THE SMART ONE (Llama 3.3 70B): For Logic, Extraction, and Verdicts.
smart_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# 2. THE FAST ONE (Llama 3.1 8B): For Organizing, Sorting, and Summarizing.
fast_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# # --- PHASE 0: THE PRE-PROCESSOR (NEW) ---
# def preprocess_raw_data(raw_text, source_name):
#     """
#     Uses the FAST model to clean up messy text before extraction.
#     """
#     print(f"   ...Cleaning up {source_name}...")
    
#     system_prompt = """
#     You are a Data Sanitizer.
#     Your job is to clean messy text from interviews or logs.
    
#     RULES:
#     1. REMOVE: Filler words (um, ah, like), timestamps if they are just noise, and repeated phrases.
#     2. FIX: Typos and broken sentences.
#     3. FORMAT: Return a clean, readable paragraph.
#     """
    
#     template = """
#     SOURCE: {source}
    
#     MESSY TEXT:
#     {text}
    
#     Cleaned Text:
#     """
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human", template)
#     ])
    
#     chain = prompt | fast_llm | StrOutputParser()
    # return chain.invoke({"text": raw_text, "source": source_name})

# --- PHASE 1: ROBUST EXTRACTION ---
def extract_structured_data(raw_text, data_type):
    """
    Uses the SMART model to extract detailed facts/claims.
    data_type: 'FACTS' (Docs) or 'CLAIMS' (Audio)
    """
    print(f"   ...Extracting {data_type} using Smart Model...")
    
    system_prompt = """
    You are a Forensic Data Extractor. Your job is to convert raw text into structured forensic data.
    
    RULES:
    1. EXTRACT: Timestamp (HH:MM), Entity (Person), Action, Location, and Source.
    2. LABELING: 
       - If input is 'FACTS', treat logs/sensors as IRREFUTABLE TRUTH.
       - If input is 'CLAIMS', treat spoken words as UNVERIFIED TESTIMONY.
    3. ACCURACY: Do not hallucinate times. If time is "around 9", write "21:00 (Approx)".
    
    OUTPUT FORMAT (Strict JSON List):
    [
      {{"time": "20:15", "entity": "Alex", "action": "Swiped Keycard", "location": "Lab 1", "type": "{dtype}"}}
    ]
    """
    
    template = """
    DATA TYPE: {dtype}
    RAW TEXT: 
    {text}
    
    Extract the JSON list now. Return ONLY the JSON.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template)
    ])
    
    # We use JSON mode if possible, but standard text parsing is safer across models
    chain = prompt | smart_llm | StrOutputParser()
    return chain.invoke({"text": raw_text, "dtype": data_type})

# --- PHASE 2: THE TIMELINE BUILDER (NEW FUNCTION) ---
def create_timeline(facts, claims):
    """
    Uses the FAST model to merge and sort the data.
    This separates the 'Ordering' logic from the 'Reasoning' logic.
    """
    print("   ...Constructing Master Timeline using Fast Model...")
    
    system_prompt = """
    You are a Timeline Architect.
    
    INPUTS:
    1. FACTS (Verified Logs)
    2. CLAIMS (Witness Statements)
    
    YOUR TASK:
    1. Merge both lists into a single Chronological Timeline (Earliest to Latest).
    2. Align events: If a Claim happens at the same time as a Fact, list them side-by-side.
    3. FLAG GAPS: Identify any period > 30 mins where a suspect is unaccounted for.
    
    OUTPUT FORMAT:
    [Time] [Type] [Entity] - [Description]
    ...
    [GAPS DETECTED]:
    - Suspect X: No activity between [Time A] and [Time B].
    """
    
    template = """
    LIST 1 (FACTS):
    {facts}
    
    LIST 2 (CLAIMS):
    {claims}
    
    Build the Master Timeline.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template)
    ])
    
    chain = prompt | fast_llm | StrOutputParser()
    return chain.invoke({"facts": facts, "claims": claims})

# --- PHASE 3: CONTRADICTION & LOGIC ---
def find_contradictions(timeline):
    """
    Uses the SMART model to find lies.
    """
    print("   ...Detecting Inconsistencies...")
    
    system_prompt = """
    You are a Senior Detective (Hercule Poirot Persona). 
    Your goal is to catch suspects in a lie.
    
    LOGIC RULES:
    1. HIERARCHY OF EVIDENCE: A 'FACT' (Log/CCTV) always overrules a 'CLAIM' (Verbal).
    2. THE LIE: If a suspect claims to be in Location A, but a Fact places them in Location B, that is a LIE.
    3. THE IMPOSSIBLE: If a door opened at 10:00 PM (Fact) but the suspect claims they were asleep (Claim), that is a SUSPICIOUS EVENT.
    
    OUTPUT:
    List every inconsistency found. Be aggressive.
    """
    
    template = """
    MASTER TIMELINE:
    {timeline}
    
    Identify the lies.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template)
    ])
    
    chain = prompt | smart_llm | StrOutputParser()
    return chain.invoke({"timeline": timeline})

# --- PHASE 4: THE FINAL VERDICT ---
def get_final_verdict(contradictions, clues, timeline):
    """
    Uses the SMART model to solve the case.
    """
    print("   ...Delivering Final Verdict...")
    
    system_prompt = """
    You are the Lead Investigator. It is time to name the killer.
    
    METHODOLOGY (MMO):
    1. MEANS: Who had the access/weapon?
    2. MOTIVE: Who benefits? (Check clues).
    3. OPPORTUNITY: Who had a time gap in the timeline?
    
    ELIMINATION:
    - If a suspect has a verified alibi (Fact) for the Time of Death, eliminate them.
    - If a suspect lied about their location during the Time of Death, they are the prime suspect.
    """
    
    template = """
    TIMELINE SUMMARY:
    {timeline}
    
    INCONSISTENCIES FOUND:
    {contradictions}
    
    FORENSIC CLUES:
    {clues}
    
    Who is the killer? Provide the name and the definitive "Smoking Gun" proof.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template)
    ])
    
    chain = prompt | smart_llm | StrOutputParser()
    return chain.invoke({
        "contradictions": contradictions, 
        "clues": clues,
        "timeline": timeline
    })

# --- MAIN EXECUTION FLOW ---
def solve_mystery(audio_text, doc_text, clue_text):
    # 1. Extraction (Smart Model)
    facts = extract_structured_data(doc_text, "FACTS")
    claims = extract_structured_data(audio_text, "CLAIMS")
    
    # 2. Timeline Construction (Fast Model - New Step!)
    master_timeline = create_timeline(facts, claims)
    print("\n--- MASTER TIMELINE ---")
    print(master_timeline)
    print("-----------------------\n")
    
    # 3. Logic Analysis (Smart Model)
    logic_analysis = find_contradictions(master_timeline)
    print("\n--- DETECTIVE'S NOTES ---")
    print(logic_analysis)
    print("-------------------------\n")
    
    # 4. Verdict (Smart Model)
    final_result = get_final_verdict(logic_analysis, clue_text, master_timeline)
    return final_result




# --- TEST ZONE ---

# Load the three data types
audio_input = get_audio_text()
document_input = get_documents_text()  
clue_input = get_clues_text()

result = solve_mystery(audio_input, document_input, clue_input)

print(result)