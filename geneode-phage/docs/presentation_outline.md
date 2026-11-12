# Presentation outline (4–5 slides, about 5 minutes)

**Style:** deep space navy background with bioluminescent teal accents, to match the GENEODE deck.

## Slide 1: Problem
- Antibiotic resistance is rising; phage therapy needs the right phage for the right bacterium.
- Most sequenced phages have no tested host. Can the genome tell us?
- One line connecting to GENEODE: this is the first AI module of the platform.

## Slide 2: Approach
- Data: complete phage genomes from NCBI, 6 host genera.
- Features: 4-mer composition + GC (phages adapt their composition to their host).
- Models: logistic regression, random forest, compared with baselines.

## Slide 3: Validation (the strongest slide)
- Figure: `results/fig1_validation_comparison.png`
- Message: random split inflates the score because near-identical phages sit on both sides;
  the homology-aware split gives the honest number; shuffled labels fall to chance.

## Slide 4: What the model learned
- Figure: `results/fig2_confusion_matrix.png` (and `fig3_feature_importance.png` if space)
- Message: errors are between related hosts, which is biologically sensible.

## Slide 5: Limits and next steps
- Weak labels, genus level only, composition only.
- Roadmap: protein-level features and Evo 2 embeddings, species level, integration into GENEODE.

## 60-second pitch
"Phage therapy needs fast host identification. I trained a small model that predicts a phage's
host genus from its genome and, more importantly, validated it properly: I grouped related
genomes so the model is never tested on close relatives of its training data, and I included
a shuffled-label control. The honest score is X, versus Y with a naive split, which shows how
easily such results are inflated. This becomes the phage module in GENEODE."

## Likely questions and answers

| Question | Answer |
|---|---|
| Why not just BLAST? | BLAST needs a close relative already in the database; composition generalises to distant phages. A combined approach is the roadmap. |
| How do you know it isn't memorising? | Cluster-grouped CV and the shuffled-label control. |
| Why such a small dataset? | Time-boxed proof of concept; the pipeline scales to all complete genomes. |
| Are the labels reliable? | They come from NCBI naming; this is a stated limitation, and curated host-range sets are the next step. |
| Why is accuracy lower than papers report? | Many published numbers use random splits; the leaky bar on slide 3 shows what that gives. |
| What would improve it? | Gene content and receptor-binding proteins, Evo 2 embeddings, more genera. |
