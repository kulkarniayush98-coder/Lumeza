import streamlit as st
import re

st.set_page_config(page_title="LUMEZA MEDICAL REPORT SUMMARISER", layout="wide")

# --- session-state compatibility helper ---
def _ensure_history_container():
    if hasattr(st, "session_state"):
        if "history" not in st.session_state:
            st.session_state.history = []
        return st.session_state.history
    if "_local_history" not in globals():
        globals()["_local_history"] = []
    return globals()["_local_history"]

history = _ensure_history_container()

# --- Dummy function implementations to avoid NameError ---
def summarize_report(text, max_sentences=3):
    sentences = re.split(r'[.!?]\s+', text.strip())
    return sentences[:max_sentences]

def pros_cons(text):
    return ["Well-structured"], ["Could use more detail"]

def suggestions_from_text(text):
    return ["Consider follow-up test", "Discuss with a specialist"]

# --- UI ---
st.title("LUMEZA MEDICAL REPORT SUMMARISER")
st.caption("No report data is stored to disk or external services. All for your safety😊 one more this is completly for temporary understanding dont forget to consult your doctor")

with st.sidebar:
    st.header("Input")
    uploaded = st.file_uploader("Upload a medical report (text)", type=['txt', 'text'])
    pasted = st.text_area("Or paste report text here", height=200)
    max_sentences = st.number_input("Max summary sentences", min_value=1, max_value=10, value=3)
    st.markdown("Use the chat box on the right for greetings or to ask for summarization.")

# --- Load report content ---
report_text = ""
bytes_data = None

if uploaded is not None:
    try:
        bytes_data = uploaded.read()
        report_text = bytes_data.decode('utf-8')
    except Exception:
        try:
            report_text = bytes_data.decode('latin-1') if bytes_data else ""
        except Exception:
            report_text = ""

if not report_text:
    report_text = pasted or ""

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Report")
    st.write("Paste or upload a medical report. Nothing is saved as your safety is our policy.")
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

        if any(g in lm for g in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'good night', 'namaste']):
            reply = 'Hi there I can summarize a medical report if you paste it and click "Summarize Report" But even consult your doctor😊.'
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

        elif any(t in lm for t in ['thank', 'thanks']):
            reply_obj["reply"] = "You're welcome."

        else:
            reply_obj["reply"] = "I can greet and summarize a pasted report. Try saying 'summarize' or paste a report and click Summarize Report but don't forget to consult your doc😊."

        history.append(reply_obj)
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
            st.write("you:", item.get("message", ""))
            st.write("LUMEZA:", item.get("reply", ""))
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
