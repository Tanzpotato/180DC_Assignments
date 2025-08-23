import requests, streamlit as st

API = "http://127.0.0.1:8000"

st.title("⚖️ Courtroom Chaos: AI Legal Debate")

case = st.text_area("Enter a legal scenario", "A man sues a parrot for defamation.")

if st.button("Generate Case"):
    r = requests.post(f"{API}/generate_case", json={"case": case})
    st.session_state["case"] = r.json()["case"]

if st.button("Start Debate"):
    r = requests.post(f"{API}/debate", json={"case": st.session_state.get('case', case)})
    st.session_state["debate"] = r.json()

debate = st.session_state.get("debate")
if debate:
    st.subheader("RAG Lawyer (Prosecution)")
    st.write(debate["rag_lawyer"]["argument"])
    st.json(debate["rag_lawyer"]["metadata"])

    st.subheader("Chaos Lawyer (Defense)")
    st.write(debate["chaos_lawyer"]["argument"])
    st.caption(debate["chaos_lawyer"]["rhetoric"])

    st.subheader("Judge Panel")
    verdict = st.selectbox("Verdict", ["Pending","RAG","Chaos","Hung"])
    new_evidence = st.text_input("Introduce new evidence (optional)")
    role_rev = st.checkbox("Role Reversal")

    if st.button("Submit Decision"):
        payload = {
            "session_id": debate.get("session_id"),
            "verdict": None if verdict=="Pending" else verdict,
            "new_evidence": new_evidence or None,
            "role_reversal": role_rev
        }
        r = requests.post(f"{API}/judge_decision", json=payload)
        st.session_state["debate"] = r.json()
        st.experimental_rerun()
