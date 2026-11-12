"""Sequence features and homology grouping."""
from itertools import product

import numpy as np
from scipy import sparse

LUT = np.full(256, -1, dtype=np.int8)
for _i, _c in enumerate("ACGT"):
    LUT[ord(_c)] = _i


def encode(seq):
    return LUT[np.frombuffer(seq.encode(), dtype=np.uint8)]


def revcomp(codes):
    return np.where(codes < 0, -1, 3 - codes)[::-1]


def kmer_idx(codes, k):
    """Integer index of every valid k-mer (windows containing N are dropped)."""
    n = len(codes) - k + 1
    if n <= 0:
        return np.array([], dtype=np.int64)
    idx = np.zeros(n, dtype=np.int64)
    bad = np.zeros(n, dtype=bool)
    for j in range(k):
        c = codes[j:j + n].astype(np.int64)
        bad |= c < 0
        idx = idx * 4 + np.where(c < 0, 0, c)
    return idx[~bad]


def kmer_freq(seqs, k=4):
    """Strand-symmetric k-mer frequency matrix (n_genomes x 4**k)."""
    X = np.zeros((len(seqs), 4 ** k))
    for i, s in enumerate(seqs):
        c = encode(s)
        counts = (np.bincount(kmer_idx(c, k), minlength=4 ** k)
                  + np.bincount(kmer_idx(revcomp(c), k), minlength=4 ** k))
        X[i] = counts / max(counts.sum(), 1)
    return X


def gc_content(seqs):
    return np.array([(s.count("G") + s.count("C")) / max(len(s), 1) for s in seqs])


def build_features(seqs, k=4):
    """k-mer frequencies + GC content. Returns (X, feature_names)."""
    X = np.hstack([kmer_freq(seqs, k), gc_content(seqs)[:, None]])
    names = ["".join(p) for p in product("ACGT", repeat=k)] + ["GC"]
    return X, names


def jaccard_dist(seqs, k=10):
    """Pairwise Jaccard distance between 10-mer sets (both strands).

    Used ONLY to group related phages so they never straddle the train/test boundary.
    """
    rows, cols = [], []
    for i, s in enumerate(seqs):
        c = encode(s)
        u = np.unique(np.concatenate([kmer_idx(c, k), kmer_idx(revcomp(c), k)]))
        rows.append(np.full(len(u), i))
        cols.append(u)
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    M = sparse.csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)),
                          shape=(len(seqs), 4 ** k))
    inter = (M @ M.T).toarray()
    sizes = np.diag(inter)
    union = sizes[:, None] + sizes[None, :] - inter
    return 1.0 - inter / np.maximum(union, 1)


def cluster_groups(seqs, threshold=0.8):
    """Average-linkage clustering on Jaccard distance -> homology group id per genome."""
    from sklearn.cluster import AgglomerativeClustering

    D = jaccard_dist(seqs)
    return AgglomerativeClustering(n_clusters=None, metric="precomputed", linkage="average",
                                   distance_threshold=threshold).fit_predict(D)
