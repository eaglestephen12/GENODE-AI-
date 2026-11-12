#!/usr/bin/env python3
"""Run the full phage host-genus pipeline.

  python run.py --email you@example.com      # download + train + validate + figures
  python run.py --skip-download              # reuse data/*.fasta
"""
import argparse
import json
from pathlib import Path

from sklearn.metrics import classification_report

from phage_host.data import download, load_dataset
from phage_host.evaluate import choose_splits, evaluate_all
from phage_host.features import build_features, cluster_groups
from phage_host.plots import fig_confusion, fig_importance, fig_validation

DEFAULT_GENERA = ["Escherichia", "Mycobacterium", "Pseudomonas",
                  "Staphylococcus", "Klebsiella", "Salmonella"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default="", help="required by NCBI for downloads")
    ap.add_argument("--genera", nargs="+", default=DEFAULT_GENERA)
    ap.add_argument("--per-genus", type=int, default=150)
    ap.add_argument("--k", type=int, default=4, help="k-mer size for composition features")
    ap.add_argument("--cluster-dist", type=float, default=0.8,
                    help="Jaccard distance below which genomes count as homologs")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--skip-download", action="store_true")
    a = ap.parse_args()

    out = Path(a.out_dir)
    out.mkdir(exist_ok=True)
    if not a.skip_download:
        if not a.email:
            raise SystemExit("Provide --email (NCBI requires it) or use --skip-download")
        download(a.genera, a.per_genus, a.email, a.data_dir, a.seed)

    ids, y, seqs = load_dataset(a.genera, a.data_dir)
    classes = sorted(set(y))
    print(f"\n{len(seqs)} genomes, {len(classes)} genera")

    X, names = build_features(seqs, a.k)
    groups = cluster_groups(seqs, a.cluster_dist)
    print(f"homology clusters: {len(set(groups))} (distance threshold {a.cluster_dist})")
    with open(out / "clusters.csv", "w") as fh:
        fh.write("id,genus,cluster\n")
        for i, g, c in zip(ids, y, groups):
            fh.write(f"{i},{g},{c}\n")

    n_splits = choose_splits(y, groups, a.folds)
    results, preds, rf = evaluate_all(X, y, groups, n_splits, a.seed)
    chance = 1 / len(classes)

    print("\n=== Results (macro-F1 / balanced accuracy) ===")
    for k, v in results.items():
        print(f"{k:50s} F1={v['macro_f1']:.3f}  BalAcc={v['balanced_acc']:.3f}"
              f"  (fold F1 {v['fold_f1_mean']:.3f} +/- {v['fold_f1_sd']:.3f})")
    print(f"chance level ~ {chance:.3f}\n")
    print("Per-genus (random forest, honest split):")
    print(classification_report(y, preds["random_forest"], zero_division=0))

    fig_validation(results, chance, out / "fig1_validation_comparison.png")
    fig_confusion(y, preds["random_forest"], classes, out / "fig2_confusion_matrix.png")
    top = fig_importance(rf, names, out / "fig3_feature_importance.png")

    report = classification_report(y, preds["random_forest"], zero_division=0, output_dict=True)
    with open(out / "results.json", "w") as fh:
        json.dump({"n_genomes": len(seqs), "genera": classes, "n_clusters": int(len(set(groups))),
                   "n_splits": n_splits, "chance": chance, "results": results,
                   "per_genus_rf_honest": report, "top_features": top}, fh, indent=2)
    print(f"Saved figures and results.json to {out}/")


if __name__ == "__main__":
    main()
