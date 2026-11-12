"""Data acquisition and loading (NCBI nuccore -> data/<Genus>.fasta)."""
import random
import time
from pathlib import Path


def download(genera, per_genus, email, data_dir, seed=0):
    """Fetch a random sample of complete phage genomes per host genus from NCBI.

    Weak label: the genus named in the NCBI organism name ("Escherichia phage T4").
    """
    from Bio import Entrez

    Entrez.email = email
    data_dir = Path(data_dir)
    data_dir.mkdir(exist_ok=True)
    rng = random.Random(seed)
    for g in genera:
        f = data_dir / f"{g}.fasta"
        if f.exists() and f.stat().st_size > 0:
            print(f"[download] {g}: cached")
            continue
        # Try several query formats; the first one that returns hits wins.
        terms = [
            f'"{g} phage"[Title] AND "complete genome"[Title] AND 20000:400000[SLEN]',
            f'{g}[Title] AND (phage[Title] OR virus[Title]) AND "complete genome"[Title] '
            f'AND 20000:400000[SLEN]',
            f'{g}[Title] AND phage[Title] AND complete[Title] AND genome[Title]',
            f'{g} AND bacteriophage AND complete genome AND 20000:400000[SLEN]',
            f'{g} phage complete genome',
        ]
        ids = []
        for term in terms:
            for _ in range(3):
                try:
                    res = Entrez.read(Entrez.esearch(db="nuccore", term=term, retmax=2000))
                    ids = res["IdList"]
                    break
                except Exception as e:
                    print(f"  search retry ({e})")
                    time.sleep(2)
            if ids:
                print(f"  query used: {term}  ->  {res.get('Count', '?')} hits")
                break
        if not ids:
            print(f"[download] {g}: no results for any query, skipping")
            continue
        rng.shuffle(ids)  # random sample avoids ordering bias
        ids = ids[:per_genus]
        print(f"[download] {g}: {len(ids)} genomes")
        with open(f, "w") as out:
            for i in range(0, len(ids), 40):
                batch = ids[i:i + 40]
                for _ in range(3):
                    try:
                        h = Entrez.efetch(db="nuccore", id=",".join(batch),
                                          rettype="fasta", retmode="text")
                        out.write(h.read())
                        break
                    except Exception as e:
                        print(f"  fetch retry ({e})")
                        time.sleep(2)
                time.sleep(0.4)


def read_fasta(path):
    name, seq = None, []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(">"):
                if name:
                    yield name, "".join(seq).upper()
                name, seq = line[1:], []
            elif line:
                seq.append(line)
    if name:
        yield name, "".join(seq).upper()


def load_dataset(genera, data_dir, min_len=20000):
    """Return (ids, labels, seqs). A genome is kept only if its header names the genus."""
    import numpy as np

    data_dir = Path(data_dir)
    ids, labels, seqs = [], [], []
    for g in genera:
        f = data_dir / f"{g}.fasta"
        if not f.exists():
            print(f"[load] missing {f}")
            continue
        n = 0
        for header, seq in read_fasta(f):
            if g.lower() not in header.lower() or len(seq) < min_len:
                continue
            ids.append(header.split()[0])
            labels.append(g)
            seqs.append(seq)
            n += 1
        print(f"[load] {g}: {n} genomes")
    return ids, np.array(labels), seqs