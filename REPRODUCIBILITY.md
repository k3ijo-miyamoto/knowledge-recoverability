# Reproducibility — Finite Synthetic Controls

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

## Excluded material

C1/P2 instrumentation and its environment-dependent records are
reserved for separate review. No private Git history, handovers,
Run Tickets, ADRs, internal reports, or operational logs are included.

## Licenses

Original author-owned software: MIT License (LICENSE-MIT).
Original author-owned manuscript: CC BY 4.0 (LICENSE.md).
Third-party materials retain their own rights.

See SOURCE_INVENTORY_SHA256.txt for checksums of published
synthetic-control files.
