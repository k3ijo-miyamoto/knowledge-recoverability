# Knowledge Recoverability

**Recoverability after Knowledge Invalidation: Contingent Safety Budgets and the Limits of Observable Evidence**  
Yukitake Miyamoto · Independent Researcher, Japan

This is the curated **public-facing repository** for a research working preprint on safe, warranted recovery after knowledge invalidation. The editorial manuscript candidate is **v0.6.1 (20 October 2026)**. It has **not** undergone peer review or independent formal mathematical certification.

## Research question

When obsolete knowledge may still be served, and the validity of staged replacements is uncertain, how many paid checks and quarantines are required to obtain *positive, warranted recovery* while guaranteeing safe fallback on every allowed terminal branch?

A deliberately restricted finite two-identity model considers two old potentially stale versions and two staged successors, an exactly known full-support joint validity law, perfectly revealing unit-cost checks, individually available unit-cost quarantine, terminal-only publication, and zero unsafe terminal probability.

With hard worst-path check-plus-quarantine budget `K`, the model's expected warranted publication optimum is:

- `K < 2`: no safe policy is feasible;
- `K = 2`: safe abstention is feasible, with `V_2 = 0`;
- `K = 3`: `V_3 = max(u, v) + j`;
- `K >= 4`: `V_K = u + v`.

Here `u` and `v` are witness-validity marginals and `j` is their joint success probability. These results are **limited to the paper's explicitly stated model**. Classical first-failure reward sequencing has a matching independent-success special case; no novel general planning algorithm or established theorem-level historical priority is claimed.

## Publication and availability

| Material | Current public status |
| --- | --- |
| Manuscript v0.6.1 | **Released** — [v0.6.1 manuscript PDF](paper/knowledge_recoverability_v0.6.1.pdf) (19 pages, CC BY 4.0) |
| Zenodo DOI | **Not assigned** |
| Research source code, fixed fixtures, run receipts and raw logs | **Not publicly released** |
| Independent W1 semantic-verification service or production safety certificate | **Not established** |

The manuscript documents the core mathematics and a set of bounded synthetic and software diagnostic controls. Control observations are not demonstrations of real-world all-route safety, and counts of deterministic rows are not independent empirical samples.

This public repository is **not a mirror** of the private research workspace. Private research discussions, historical Git commits, internal reports, and unreviewed artifacts are intentionally excluded. Source labels such as `[S0]–[S20]` describe private evidence roles and must not be interpreted as public download links.

**PDF SHA-256:** `053b228058438412c36f9e51022cabd7f7f41652afe57b726feca04a49394d06`. No Zenodo DOI has been assigned.

## Citation and licensing

Citation metadata are in [CITATION.cff](CITATION.cff); a DOI will be supplied only after a real public deposit. The original author-owned manuscript text and equations have the author's **CC BY 4.0** licensing approval; see [LICENSE.md](LICENSE.md) for scope. This does not grant rights to third-party content, independent software, or private repository material.

AI tools assisted parts of literature comparison, mathematical derivation and checking, research instrumentation, and manuscript drafting. The author directs the study and remains responsible for its claims. Independent scholarly review and the historical theorem-priority assessment remain open.

See [PUBLICATION_SCOPE.md](PUBLICATION_SCOPE.md) for the public/private boundary and release checklist.
