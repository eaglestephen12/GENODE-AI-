#!/usr/bin/env python3
"""GENEODE phage helper: load a sequence, run soft checks, predict host genus, suggest next steps.

  python predict.py my_phage.fasta
  python predict.py --accession NC_001604 --email you@example.com   # fetch from NCBI
Run `python train_model.py` once first (needs data/ from run.py).
"""
import argparse
import json
from pathlib import Path

import joblib

from phage_host.advisor import analyse, format_report


def parse_fasta_text(text):
    name, seq = None, []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(">"):
            if name:
                yield name, "".join(seq)
            name, seq = line[1:].split()[0], []
        elif line:
            seq.append(line)
    if name:
        yield name, "".join(seq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fasta", nargs="?", help="FASTA file (one or more records)")
    ap.add_argument("--accession", help="fetch this NCBI accession instead of a file")
    ap.add_argument("--email", default="", help="required with --accession")
    ap.add_argument("--model", default="models/phage_host_model.joblib")
    ap.add_argument("--out-dir", default="reports", help="where to save the text reports")
    a = ap.parse_args()

    if not Path(a.model).exists():
        raise SystemExit(f"Model not found: {a.model}. Run `python train_model.py` first.")
    bundle = joblib.load(a.model)

    if a.accession:
        if not a.email:
            raise SystemExit("--email is required with --accession")
        from Bio import Entrez
        Entrez.email = a.email
        text = Entrez.efetch(db="nuccore", id=a.accession, rettype="fasta", retmode="text").read()
    elif a.fasta:
        text = Path(a.fasta).read_text()
    else:
        raise SystemExit("Give a FASTA file or --accession")

    out = Path(a.out_dir)
    out.mkdir(exist_ok=True)
    for name, seq in parse_fasta_text(text):
        rep = analyse(name, seq, bundle)
        txt = format_report(rep)
        print("\n" + txt + "\n")
        (out / f"{name}.txt").write_text(txt)
        (out / f"{name}.json").write_text(json.dumps(rep, indent=2, default=float))
    print(f"Reports saved to {out}/")


if __name__ == "__main__":
    main()