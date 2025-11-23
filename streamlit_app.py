
import streamlit as st
from io import StringIO
from scoring import evaluate_transcript

st.set_page_config(page_title="Nirmaan AI – Intro Scorer", layout="wide")
st.title("Nirmaan AI – Spoken Introduction Scorer")
st.write("Paste a student's self-introduction transcript or upload a .txt file.")

with st.sidebar:
    st.header("Options")
    duration = st.number_input("Audio duration (seconds, optional)", min_value=0.0, value=0.0)
    show_raw = st.checkbox("Show raw JSON output", value=True)

tab_in, tab_out = st.tabs(["1️⃣ Input", "2️⃣ Results"])

with tab_in:
    uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"])
    default_text = ""
    if uploaded:
        default_text = StringIO(uploaded.getvalue().decode("utf-8", errors="ignore")).read()
    transcript = st.text_area("Transcript", value=default_text, height=250)
    run = st.button("Score introduction ✅")

with tab_out:
    if run:
        if not transcript.strip():
            st.error("Please enter or upload a transcript.")
        else:
            with st.spinner("Scoring..."):
                res = evaluate_transcript(transcript, duration_seconds=(duration or None))
            st.session_state["res"] = res

    if "res" not in st.session_state:
        st.info("Run the scorer from the Input tab.")
    else:
        res = st.session_state["res"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall score (0–100)", f"{res['overall_score']:.1f}")
        with col2:
            st.write("Meta")
            st.json(res["meta"])
        st.subheader("Criterion-wise scores")
        rows = [
            {
                "Criterion": c["name"],
                "Score": c["score"],
                "Max": c["max_score"],
                "Norm (0–1)": c["score_normalized_0_1"],
            }
            for c in res["criteria"]
        ]
        st.dataframe(rows, use_container_width=True)
        st.subheader("Details")
        for c in res["criteria"]:
            with st.expander(f"{c['name']} – {c['score']}/{c['max_score']}"):
                st.json(c["details"])
        if show_raw:
            st.subheader("Raw JSON")
            st.json(res)
