# Work plan: GENEODE phage host predictor

**Goal:** a small, honestly validated model that shows the GENEODE phage module is real.
**Deadline for building:** today 15:00. **Presentation:** tomorrow.

## Today (until 15:00)

| Time | Task | Done when |
|---|---|---|
| 13:05–13:15 | Setup: unzip, `pip install -r requirements.txt` | `python run.py --help` works |
| 13:15–13:40 | Run `python run.py --email <you>` (downloads ~900 genomes, then trains) | `data/` has 6 FASTA files, `results/` has 3 PNGs + `results.json` |
| 13:40–14:10 | Read the results and sanity-check them (see checklist below) | You can explain every number |
| 14:10–14:30 | Ablation: rerun with `--k 3` and `--k 5`, and with `--cluster-dist 0.6` | Short table in README: how robust is the result? |
| 14:30–14:50 | Slides: follow `docs/presentation_outline.md`, paste the 3 figures | 4–5 slides |
| 14:50–15:00 | Fill the numbers into README "Results" and rehearse the 60-second pitch | README complete |

## Sanity checklist (do not skip: this is what shows seriousness)

- [ ] Shuffled-label control is near chance (about 1/6 = 0.17). If higher, something leaks.
- [ ] Honest F1 is lower than leaky F1. The gap is the finding.
- [ ] Majority baseline is far below the model.
- [ ] Number of homology clusters per genus is reasonable (`results/clusters.csv`).
- [ ] Confusion matrix errors make biological sense (for example Escherichia / Salmonella / Klebsiella mix-ups).
- [ ] Top k-mers are not a trivial artifact (for example GC content dominating is fine to explain; mention it).

## If something breaks

| Problem | Action |
|---|---|
| NCBI slow or timing out | Re-run; downloads are cached per genus. Lower `--per-genus 80` |
| A genus has too few genomes | Drop it: `--genera Escherichia Mycobacterium Pseudomonas Staphylococcus` |
| `AgglomerativeClustering` complains about `metric` | `pip install -U scikit-learn` |
| Only 1–2 clusters per genus | Lower `--cluster-dist` (try 0.6) |
| Honest score near chance | Report it plainly; explain composition limits; present the protein-level roadmap |

## Stretch (only if everything above is done early)

1. Add an MLP (`sklearn.neural_network.MLPClassifier`) to `phage_host/evaluate.py` and compare.
2. Add one real-world example: take a phage genome not in the dataset and show the predicted genus.

## Tomorrow

- Morning: final run for the numbers on the slides, rehearse twice, prepare answers to questions in `docs/presentation_outline.md`.
