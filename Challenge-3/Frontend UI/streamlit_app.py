import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Legal Debate", layout="wide")

st.title("⚖️ AI-Powered Legal Debate System")

# -----------------------------
# Generate Case
# -----------------------------
if st.button("🎲 Generate Random Case"):
    response = requests.post(f"{BACKEND_URL}/generate_case")
    if response.status_code == 200:
        st.session_state["case"] = response.json()["case"]
        st.session_state["debate"] = None
        st.session_state["session_id"] = None
    else:
        st.error("Failed to generate case. Please check backend.")

if "case" in st.session_state:
    st.subheader("📄 Case")
    st.write(st.session_state["case"])

# -----------------------------
# Run Debate
# -----------------------------
if "case" in st.session_state and st.button("⚔️ Start Debate"):
    response = requests.post(f"{BACKEND_URL}/debate", json={"case": st.session_state["case"]})
    if response.status_code == 200:
        st.session_state["debate"] = response.json()
        st.session_state["session_id"] = st.session_state["debate"]["session_id"]
    else:
        st.error("Failed to start debate. Please check backend.")

# -----------------------------
# Show Debate
# -----------------------------
if "debate" in st.session_state and st.session_state["debate"]:
    st.subheader("🗣️ Debate Rounds")

    debate = st.session_state["debate"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 RAG Lawyer")
        for turn in debate["rag_lawyer"]:
            st.write(f"**Round {turn['round']}**: {turn['argument']}")

    with col2:
        st.markdown("### 🌀 Chaos Lawyer")
        for turn in debate["chaos_lawyer"]:
            st.write(f"**Round {turn['round']}**: {turn['argument']}")

    # -----------------------------
    # User as Judge
    # -----------------------------
    st.subheader("⚖️ You Are the Judge")
    choice = st.radio("Who wins the case?", ["RAG Lawyer", "Chaos Lawyer"], index=0)

    if st.button("✅ Submit Verdict"):
        response = requests.post(
            f"{BACKEND_URL}/judge_decision",
            json={
                "session_id": st.session_state["session_id"],
                "verdict": choice
            }
        )
        if response.status_code == 200:
            result = response.json()
            st.session_state["debate"]["judge_decision"] = result["judge_decision"]
        else:
            st.error("Failed to submit verdict. Please check backend.")

    # -----------------------------
    # Show Final Verdict
    # -----------------------------
    if st.session_state["debate"]["judge_decision"]:
        st.success(st.session_state["debate"]["judge_decision"])
