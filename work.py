# ...existing code...
import streamlit as st
import re

st.set_page_config(page_title="Medical Report Chat (no saving)", layout="wide")

# --- Add missing NLP helpers to fix NameError ---
def sentences(text: str):
    parts = re.split(r'(?<=[\.\?\!])\s+', (text or "").strip())
    return [p.strip() for p in parts if p.strip()]

KEYWORDS = [
    'diagnosis','impression','finding','recommend','recommendation',
    'normal','abnormal','mass','lesion','tumor','fracture','inflammation',
    'infection','elevated','decreased','reduced','stable'
]

POSITIVE = ['normal','unremarkable','within normal limits','no acute','stable']
NEGATIVE = ['abnormal','mass','lesion','tumor','fracture','infection','inflammation','elevated','decreased','reduced']

def summarize_report(text: str, max_sentences: int = 3):
    sents = sentences(text)
    if not sents:
        return ["No report text provided."]
    scores = []
    for s in sents:
        low = s.lower()
        score = 0
        for kw in KEYWORDS:
            if kw in low:
                score += 2
        score += min(len(s.split()), 40) / 40.0
        scores.append((score, s))
    scores.sort(reverse=True, key=lambda x: x[0])
    chosen = [s for _, s in scores[:max_sentences]]
    return chosen

def pros_cons(text: str):
    low = (text or "").lower()
    pros = []
    cons = []
    for p in POSITIVE:
        if p in low:
            pros.append(p)
    for n in NEGATIVE:
        if n in low:
            cons.append(n)
    return sorted(set(pros)), sorted(set(cons))

def suggestions_from_text(text: str):
    low = (text or "").lower()
    sug = []
    if any(w in low for w in ['follow-up','recommend','recommendation','repeat']):
        sug.append('Follow-up recommended (see report recommendations).')
    if any(w in low for w in ['biopsy','suspicious','tumor','mass','lesion']):
        sug.append('Consider specialist referral and possible biopsy/imaging.')
    if not sug:
        sug.append('If unclear, consult your clinician for next steps.')
    return sug
# ...existing code...

# --- session-state compatibility helper (NEW) ---
def _ensure_history_container():
    """
    Return a mutable list acting as the chat history.
    Prefer st.session_state.history when available; otherwise use module-global fallback.
    This avoids AttributeError on older Streamlit versions.
    """
    if hasattr(st, "session_state"):
        if "history" not in st.session_state:
            st.session_state.history = []
        return st.session_state.history
    # fallback: global in-memory history (ephemeral for the process)
    if "_local_history" not in globals():
        globals()["_local_history"] = []
    return globals()["_local_history"]

# Use the helper to get the history list
history = _ensure_history_container()

# --- UI ---
st.title("Medical Report Chat — In-memory only")
st.caption("No report data is stored to disk or external services. All for your safety😊.")

with st.sidebar:
    st.header("Input")
    uploaded = st.file_uploader("Upload a medical report (text)", type=['txt', 'text'])
    pasted = st.text_area("Or paste report text here", height=200)
    max_sentences = st.number_input("Max summary sentences", min_value=1, max_value=10, value=3)
    st.markdown("Use the chat box on the right for greetings or to ask for summarization.")

# Ensure report_text is defined before use
report_text = ""

# replace direct st.session_state.history usage with `history`
if uploaded is not None:
    try:
        bytes_data = uploaded.read()
        report_text = bytes_data.decode('utf-8')
    except Exception:
        try:
            report_text = bytes_data.decode('latin-1')
        except Exception:
            report_text = ""
if not report_text:
    report_text = pasted or ""

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Report")
    st.write("Paste or upload a medical report. Nothing is saved.")
    report_display = st.text_area("Report text", value=report_text, height=400, key="report_area")
    if st.button("Summarize Report"):
        summary = summarize_report(report_display, max_sentences=max_sentences)
        pros, cons = pros_cons(report_display)
        suggestions = suggestions_from_text(report_display)
        history.append({
            "type": "summary",
            "summary": summary,
            "pros": pros,
            "cons": cons,
            "suggestions": suggestions
        })
        st.success("Summary generated (in-memory only).")

with col2:
    st.subheader("Chat")
    user_msg = st.text_input("Type a message (e.g. hi, summarize)", key="chat_input")
    if st.button("Send"):
        msg = (user_msg or "").strip()
        reply_obj = {"type": "reply", "message": msg}
        lm = msg.lower()
        if any(g in lm for g in ['hello','hi','hey','good morning','good afternoon','good evening']):
            reply = 'Hello — I can summarize a medical report if you paste it and click "Summarize Report".'
            reply_obj["reply"] = reply
        elif 'summar' in lm or 'analy' in lm or 'report' in lm:
            if report_display and report_display.strip():
                summary = summarize_report(report_display, max_sentences=max_sentences)
                pros, cons = pros_cons(report_display)
                suggestions = suggestions_from_text(report_display)
                reply_obj.update({
                    "reply": "Report summary (generated in-memory):",
                    "summary": summary,
                    "pros": pros,
                    "cons": cons,
                    "suggestions": suggestions
                })
            else:
                reply_obj["reply"] = "Please paste or upload the report text first."
        elif any(t in lm for t in ['thank','thanks']):
            reply_obj["reply"] = "You're welcome."
        else:
            reply_obj["reply"] = "I can greet and summarize a pasted report. Try saying 'summarize' or paste a report and click Summarize Report."
        history.append(reply_obj)
        # safe rerun: only call experimental_rerun if available
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.success("Message processed (in-memory).")

    st.markdown("### Conversation (in-memory)")
    for item in reversed(history[-20:]):
        if item.get("type") == "summary":
            st.markdown("**Summary generated:**")
            for s in item["summary"]:
                st.write("-", s)
            if item["pros"]:
                st.write("Pros:", ", ".join(item["pros"]))
            if item["cons"]:
                st.write("Cons:", ", ".join(item["cons"]))
            st.write("Suggestions:", "; ".join(item["suggestions"]))
            st.markdown("---")
        else:
            st.write("User:", item.get("message", ""))
            st.write("Bot:", item.get("reply", ""))
            if "summary" in item:
                for s in item["summary"]:
                    st.write("-", s)
                if item.get("pros"):
                    st.write("Pros:", ", ".join(item["pros"]))
                if item.get("cons"):
                    st.write("Cons:", ", ".join(item["cons"]))
                st.write("Suggestions:", "; ".join(item.get("suggestions", [])))
            st.markdown("---")

st.caption("All processing is ephemeral and kept in session memory only. No files or data are written to disk.")
# ...existing code...