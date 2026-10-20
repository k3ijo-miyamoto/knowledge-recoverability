# Reproducibility — Synthetic Controls and Bounded Diagnostics

This repository provides curated implementations, frozen synthetic fixtures,
and selected saved results for three diagnostic controls associated with
the working preprint v0.6.1.

## Included studies

- X0-A: 12 predetermined synthetic fixture families, with transition
  and warrant-scoring tests.
- X0-B: 8 probability atoms, 3 policies, and 24 exact world-policy
  evaluations.
- Audit Allocation Pilot: 2 fixed laws, 16 atoms, and 4 policies,
  yielding 128 deterministically scored rows.

The 128 rows are not independent empirical trials. These controls
do not establish the MH-2 theorem's correctness, real-world safety,
or independent semantic W1 verification.

## Reproduction limits

The original tests depend on Linux /proc, a one-process/thread setting,
a 1 GiB address-space limit, disabled Python bytecode, and frozen
fixture records in their original artifact paths.

The exported source and fixtures have not been independently rerun
as a standalone public package. Previous PASS results describe
historical bounded executions, not new tests of this release.

The evidence/ directory contains selected frozen hashes and compact
results, not a complete historical execution archive.

## C1 and P2 — curated diagnostic source release

Selected C1/P2 code, historical small results, and test source are
included. See C1_P2_SOURCE_INVENTORY_SHA256.txt for 12 file hashes.

### C1: installed state versus retained runtime

One prior isolated observation reported the same installed urllib3 2.0.2
state for two post-update conditions. The retained process reported
loaded version 2.0.0; the restarted process reported 2.0.2.

A separate locally authored gzip streaming check recorded 1,024 of
262,144 expected bytes under urllib3 2.0.0 and all 262,144 bytes
under 2.0.2. This check was not executed inside the retained old
worker. It is not general software-safety certification.

### P2: generated output versus client-received response

One scripted two-world, two-query local instrument produced four
recorded responses. Pre-egress semantic records matched by query.
The q1 received outputs matched; the q2 outputs differed because
STALE_EGRESS deliberately substituted an old answer after generation.

The saved scores establish only a bounded source-relative comparison
against a frozen PyPI issuer declaration (P4a).
Independent semantic warrant W1/P4b, real-world all-route coverage,
and a general zero-unsafe-probability guarantee are not established.

### Standalone reproduction limitations

The original C1 and P2 tests refer to historical artifact paths,
including full pip inspect and process-lifecycle receipts, a frozen
third-party PyPI metadata snapshot, and byte-exact client/gateway
receipts. Those original records have NOT been included in this
curated public subset. Thus the published C1/P2 tests are provided
for inspection, but are not a self-contained executable replay suite.

No C1/P2 experiment or test was rerun for this publication.
Some source programs perform package downloads or controlled process
execution if invoked; publication is not an instruction or permission
to run those programs.

## Excluded material

Original C1/P2 runtime receipts, full third-party metadata snapshots,
environment-dependent records, and private execution logs remain excluded. No private Git history, handovers,
Run Tickets, ADRs, internal reports, or operational logs are included.

## Licenses

Original author-owned software: MIT License (LICENSE-MIT).
Original author-owned manuscript: CC BY 4.0 (LICENSE.md).
Third-party materials retain their own rights.

See SOURCE_INVENTORY_SHA256.txt for checksums of published
synthetic-control files.
