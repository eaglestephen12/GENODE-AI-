"""GENEODE Phage Helper: web page (Streamlit).

Run locally:   streamlit run app.py
On Render:     streamlit run app.py --server.port $PORT --server.address 0.0.0.0
"""
from pathlib import Path

import joblib
import streamlit as st

from phage_host.advisor import analyse, format_report
from predict import parse_fasta_text

MODEL = Path(__file__).parent / "models" / "phage_host_model.joblib"
MAX_CHARS = 2_000_000
MAX_RECORDS = 5

st.set_page_config(page_title="GENEODE Phage Helper", page_icon="🧬", layout="centered")


@st.cache_resource
def load_bundle():
    return joblib.load(MODEL)


st.title("GENEODE Phage Helper")
st.caption("Load a complete phage genome sequence to get soft checks, a host-genus prediction "
           "with validated confidence, and suggested next steps. Decision support only. "
           "The prediction is the host genus, not the strain.")

if not MODEL.exists():
    st.error("Model file not found (models/phage_host_model.joblib).")
    st.stop()
bundle = load_bundle()

tab_paste, tab_file = st.tabs(["Paste sequence", "Upload FASTA"])
with tab_paste:
    pasted = st.text_area("FASTA or raw nucleotide sequence", height=200,
                          placeholder=">my_phage\nATGCGT...")
with tab_file:
    upload = st.file_uploader("FASTA file", type=["fasta", "fa", "fna", "txt"])

text = ""
if upload is not None:
    text = upload.getvalue().decode("utf-8", errors="ignore")
elif pasted.strip():
    text = pasted

if st.button("Analyse", type="primary"):
    if not text.strip():
        st.warning("Paste a sequence or upload a FASTA file first.")
        st.stop()
    if len(text) > MAX_CHARS:
        st.error("Input is too large for this demo (limit about 2 MB).")
        st.stop()
    if ">" not in text:
        text = ">pasted_sequence\n" + text

    records = list(parse_fasta_text(text))
    if len(records) > MAX_RECORDS:
        st.info(f"Only the first {MAX_RECORDS} records are analysed.")
    for name, seq in records[:MAX_RECORDS]:
        seq = "".join(ch for ch in seq if ch.isalpha()).upper()
        st.divider()
        st.subheader(name)
        if len(seq) < 1000:
            st.error("Sequence is shorter than 1,000 bp; too short to analyse.")
            continue
        with st.spinner("Analysing..."):
            rep = analyse(name, seq, bundle)
        c = rep["checks"]

        cols = st.columns(4)
        cols[0].metric("Length", f"{c['length']:,} bp")
        cols[1].metric("GC content", f"{c['gc']:.1%}")
        cols[2].metric("Ambiguous bases", f"{c['ambiguous_fraction']:.2%}")
        cols[3].metric("Gene-dense", f"{c['coding_fraction']:.0%}")
        st.caption(f"Typical GC for {rep['top']} phages: {rep['gc_host'][0]:.1%} "
                   f"+/- {rep['gc_host'][1]:.1%} (z = {rep['gc_z']:+.1f})")
        for w in rep["warnings"]:
            st.warning(w)

        st.markdown("#### Host prediction (genus, not strain)")
        for genus, p in rep["ranking"]:
            st.progress(float(p), text=f"{genus}: {p:.1%}")
        b = rep["band"]
        if b["n"] == 0:
            st.info(f"Confidence band {b['lo']:.1f}-{min(b['hi'], 1.0):.1f}: no validation "
                    "prediction fell in this band, so its reliability is unknown. Treat as unreliable.")
        else:
            few = ", few samples, interpret cautiously" if b["n"] < 30 else ""
            st.info(f"In honest cross-validation, predictions with confidence "
                    f"{b['lo']:.1f}-{min(b['hi'], 1.0):.1f} were correct {b['accuracy']:.0%} of the "
                    f"time (n={b['n']}{few}).")
        st.caption("Novelty: " + rep["novelty"])
        for n in rep["notes"]:
            st.warning(n)

        st.markdown("#### Suggested next steps")
        st.caption("Rule-based workflow guidance, not a model prediction.")
        st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(rep["steps"], 1)))
        st.download_button("Download report (.txt)", format_report(rep),
                           file_name=f"{name}_report.txt", key=f"dl_{name}")

st.divider()
st.caption("GENEODE phage module, proof of concept. Trained on 900 NCBI phage genomes from 6 host "
           "genera; honest macro-F1 about 0.63 at the default validation setting. Validate in the "
           "lab and with expert review before acting.")


# checking it