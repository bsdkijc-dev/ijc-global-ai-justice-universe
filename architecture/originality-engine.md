# Originality & Semantic Deduplication Engine

## 1. Purpose
Prevent combinatorial bloat and near-duplicate program specifications when sampling from the $10^{12}+$ design space.

## 2. Three-Tier Screening Pipeline
1. **Exact Coordinate & Hash Deduplication**: Checks `SHA-256` of the 12-tuple `(d1, ..., d12)` and canonical `program_id`. Guarantees zero exact duplicates.
2. **Lexical / Structural Overlap (Token Jaccard)**: Computes pairwise Jaccard similarity across normalized program title + rationale + workflow tokens.
3. **TF-IDF Cosine Similarity**: Computes vector-space cosine similarity across generated program descriptions using pure-Python / NumPy TF-IDF (zero external APIs). Pairs exceeding threshold $\tau = 0.85$ are flagged for review or suppressed; each program receives an `originality_score` in $[0.0, 1.0]$ equal to $1.0 - \max_{j \neq i} \text{sim}(i, j)$.
