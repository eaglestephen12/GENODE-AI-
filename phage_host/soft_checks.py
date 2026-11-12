"""Soft checks on a single input sequence: composition, ambiguity, coding-likeness, MinHash sketch."""
import numpy as np

from .features import encode, kmer_idx, revcomp


# ---------------------------------------------------------------- MinHash sketch (novelty check)
def _mix(x):
    x = x.astype(np.uint64)
    x ^= x >> np.uint64(33)
    x *= np.uint64(0xFF51AFD7ED558CCD)
    x ^= x >> np.uint64(33)
    x *= np.uint64(0xC4CEB9FE1A85EC53)
    x ^= x >> np.uint64(33)
    return x


def sketch(seq, k=10, size=2000):
    """Bottom-`size` MinHash of the 10-mer set (both strands). Estimates Jaccard similarity."""
    c = encode(seq)
    u = np.unique(np.concatenate([kmer_idx(c, k), kmer_idx(revcomp(c), k)]))
    return np.sort(_mix(u))[:size]


def jaccard_estimate(a, b, size=2000):
    union = np.union1d(a, b)[:size]
    if len(union) == 0:
        return 0.0
    inter = np.intersect1d(a, b, assume_unique=True)
    return float(np.isin(union, inter).mean())


def nearest_in_set(query_sketch, matrix, size=2000):
    sims = np.array([jaccard_estimate(query_sketch, row, size) for row in matrix])
    i = int(np.argmax(sims))
    return i, float(sims[i])


# ------------------------------------------------------------------------- coding-likeness
def _orf_cover(codes, min_codons=100):
    """Boolean coverage of ORFs (ATG..stop, >= min_codons) on one strand, all three frames."""
    n = len(codes)
    cover = np.zeros(n, dtype=bool)
    for f in range(3):
        m = (n - f) // 3
        if m < 2:
            continue
        c = codes[f:f + 3 * m].astype(np.int64).reshape(m, 3)
        valid = (c >= 0).all(axis=1)
        idx = np.where(valid, c[:, 0] * 16 + c[:, 1] * 4 + c[:, 2], -1)
        stops = np.where(np.isin(idx, (48, 50, 56)))[0]  # TAA, TAG, TGA
        bounds = np.concatenate([[-1], stops, [m]])
        for a, b in zip(bounds[:-1], bounds[1:]):
            seg = idx[a + 1:b]
            if len(seg) < min_codons:
                continue
            atg = np.where(seg == 14)[0]  # ATG
            if len(atg) == 0:
                continue
            s = a + 1 + atg[0]
            if b - s >= min_codons:
                cover[f + 3 * s: min(f + 3 * b + 3, n)] = True
    return cover


def coding_fraction(seq):
    """Fraction of the sequence inside long ORFs on either strand (phage genomes are gene-dense)."""
    c = encode(seq)
    return float((_orf_cover(c) | _orf_cover(revcomp(c))[::-1]).mean())


# ------------------------------------------------------------------------------- summary
def run_checks(seq):
    n = len(seq)
    s = seq.upper()
    gc = (s.count("G") + s.count("C")) / max(n, 1)
    n_frac = sum(1 for ch in s if ch not in "ACGT") / max(n, 1)
    return {"length": n, "gc": gc, "ambiguous_fraction": n_frac,
            "coding_fraction": coding_fraction(s)}