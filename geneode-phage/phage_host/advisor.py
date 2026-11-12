"""GENEODE phage helper: soft checks + host-genus call with validated confidence + next steps.

Everything under "Suggested next steps" is RULE-BASED workflow guidance, not a model prediction.
"""
import numpy as np

from .features import build_features
from .softchecks import nearest_in_set, run_checks, sketch

ENTERO = {"Escherichia", "Klebsiella", "Salmonella"}
LEN_RANGE = (20_000, 400_000)


def _band(conf, reliability):
    for b in reliability:
        if b["lo"] <= conf < b["hi"]:
            return b
    return reliability[-1]


def analyse(name, seq, bundle):
    seq = seq.upper()
    checks = run_checks(seq)
    X, _ = build_features([seq], bundle["k"])
    proba = bundle["model"].predict_proba(X)[0]
    classes = list(bundle["model"].classes_)
    order = np.argsort(proba)[::-1]
    ranking = [(classes[i], float(proba[i])) for i in order]
    top, conf = ranking[0]

    mean, sd = bundle["gc_stats"][top]
    gc_z = (checks["gc"] - mean) / sd if sd > 0 else 0.0

    sk = sketch(seq, size=bundle["sketch_size"])
    j, sim = nearest_in_set(sk, bundle["sketch_matrix"], bundle["sketch_size"])
    nearest = {"id": bundle["sketch_ids"][j], "genus": bundle["sketch_labels"][j], "similarity": sim}

    band = _band(conf, bundle["reliability"])
    warnings = []
    if not LEN_RANGE[0] <= checks["length"] <= LEN_RANGE[1]:
        warnings.append(f"Length {checks['length']:,} bp is outside the 20-400 kb range of the training "
                        "genomes. This model expects a complete phage genome; fragments are unreliable.")
    if checks["ambiguous_fraction"] > 0.01:
        warnings.append(f"{checks['ambiguous_fraction']:.1%} of bases are ambiguous (N, R, Y, ...).")
    if abs(gc_z) > 2.5:
        warnings.append(f"GC content ({checks['gc']:.1%}) is unusual for phages of the predicted host "
                        f"({top}: {mean:.1%} +/- {sd:.1%}).")
    coding_bar = bundle.get("coding_p1", 0.60)
    if checks["coding_fraction"] < coding_bar:
        warnings.append(f"Only {checks['coding_fraction']:.0%} of the sequence lies in long ORFs, below "
                        f"the {coding_bar:.0%} seen in 99% of the training phage genomes. Could be a "
                        "fragment, contaminated or non-phage.")

    if sim >= 0.90:
        novelty = (f"Near-identical to a training genome ({nearest['id']}, {nearest['genus']}); "
                   "this is NOT an independent test of the model.")
    elif sim >= 0.20:
        novelty = (f"Has a relative in the training set ({nearest['id']}, {nearest['genus']}, "
                   f"similarity {sim:.2f}). Honest validation applies at the default level (macro-F1 ~0.63).")
    else:
        novelty = (f"No close relative in the training set (best similarity {sim:.2f}). This is "
                   "extrapolation: in validation, performance fell to ~0.43 macro-F1 for distant relatives.")

    notes = []
    if conf < 0.40:
        notes.append("Confidence is low: do not act on this host call.")
    if len(ranking) > 1 and {top, ranking[1][0]} <= ENTERO and ranking[0][1] + ranking[1][1] > 0.6:
        notes.append("Top two candidates are both Enterobacteriaceae (Escherichia/Klebsiella/Salmonella). "
                     "This is the model's known weak spot; treat the host as 'Enterobacteriaceae, genus "
                     "unresolved' until tested.")

    return {"name": name, "checks": checks, "ranking": ranking[:3], "top": top, "confidence": conf,
            "band": band, "gc_z": gc_z, "gc_host": (mean, sd), "nearest": nearest, "novelty": novelty,
            "warnings": warnings, "notes": notes,
            "steps": next_steps(checks, top, conf, ranking, warnings, nearest)}


