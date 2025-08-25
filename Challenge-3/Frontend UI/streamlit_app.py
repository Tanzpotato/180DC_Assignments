import streamlit as st
import requests
from typing import Any, Dict, List

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="AI Legal Debate", layout="wide")
st.title("⚖️ AI-Powered Legal Debate Simulator")

# ----------------------------
# Session state init
# ----------------------------
if "debate_started" not in st.session_state:
    st.session_state["debate_started"] = False
if "debate" not in st.session_state:
    st.session_state["debate"] = {}
if "history" not in st.session_state:
    st.session_state["history"] = []

# ----------------------------
# Backend helpers
# ----------------------------
def api_post(path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """POST request to backend."""
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload or {}, timeout=180)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Backend error {r.status_code}: {r.text}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not reach backend: {e}")
        return {}

def label_for_case(case_obj: Any) -> str:
    """Generate short label for sidebar."""
    if isinstance(case_obj, dict):
        title = case_obj.get("title") or case_obj.get("text") or "Untitled Case"
    else:
        title = str(case_obj) if case_obj else "Untitled Case"
    return (title[:40] + "…") if len(title) > 40 else title

# ----------------------------
# Sidebar: Past debates
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

# Info for MOCK LLM
st.sidebar.info("ℹ️ Using MOCK LLM — no API key required")

# ----------------------------
# Start New Debate
# ----------------------------
if not st.session_state["debate_started"]:
    if st.button("🎬 Start New Debate"):
        case_resp = api_post("/generate_case")
        if not case_resp:
            st.stop()
        case = case_resp.get("case")
        if not case:
            st.error("⚠️ No case returned from backend")
            st.stop()

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
        st.markdown(f"**{case_obj.get('title', 'Untitled Case')}** "
                    f"({case_obj.get('year', 'N/A')}, {case_obj.get('jurisdiction', 'Unknown')})")
        st.write(case_obj.get("text", ""))
    else:
        st.write(str(case_obj))

    # Arguments
    st.subheader("🧑‍⚖️ AI Lawyer Arguments")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prosecution (RAG Lawyer)**")
        for turn in debate.get("prosecution", []):
            st.write(f"**Round {turn.get('round')}:** {turn.get('argument')}")
    with col2:
        st.markdown("**Defense (Chaos Lawyer)**")
        for turn in debate.get("defense", []):
            st.write(f"**Round {turn.get('round')}:** {turn.get('argument')}")

    # Judge events
    st.subheader("⚖️ Judge's Random Events")
    for ev in debate.get("judge_events", []):
        st.write(f"**Round {ev.get('round')}:** {ev.get('event')}")

    st.divider()

    # Verdict
    st.subheader("⚖️ Judge’s Verdict")
    judge_choice = st.radio(
        "Who wins?",
        ["Prosecution", "Defense"],
        index=0,
        key="judge_choice",
        horizontal=True
    )

    if st.button("✅ Submit Verdict & Summarize"):
        debate["judge_decision"] = judge_choice
        payload = {
            "session_id": debate.get("session_id"),
            "case": case_obj,
            "case_text": debate.get("case_text", ""),
            "prosecution": debate.get("prosecution", []),
            "defense": debate.get("defense", []),
            "judge_decision": judge_choice,
        }
        summ = api_post("/summarize_verdict", payload)
        if summ:
            debate["summary"] = summ.get("summary", "No summary generated.")
            st.session_state["debate"] = debate
            st.session_state["history"].append(debate.copy())
            st.success("Verdict submitted 🎉")

    if debate.get("judge_decision"):
        st.info(f"**Judge’s Decision:** {debate['judge_decision']}")
    if debate.get("summary"):
        st.write("**Summary:**")
        st.write(debate["summary"])

    st.divider()
    if st.button("🏁 End Debate"):
        st.session_state["debate_started"] = False
        st.session_state["debate"] = {}
