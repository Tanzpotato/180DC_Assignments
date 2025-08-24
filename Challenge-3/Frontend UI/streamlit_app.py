import streamlit as st
import requests
from typing import Any, Dict, List

BACKEND_URL = "http://127.0.0.1:8000"

# ----------------------------
# Streamlit page setup
# ----------------------------
st.set_page_config(page_title="AI Legal Debate", layout="wide")
st.title("⚖️ AI-Powered Legal Debate Simulator")

# ----------------------------
# Session state initialization
# ----------------------------
if "debate_started" not in st.session_state:
    st.session_state["debate_started"] = False
if "debate" not in st.session_state:
    st.session_state["debate"] = {}
if "history" not in st.session_state:
    st.session_state["history"] = []

# ----------------------------
# Helpers
# ----------------------------
def api_post(path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """POST to backend and return JSON dict or {} if error."""
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload or {})
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Backend error {r.status_code}: {r.text}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not reach backend: {e}")
        return {}

def label_for_case(case_obj: Any) -> str:
    """Return a short safe label for sidebar history buttons."""
    if isinstance(case_obj, dict):
        title = case_obj.get("title") or case_obj.get("text") or "Untitled Case"
    else:
        title = str(case_obj) if case_obj else "Untitled Case"
    title = str(title)
    return (title[:40] + "…") if len(title) > 40 else title

# ----------------------------
# Sidebar: Debate History
# ----------------------------
st.sidebar.header("📜 Past Debates")
if st.session_state["history"]:
    for i, past in enumerate(st.session_state["history"]):
        label = f"Case {i+1}: {label_for_case(past.get('case'))}"
        if st.sidebar.button(label, key=f"hist_{i}"):
            st.session_state["debate"] = past.copy()
            st.session_state["debate_started"] = True
else:
    st.sidebar.caption("No past debates yet.")

# ----------------------------
# Start New Debate
# ----------------------------
if not st.session_state["debate_started"]:
    if st.button("🎬 Start New Debate"):
        # 1) Fetch a case
        case_resp = api_post("/generate_case")
        if not case_resp:
            st.stop()

        case = case_resp.get("case")
        if not case:
            st.error("⚠️ No case returned from backend")
            st.stop()

        # 2) Run debate simulation (multi-round)
        debate_resp = api_post("/debate", {"case": case})
        if debate_resp:
            st.session_state["debate"] = debate_resp
            st.session_state["debate_started"] = True

# ----------------------------
# Active Debate View
# ----------------------------
if st.session_state["debate_started"]:
    debate = st.session_state["debate"]
    case_obj = debate.get("case", {})

    # Case details
    st.subheader("📂 Case Details")
    if isinstance(case_obj, dict):
        title = case_obj.get("title", "Untitled Case")
        year = case_obj.get("year", "N/A")
        jur = case_obj.get("jurisdiction", "Unknown")
        text = case_obj.get("text", "")
        st.markdown(f"**{title}** ({year}, {jur})")
        st.write(text)
    else:
        st.write(str(case_obj))

    # Arguments
    st.subheader("🧑‍⚖️ AI Lawyer Arguments")
    pros_rounds: List[Dict[str, Any]] = debate.get("prosecution", []) or debate.get("rag_lawyer", [])
    def_rounds: List[Dict[str, Any]] = debate.get("defense", []) or debate.get("chaos_lawyer", [])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prosecution (RAG Lawyer)**")
        if pros_rounds:
            for turn in pros_rounds:
                st.write(f"**Round {turn.get('round', '?')}:** {turn.get('argument', '')}")
        else:
            st.caption("No prosecution arguments.")

    with col2:
        st.markdown("**Defense (Chaos Lawyer)**")
        if def_rounds:
            for turn in def_rounds:
                st.write(f"**Round {turn.get('round', '?')}:** {turn.get('argument', '')}")
        else:
            st.caption("No defense arguments.")

    st.divider()

    # Judge (user role)
    st.subheader("⚖️ Judge’s Verdict")
    current_choice = st.session_state.get("judge_choice", "Prosecution")
    judge_choice = st.radio(
        "Who wins the case?",
        ["Prosecution", "Defense"],
        index=(0 if current_choice == "Prosecution" else 1),
        key="judge_choice",
        horizontal=True
    )

    if st.button("✅ Submit Verdict & Summarize"):
        debate["judge_decision"] = judge_choice
        st.session_state["debate"] = debate

        payload = {
            "session_id": debate.get("session_id"),
            "case": debate.get("case"),
            "prosecution": pros_rounds,
            "defense": def_rounds,
            "judge_decision": judge_choice,
        }
        summ = api_post("/summarize_verdict", payload)
        if summ:
            debate["summary"] = summ.get("summary", "No summary generated.")
            st.session_state["debate"] = debate
            st.success("Verdict submitted 🎉")

            st.session_state["history"].append(debate.copy())

    # Show existing decision
    if debate.get("judge_decision"):
        st.info(f"**Judge’s Decision:** {debate['judge_decision']}")
    if debate.get("summary"):
        st.write("**Summary:**")
        st.write(debate["summary"])

    st.divider()
    if st.button("🏁 End Debate"):
        st.session_state["debate_started"] = False
        st.session_state["debate"] = {}