def next_steps(checks, top, conf, ranking, warnings, nearest):
    steps = []
    if warnings:
        steps.append("Resolve the warnings above first (re-assemble or re-sequence, trim to a complete "
                     "genome, remove contaminating contigs); results on poor input are not meaningful.")
    steps.append("Search for a known relative: BLASTn against NCBI Virus / INPHARED. If a close hit has a "
                 "recorded host, that evidence outranks this model.")
    steps.append("Annotate the genome (e.g. Pharokka, which uses PHANOTATE; tRNAscan-SE for tRNAs) and "
                 "check completeness (CheckV).")
    steps.append("Predict lifestyle (e.g. BACPHLIP) and screen for integrase/repressor genes, toxins, "
                 "virulence and antibiotic-resistance genes (e.g. ABRicate with VFDB/CARD, or "
                 "AMRFinderPlus). Temperate phages or phages carrying such genes are generally unsuitable "
                 "for therapy.")
    steps.append("Place it taxonomically (e.g. VIRIDIC, vConTACT) to see which known phage group it "
                 "belongs to. Strain-level identity needs reference-based comparison; this model does not "
                 "give it.")
    cands = [g for g, p in ranking if p >= 0.15] or [top]
    if conf >= 0.60:
        extra = (f", plus a few strains of the next candidate(s) ({', '.join(cands[1:])}) as controls"
                 if len(cands) > 1 else "")
        steps.append(f"Confirm the host in the lab: spot assay / efficiency of plating on a panel of "
                     f"{top} strains{extra}.")
    else:
        steps.append("Confirm the host in the lab before assuming anything: test a panel covering all "
                     f"candidates ({', '.join(cands)}), since confidence is not high enough to pick one.")
    steps.append("Only if the goal is to express or clone a gene or region (e.g. an endolysin or a "
                 "receptor-binding protein): pick it from the annotation, compare its codon usage/GC with "
                 f"the expression host (this genome is {checks['gc']:.1%} GC), design primers, and choose a "
                 "vector accordingly. Cloning a whole phage genome into a plasmid is not routine; genome "
                 "engineering uses different workflows (e.g. yeast-based or cell-free rebooting).")
    return steps


def format_report(r):
    c = r["checks"]
    b = r["band"]
    lines = [f"=== GENEODE phage helper: {r['name']} ===", "",
             "SOFT CHECKS",
             f"  length            {c['length']:,} bp",
             f"  GC content        {c['gc']:.1%}   (typical for {r['top']} phages: "
             f"{r['gc_host'][0]:.1%} +/- {r['gc_host'][1]:.1%}, z = {r['gc_z']:+.1f})",
             f"  ambiguous bases   {c['ambiguous_fraction']:.2%}",
             f"  coding-like       {c['coding_fraction']:.0%} of sequence in long ORFs"]
    lines += [f"  WARNING: {w}" for w in r["warnings"]]
    lines += ["", "HOST PREDICTION (resolution: host GENUS, not strain)"]
    for g, p in r["ranking"]:
        lines.append(f"  {g:<16s}{p:6.1%}")
    if b["n"] == 0:
        lines.append(f"  Confidence band {b['lo']:.1f}-{min(b['hi'], 1.0):.1f}: no cross-validation "
                     "prediction fell in this band, so its reliability is unknown. Treat as unreliable.")
    else:
        n_txt = f"n={b['n']}" + (", few samples, interpret cautiously" if b["n"] < 30 else "")
        lines.append(f"  Confidence band {b['lo']:.1f}-{min(b['hi'], 1.0):.1f}: in honest cross-validation, "
                     f"predictions in this band were correct {b['accuracy']:.0%} of the time ({n_txt}).")
    lines.append(f"  Novelty: {r['novelty']}")
    lines += [f"  NOTE: {n}" for n in r["notes"]]
    lines += ["", "SUGGESTED NEXT STEPS (rule-based guidance, not a model prediction)"]
    lines += [f"  {i}. {s}" for i, s in enumerate(r["steps"], 1)]
    lines += ["", "Decision support only: validate in the lab and with expert review before acting."]
    return "\n".join(lines)