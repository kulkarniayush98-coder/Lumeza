import streamlit as st
import re

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="LUMEZA – Medical Summariser", layout="wide")


# -------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------
def summarize_report(text, max_sentences=3):
    sentences = re.split(r'[.!?]\s+', text.strip())
    return sentences[:max_sentences]


# Basic keyword → doctor mapping
SPECIALIST_MAP = {
    "heart": "Cardiologist",
    "cardiac": "Cardiologist",
    "hypertension": "Cardiologist",
    "blood pressure": "Cardiologist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
    "fracture": "Orthopedic Surgeon",
    "bone": "Orthopedic Specialist",
    "liver": "Hepatologist",
    "kidney": "Nephrologist",
    "renal": "Nephrologist",
    "lung": "Pulmonologist",
    "asthma": "Pulmonologist",
    "cholesterol": "Cardiologist",
    "infection": "Internal Medicine Specialist",
    "anemia": "Hematologist",
    "neurology": "Neurologist",
    "stroke": "Neurologist",
}

def detect_specialist(text):
    text_l = text.lower()
    found = []
    for keyword, doctor in SPECIALIST_MAP.items():
        if keyword in text_l:
            found.append(doctor)
    return list(set(found)) if found else ["General Physician (for initial evaluation)"]


def extract_conditions(text):
    words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())
    common_med_terms = [
        "hypertension", "diabetes", "infection", "cholesterol", "anemia", "fracture",
        "inflammation", "renal", "thyroid", "asthma", "tumor", "lesion", "mass"
    ]
    found = [w for w in words if w in common_med_terms]
    return list(set(found))


def explain_term(term):
    explanations = {
        "hypertension": "Hypertension means consistently high blood pressure.",
        "diabetes": "Diabetes is a condition where blood sugar levels are elevated.",
        "anemia": "Anemia means low hemoglobin or reduced red blood cells.",
        "cholesterol": "High cholesterol increases the risk of heart disease.",
        "thyroid": "Thyroid issues affect metabolism, energy, and hormones.",
        "asthma": "Asthma is a chronic lung condition causing breathing difficulty.",
    }
    return explanations.get(term.lower(), None)


# Pros/cons suggestions
def pros_cons(text):
    return ["Clear structure"], ["Needs more detail"]

def suggestions_from_text(text):
    return ["Consider follow-up tests", "Discuss findings with a specialist"]


# -------------------------------------------------------------------
# CSS FOR UI
# -------------------------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #edf7f6;
}

/* Animated Gradient Title */
.gradient-title {
  font-size: 55px;
  font-weight: bold;
  text-align: center;
  background: linear-gradient(90deg, #51e2f5, #3dd1c8, #60efff, #00bbf0);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientMove 6s ease infinite;
  margin-bottom: -5px;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.subtitle {
  color: #2e2e2e;
  text-align: center;
  font-size: 20px;
  margin-top: -10px;
}

.section-title {
    font-size: 32px;
    font-weight: 700;
    color: #00bbf0;
    margin-bottom: 10px;
}

.chat-user {
    background-color: #51e2f5;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 8px;
    width: fit-content;
}

.chat-bot {
    background-color: #edf7f6;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 8px;
    width: fit-content;
    border: 1px solid #51e2f5;
}

.box {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #51e2f5;
}

</style>
""", unsafe_allow_html=True)



# -------------------------------------------------------------------
# TOP TITLE
# -------------------------------------------------------------------
st.markdown("<div class='gradient-title'>🩺 LUMEZA Medical Intelligence</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Fast • Private • In-Browser Medical Insight</p>", unsafe_allow_html=True)
st.write("---")


# -------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "📄 Report Summariser", "💬 Chat Assistant"])

st.sidebar.info("All processing stays inside your browser only.")



# -------------------------------------------------------------------
# PAGE — HOME
# -------------------------------------------------------------------
if page == "🏠 Home":
    st.markdown("### 🚀 Welcome to LUMEZA")
    st.write("""
LUMEZA helps you:
- Summarize medical reports  
- Extract key issues  
- Suggest appropriate doctors  
- Explain medical terms  
- Chat about your report  

Use the sidebar to navigate.
""")


# -------------------------------------------------------------------
# PAGE — REPORT SUMMARISER
# -------------------------------------------------------------------
elif page == "📄 Report Summariser":

    st.markdown("<div class='section-title'>📄 Report Summariser</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload medical report (.txt)", type=['txt'])
    pasted = st.text_area("Or paste report text here", height=180)

    max_sentences = st.slider("Max summary sentences", 1, 10, 3)

    report_text = ""
    if uploaded:
        report_text = uploaded.read().decode("utf-8", errors="ignore")
    if pasted:
        report_text = pasted

    if st.button("🚀 Summarize"):
        if report_text.strip():

            st.session_state.report_text = report_text  # store for chat assistant

            summary = summarize_report(report_text, max_sentences)
            pros, cons = pros_cons(report_text)
            suggestions = suggestions_from_text(report_text)

            st.markdown("### 🧠 Summary")
            st.markdown("<div class='box'>", unsafe_allow_html=True)
            for s in summary:
                st.markdown(f"- {s}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### 👍 Pros")
            st.info(", ".join(pros))

            st.markdown("### ⚠ Cons")
            st.warning(", ".join(cons))

            st.markdown("### 💡 Suggestions")
            st.success("; ".join(suggestions))
        else:
            st.error("Please upload or paste a report first.")



# -------------------------------------------------------------------
# PAGE — CHAT ASSISTANT (SMART & REPORT-AWARE)
# -------------------------------------------------------------------
elif page == "💬 Chat Assistant":

    st.markdown("<div class='section-title'>💬 Chat with LUMEZA</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    msg = st.text_input("Ask something about your medical report:")

    if st.button("Send"):
        if msg.strip():
            st.session_state.chat_history.append(("user", msg))

            # If no report available
            if "report_text" not in st.session_state:
                reply = "Please upload and summarize a medical report first in the 📄 Report Summariser page."
                st.session_state.chat_history.append(("bot", reply))
            else:
                report = st.session_state.report_text.lower()
                user_l = msg.lower()

                # 1. Doctor suggestion
                if "doctor" in user_l or "specialist" in user_l or "consult" in user_l:
                    specialists = detect_specialist(report)
                    reply = f"Based on your report, you may consult: **{', '.join(specialists)}**."

                # 2. Explain terms
                elif "meaning" in user_l or "explain" in user_l:
                    words = user_l.split()
                    explained = False
                    for w in words:
                        meaning = explain_term(w)
                        if meaning:
                            reply = f"**{w.capitalize()}** → {meaning}"
                            explained = True
                            break
                    if not explained:
                        reply = "Please specify the medical term you want explained."

                # 3. Conditions in report
                elif "issue" in user_l or "problem" in user_l or "condition" in user_l:
                    cond = extract_conditions(report)
                    if cond:
                        reply = f"Your report mentions: **{', '.join(cond)}**."
                    else:
                        reply = "I couldn’t detect specific conditions in the report."

                # 4. General Q&A
                else:
                    reply = "I can help with:\n- Which doctor to consult\n- Explaining medical terms\n- Identifying issues in the report\nTry asking: **Which doctor should I consult?**"

                st.session_state.chat_history.append(("bot", reply))

    # Display chat history
    for sender, text in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div class='chat-user'>👤 {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>🤖 {text}</div>", unsafe_allow_html=True)
