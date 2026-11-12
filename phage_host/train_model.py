#!/usr/bin/env python3
"""Train the final host-genus model on all data and save it for the helper (predict.py).

Also measures how trustworthy each confidence level is, using honest (cluster-grouped)
cross-validation, and stores that table in the model file.

  python train_model.py            # uses data/*.fasta from run.py
"""
import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold

from phage_host.data import load_dataset
from phage_host.evaluate import choose_splits
from phage_host.features import build_features, cluster_groups
from phage_host.softchecks import coding_fraction, sketch

DEFAULT_GENERA = ["Escherichia", "Mycobacterium", "Pseudomonas",
                  "Staphylococcus", "Klebsiella", "Salmonella"]
EDGES = [0.0, 0.4, 0.6, 0.8, 1.0001]
SKETCH = 2000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--genera", nargs="+", default=DEFAULT_GENERA)
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out", default="models/phage_host_model.joblib")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--cluster-dist", type=float, default=0.8)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    ids, y, seqs = load_dataset(a.genera, a.data_dir)
    classes = sorted(set(y))
    X, _ = build_features(seqs, a.k)
    groups = cluster_groups(seqs, a.cluster_dist)
    n_splits = choose_splits(y, groups, a.folds)

    def rf():
        return RandomForestClassifier(500, class_weight="balanced", n_jobs=-1, random_state=a.seed)

    # out-of-fold probabilities under the honest split -> reliability of each confidence band
    oof = np.zeros((len(y), len(classes)))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=a.seed)
    for tr, te in cv.split(X, y, groups):
        m = rf().fit(X[tr], y[tr])
        assert list(m.classes_) == classes, "a fold is missing a genus"
        oof[te] = m.predict_proba(X[te])
    conf = oof.max(1)
    correct = np.array(classes)[oof.argmax(1)] == y
    reliability = []
    print("\nHonest-CV reliability of the confidence score")
    print(f"{'band':<12}{'n':>6}{'accuracy':>10}")
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        sel = (conf >= lo) & (conf < hi)
        n = int(sel.sum())
        acc = float(correct[sel].mean()) if n else float("nan")
        reliability.append({"lo": lo, "hi": hi, "n": n, "accuracy": acc})
        print(f"{lo:.1f}-{min(hi, 1.0):.1f}{'':<5}{n:>6}{acc:>10.1%}")

    model = rf().fit(X, y)
    gc = X[:, -1]
    gc_stats = {c: (float(gc[y == c].mean()), float(gc[y == c].std())) for c in classes}
    matrix = np.stack([sketch(s, size=SKETCH) for s in seqs])
    coding = np.array([coding_fraction(s) for s in seqs])  # real phage genomes set the warning bar
    print(f"Coding-like fraction in training genomes: median {np.median(coding):.0%}, "
          f"1st percentile {np.percentile(coding, 1):.0%}")

    out = Path(a.out)
    out.parent.mkdir(exist_ok=True)
    joblib.dump({"model": model, "k": a.k, "gc_stats": gc_stats, "reliability": reliability,
                 "sketch_matrix": matrix, "sketch_ids": ids, "sketch_labels": list(y),
                 "sketch_size": SKETCH, "cluster_dist": a.cluster_dist, "n_train": len(y),
                 "coding_p1": float(np.percentile(coding, 1))},
                out, compress=3)
    print(f"\nSaved model to {out} ({len(y)} training genomes)")

    try:  # slide-ready figure
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
        labels = [f"{lo:.1f}-{min(hi, 1.0):.1f}\n(n={r['n']})" for r, lo, hi
                  in zip(reliability, EDGES[:-1], EDGES[1:])]
        accs = [r["accuracy"] if r["n"] else 0 for r in reliability]
        fig, ax = plt.subplots(figsize=(7, 4.3))
        bars = ax.bar(labels, accs, color="#0b7a75")
        for b_, v in zip(bars, accs):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 0.01, f"{v:.0%}", ha="center")
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Model confidence (top predicted probability)")
        ax.set_ylabel("Fraction of predictions correct")
        ax.set_title("Does higher confidence mean more reliable? (honest cross-validation)")
        fig.tight_layout()
        Path("results").mkdir(exist_ok=True)
        fig.savefig("results/fig5_confidence_reliability.png", dpi=200)
        print("Saved results/fig5_confidence_reliability.png")
    except Exception as e:
        print(f"(figure skipped: {e})")


if __name__ == "__main__":
    main()