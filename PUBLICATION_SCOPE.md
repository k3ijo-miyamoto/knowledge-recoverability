# Public release boundary and checklist

This repository is a **curated publication surface** for the working preprint by Yukitake Miyamoto. It is deliberately separate from the private research repository `k3ijo-miyamoto/AssuredKnowledgeEvolution`.

## What may appear here

- Author-approved, rights-reviewed **final manuscript PDF** (after validating its exact SHA-256 and readable pages).
- The corresponding public-facing explanatory README, citation metadata and manuscript copyright/license notice.
- Supplementary code, fixtures or evidence **only after** a specific public-scope review (separate rights and software licensing, reproducibility and privacy screening, checksums and full source attribution).

## What must not be copied automatically

- The private research repository's Git history, branches, issue discussions or private AGENTS/ADR files.
- Internal `reports/`, `artifacts/`, experimental scratch files, logs, Git SHA/provenance matrices or unreviewed code.
- Customer/employer data, credentials, personal identifiers, private evidence sources or third-party copyrighted PDFs.
- Material whose permission, ownership or third-party license status has not been assessed.

## Current state

The selected paper candidate is **v0.6.1**. Its 19-page XeLaTeX PDF passed an internal *layout* review, with a minor nonblocking page-break imperfection; independent proof checking, historical novelty verification, data/code reproducibility and third-party/software rights and independently certified proof remain separate matters. The author approved the exact PDF for public GitHub release.

The author-approved [v0.6.1 manuscript PDF](paper/knowledge_recoverability_v0.6.1.pdf) has been publicly released in this repository; its SHA-256 is `053b228058438412c36f9e51022cabd7f7f41652afe57b726feca04a49394d06`. The corresponding Zenodo DOI is **not assigned**. A curated synthetic code, fixture, and compact-results subset is included, subject to the reproducibility limits in REPRODUCIBILITY.md. Other research evidence remains private. In particular, manuscript identifiers `[S0]` through `[S20]` are *private evidence-role identifiers*, not public links.

## Curated C1/P2 release — 21 October 2026

The public supplement now includes seven C1/P2 source files, two
historical receipt-inspection test files, and three compact saved
result files. File SHA-256 values are listed in
C1_P2_SOURCE_INVENTORY_SHA256.txt.

These results do not constitute a complete independent replay package.
Original runtime receipts, full PyPI snapshots, process metadata,
historical execution logs, and private handovers are not published.
See REPRODUCIBILITY.md for the bounded scientific interpretation.

## Before publishing any additional artifact

1. Confirm author's explicit approval for release of that **exact** PDF/file and the rights (including any employer and third-party concerns).
2. Confirm the specific bytes with SHA-256, current byline, version, preprint status, CC BY 4.0 scope, citations and complete rendered math.
3. Make a fresh public-only commit, **not a repository mirror**, and inspect exactly the staged paths before pushing.
4. Once actually released, update `README.md`, `CITATION.cff`, and this status to include only authentic persistent links and identifiers.
5. Register at Zenodo only following a separate explicit submission authorization. Do not invent or preannounce a DOI.

The absence of open evidence does not weaken the obligation to communicate limitations; it means the PDF alone is not a complete end-to-end replication package.
