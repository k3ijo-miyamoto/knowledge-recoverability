---
title: "Recoverability after Knowledge Invalidation: Contingent Safety Budgets and the Limits of Observable Evidence"
author: "Yukitake Miyamoto"
date: "20 October 2026"
lang: en-US
header-includes:
  - \usepackage{xurl}
  - \usepackage{seqsplit}
  - \usepackage{needspace}
  - \setlength{\emergencystretch}{3em}
---

*Independent Researcher, Japan.*

*Working preprint · Version 0.6.1 · Not peer reviewed.*

© 2026 Yukitake Miyamoto. The author's original manuscript material is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/); this does not relicense third-party works or separate software.

## Abstract

Knowledge invalidation creates a contingent recovery problem: a staged successor may fail verification while its potentially stale predecessor remains servable and must still be retired or isolated. We characterize the attainable recovery in a finite two-identity model with two pre-staged successors, a known full-support joint law of witness validity, exact unit-cost checks, individual unit-cost quarantine, terminal-only publication, and zero terminal unsafe risk. Under a **hard worst-path budget** \(K\) for checks plus quarantines, no safe policy is feasible for \(K<2\), safe empty termination attains \(V_2=0\), and the maximum expected count of warranted new publications is \(V_3=\max(u,v)+j\) at \(K=3\) and \(V_K=u+v\) for \(K\ge4\), where \(u,v\) are validity marginals and \(j\) is their joint success probability.

A complete four-initial-action proof identifies which adaptive checks and fallback quarantines attain these bounds, including feasible quarantine-first continuations. The formulation makes explicit **how much worst-case fallback capacity must remain available when verification can fail**, and how dependence between warrants changes expected recovery. Its two-task independent-success specialization agrees in optimal expected reward with classical first-failure sequencing (Garey, 1973); the recovery contract additionally states version-specific isolation and the hard fallback budget rather than claiming a new general task-ordering algorithm. Separate one-old-hazard results (T1, T3) and a pre-invalidation record-sufficiency baseline (G9) provide comparison points under different assumptions.

Diagnostic controls from finite synthetic worlds and isolated software processes distinguish visible source, installed, loaded, generated, and delivered states. They identify evidentiary gaps that matter when interpreting the idealized recovery model in operational systems. This paper offers a tractable exact characterization and an evidence-aware interpretation; independent semantic warrants, all-route serving guarantees, and full lifecycle costs are outside the verified evidence.

**Keywords:** knowledge invalidation; safe recovery; adaptive verification; quarantine; provenance; witness dependence; observability; auditing.

## 1. Introduction

After knowledge invalidation, a system can face three obligations simultaneously: an old cached or derived artifact may remain servable **when the observed withdrawal scope is incomplete**; a staged successor may have uncertain evidence validity; and a verification budget may be insufficient to both inspect that successor and quarantine remaining old hazards **if inspection fails**. The challenge is not simply whether a new version can be written, but whether positive, warranted recovery and safe fallback can both be achieved on every admissible terminal branch. This is a motivating restricted scenario, **not** a new universal "trilemma" theorem.

Versioned knowledge bases, agent memories and tool-derived artifacts can persist after their supporting source is invalidated. An updated inventory is not a proof that every running process or cached answer has changed. Conversely, a genuinely complete barrier for every affected object in a declared service boundary has stronger implications than the **incomplete logged influence graph** considered in our residual-hazard models. Cascade withdrawal and validated repair are already direct subjects of MemoRepair [R1]; this manuscript does not claim that their introduction is new.

Our focus is the **post-invalidation, contingent resource constraint**. After an invalidation is reported, a logged withdrawal barrier may leave some old artifacts servable because the visible lineage is incomplete. Successor versions may be staged, yet their named warrants remain uncertain and must be checked. A valid successor can replace its old identity; otherwise the unsafe old version may require quarantine. A policy that commits its limited verification budget to positive branches must still have a legal way to terminate safely after a witness check fails. This makes **worst-path fallback reserve** important, as opposed to only optimizing an average verification bill.

Positive recovery must be distinguished from defensive deletion. A system may quarantine everything and achieve a locally safe empty serving set, but this yields no newly warranted knowledge. Similarly, a check reporting PASS may not imply actual semantic validity if the check is fallible. We therefore distinguish *true warrant validity*, *observable check messages*, *service state* and *observed client output*, rather than using a single undifferentiated notion of “knowledge updated.”

We develop three **separate** small mathematical subclasses with different residual-old-state structures. Their action spaces isolate paid checks and quarantine after independently costed staging, and their \(\delta=0\) condition applies to the **terminal** unsafe event, not continuously to every instant of deployment. The analytical values are interpretable exact special cases; generic Bellman planning can represent them, but that representability neither proves an independent historical discovery nor by itself removes the explanatory value of a closed form. Classical first-failure inspection and risk-constrained decision literature [R6–R9] supplies particularly relevant competing frameworks.

A second theme is the **evidentiary gap** between ideal witness-check assumptions and actual observable software. Existing one-consumer measurements and one local deterministic answer-gateway assay show why installed, loaded, generated and finally served states must not be conflated. We use these as bounded controls rather than examples of a production RAG recovery guarantee. We also identify the unverified origin/semantic/rights components of a genuinely independent W1 warrant and the currently unmeasured expense of producing and renewing it.

Sections 2–3 state the formal question and the three finite frontiers, with a distinct pre-event memory baseline. Section 4 gives the exact provenance and units of completed synthetic and software checks. Section 5 discusses the relation to earlier literature and operational evidence. Section 6 states limitations and next verification obligations. Appendix A contains further proof and source-traceability notes.

### Analytical contributions and diagnostic controls

The principal contribution is an **explicit safe-recovery frontier** for the MH-2 action contract. The closed form distinguishes infeasible budgets, safe abstention, positive contingent recovery, and the budget required to recover every checked-valid successor in expectation. Its value comes from tying each achievable outcome to a feasible terminal old-version covering policy, not merely from writing an expected-reward expression.

The analysis also clarifies the role of witness dependence. Even with identical validity marginals \(u,v\), the attainable \(K=3\) recovery changes with joint validity \(j\). T1 and T3 address different one-old-hazard action spaces, while G9 concerns evidence retained **before** invalidation. They are useful contrasting results, not components of a proved unified theorem.

Finally, X0-A, X0-B and the audit-allocation pilot test stipulated transition and risk-accounting contracts; C1 and P2 identify concrete boundaries between installed, loaded, generated and client-received evidence. Section 4 treats these as **diagnostic controls** that make the model's operational assumptions visible. Their observed units and scope are reported exactly in Appendix C. The separate evidence-realizability proposal EBR-1 [S17] remains future work.

## 2. Research Question and Declared Semantics

### 2.1 Questions and observable boundaries

**RQ1 (mathematical):** With potentially stale old versions remaining after a logged invalidation barrier, how do hard contingent witness-check/quarantine budgets and dependent witness validity constrain nonempty, globally safe and warranted recovery?

**Supporting evidence-boundary question (not a separate proved research contribution):** Which observed store, runtime, generated and client-delivered records fail to warrant transfer of the exact-check theorem to operational safety, and what independent evidence would be needed?

**RQ1 is the single principal mathematical question.** The evidence-boundary question supplies narrowly scoped motivation and a list of assumptions not established by controls; the two do not form a jointly validated theorem.

### 2.2 Versioned serving and substantive safety

Let \(M_t\) contain servable versions, \(B_t\) barred versions, \(Q_t\) staged unpublished successors and \(P_t\) published new successors, within one declared logical system. Old historical influence edges and new active support edges are distinct. The real affected-old set may differ from the lineage reachable in the policy-visible log. These states and the “logged barrier B0” follow the existing *synthetic* X0-A contract [S5]. They are not observed properties of any deployed enterprise knowledge service.

At a reachable terminal history \(h_T\), define \(\mathrm{GlobalUnsafe}=1\) if some actually invalidated old version remains served, an unwarranted successor is published or another hazard is explicitly included by the model. The strict safety criterion in the mathematical subclasses is

\[
\Pr(\mathrm{GlobalUnsafe}=1\mid h_T)\le\delta=0
\]
for every reached positive-probability terminal history \(h_T\).

For the same terminal unsafe event \(U\) and finite set \(H_T\) of reached histories with positive probability, the law of total probability yields
\[
\Pr(U)=\sum_{h\in H_T}\Pr(h)\Pr(U\mid h).
\]
Because all summands are nonnegative, \(\Pr(U)=0\) **if and only if** every reached positive-probability terminal \(h\) has \(\Pr(U\mid h)=0\). Consequently, the **branchwise zero threshold is not a newly stronger safety quantifier** than terminal almost-sure safety for this same event. Quarantine determines whether that condition is *feasible* under \(K\), not why this probability identity holds. For \(\delta>0\), the per-history and aggregate risk constraints generally differ; neither terminal definition guarantees continuous safety during intermediate actions or across unobserved service routes. Randomized terminal decisions remain subject to the declared zero-risk event.

Let \(W\) count genuinely warranted newly published successors, rather than retained old valid items or safe empty publication. For the restricted legal policy class \(\Pi_K\), let

\[
V_K=\sup_{\pi\in\Pi_K,\ \pi\ {\rm terminally\ safe}}\mathbb E_\pi[W].
\]

Write **INFEASIBLE** if no safe policy exists (not \(V_K=0\)). Let \(K_{\min}(\gamma)\) be the smallest worst-path paid-operation budget permitting \(\mathbb E[W]\ge\gamma>0\).

The budget \(K\) counts **only the witness checks and quarantine operations named in a given theorem**. Staging, repair, barrier administration, replacement/publication, source adjudication, rights review and audit renewal are **not priced within those toy \(K\) units**. They would be additional expenses in a full operational cost statement.

### 2.3 Warrant validity versus observable reports

A genuine successor W1 warrant must be tied to a named, claim- and context-specific source, substantively support the successor, be independent **in origin** from the invalidated root under a justified provenance boundary, and permit the actual cited use. A readable `source_id`, a digest, or a validator's PASS response does not by itself prove these properties. Statistical dependence of two legitimately separately sourced witnesses' **validity errors** also differs from common **contaminated source origin**.

The exact-check theorems below stipulate legitimate origin/permission/correct successor content and allow the purchased check to reveal the true validity bit. **These are mathematical premises.** Neither the X0 synthetic scorer's sealed truth bits nor the later C1/P2 software recordings instantiate an independent field W1 producer.

### 2.4 Separate role for retained pre-event information

The fourth accepted mathematical foundation, G9, asks what usable evidence must be stored before an invalidation for a later bounded verification/repair decision. Its ideal encoder initially sees complete latent worlds and post-event checks can be perfect. This is a distinct baseline; without reconciling observation and budget semantics, it cannot be multiplied or substituted into the post-event results.

## 3. Restricted Analytical Results

The propositions below characterize **three distinct finite models under their stated assumptions**, with a separate G9 pre-event baseline. The corrected MH-2 proof is complete in Appendix A.5; a state-based Bellman rederivation [S15] supplies an internal consistency check. The assumptions, including exact witness checks and known full-support probabilities, determine the scope of the results. Their historical theorem-level priority is discussed in §5 rather than asserted from the closed forms alone.

### 3.1 MH-2 — Two-Hazard Contingent Safe-Recovery Frontier

After B0, old \(a^-\) and \(b^-\) remain servable and each may be stale with strictly positive posterior probability whenever still served. Witness checks do not reveal old-staleness truth. Correctly staged and legally supportable \(a^+\), \(b^+\) have distinct uncertain witness-validity bits \(E_a,E_b\) and a known full-support joint distribution. Let

\[
\begin{aligned}
u&=\Pr(E_a=1),\quad v=\Pr(E_b=1),\\
j&=\Pr(E_a=1,E_b=1),\\
\max(0,u+v-1)&<j<\min(u,v).
\end{aligned}
\]

Each witness may be perfectly checked once for cost one. Each old identity may be quarantined at cost one. Only a checked-valid successor may be published; its publication **at termination** atomically retires the same old identity, at zero further \(K\) cost. A check PASS or successful staging alone does **not** retire an old version.

**Proposition MH-2 (restricted full frontier [S1]).**

\[
\begin{array}{lll}
K=0,1 &: &\mathrm{INFEASIBLE},\\
K=2 &: &V_2=0,\\
K=3 &: &V_3=\max(u,v)+j,\\
K\ge4 &: &V_K=u+v .
\end{array}
\]

For a positive expected warranted recovery target \(\gamma\):

\[
K_{\min}(\gamma)=
\begin{cases}
3,&0<\gamma\le \max(u,v)+j,\\
4,&\max(u,v)+j<\gamma\le u+v,\\
\mathrm{INFEASIBLE},&\gamma>u+v.
\end{cases}
\]

Safe **empty** recovery is first feasible at \(K=2\); it is different from \(\gamma>0\).

**Proof summary; complete self-contained proof in Appendix A.5 [S18].** If \(m\) is the number of checked witnesses, \(F\) the number of failed checks, \(q\) old quarantines and \(s\) newly published checked-valid successors, safe termination requires \(q+s\ge2\) and \(m\ge s+F\), hence
\[
m+q\ge2+F.
\]
This rules out \(K<2\), and at \(K=2\) any purchased check admits a positive-probability FAIL path requiring more than the available budget; double quarantine achieves \(V_2=0\). For \(K=3\), the four legal first actions \(C_a,C_b,Q_a,Q_b\) have attainable conditional-start maxima \(u+j,\ v+j,\ \max(u,v+j),\ \max(v,u+j)\), respectively, so their maximum is \(\max(u,v)+j\). Notably a **quarantine-first** policy \(Q_a,C_b\), then \(C_a\) if \(E_b\) passes, is legal and earns \(v+j\); the earlier discarded upper-bound proof overlooked it. For \(K\ge4\), inspect both and quarantine the old identity of each failed candidate, publishing every checked-valid successor at terminal, attaining \(u+v\). Appendix A.5 checks every branch for safety and admissibility.

**First-failure reward interpretation.** In the attaining \(C_a\)-first tree, the new-publication reward is \(\mathbf 1_{E_a=1}+\mathbf 1_{E_a=E_b=1}\), with expectation \(u+j\). The \(C_b\)-first tree gives \(v+j\). Together with the full four-first-action bound, this proves an **exact optimal-value equivalence to a specially constructed two-task stop-on-first-failure positive-reward sequencing problem**—not equivalence to the exact published result of Garey [R6] or Duffuaa–Pollock [R7], whose original objectives and model rights are not yet matched theorem-to-theorem [S18].

**Distinct \(n\)-hazard accounting [S1].** Under individually quarantineable \(n\) residual old hazards and positive probability of the all-witness-FAIL assignment, a necessary paid path cost is \(m+q\ge n+F\), and the least worst-path budget for **some sufficiently small positive** recovery is \(n+1\). This is *not* an arbitrary-\(\gamma\) n-candidate optimum. A separate later note [S16] proposes a first-failure ordering expression at \(K=n+1\) only after strengthening to strict full support for **every** joint witness assignment. Its standalone novelty is threatened by established dependent-inspection and first-failure sequencing [R6,R7]; its proof is not independently certified or adopted as a theorem of this manuscript. The n-extension is deliberately excluded from the paper's confirmed principal propositions.

For a numerical **formula illustration** with \(u=v=0.9,j=0.81\), the three MH-2 values are \(0,1.71,1.8\) at \(K=2,3,4\). The \(\gamma=1.75\) goal requires \(K=4\). These numbers are not fitted data or experimental observations.

### 3.2 T1 — One-Hazard Joint-Witness Budget Frontier

A **different subclass** retains only old \(a^-\), still possibly stale after B0 with hidden \(H\) satisfying \(\Pr(H=1)=p\in(0,1)\). \(H\) is not revealed by witness checks. Publishing \(a^+\) safely replaces \(a^-\), but publishing \(b^+\) does not. Both successor contents and origin-access requirements are stipulated valid; their distinct witness-validity records have full-support joint distribution specified by \(u,v,j\). Perfect checks and the single \(a^-\) quarantine each cost one.

**Proposition T1 (restricted [S2]).**

\[
K=0:\mathrm{INFEASIBLE},\quad V_1=0,\quad
V_2=\max(u+j,v),\quad V_K=u+v\ \text{for }K\ge3.
\]

A first check of \(E_a\), followed (on PASS) by check of \(E_b\), can publish the rescue successor and then a second checked-valid successor; on initial FAIL the remaining unit quarantines \(a^-\). Its gain is \(u+j\). Alternatively quarantining the old item followed by checking \(E_b\) yields \(v\). The two types exhaust the best feasible first-action strategies at budget two. Quarantine plus two exact checks fits \(K=3\), attaining \(u+v\).

**Fixed marginals, different budgets.** At \(u=v=0.9,\delta=0,\gamma=1.75\), if \(j=0.81\), then \(V_2=1.71<\gamma\) and \(K_{\min}=3\); with \(j=0.88\), the same declared graph, actions and marginals give \(V_2=1.78\ge\gamma\) and \(K_{\min}=2\). Both distributions have full support. Dependence affects this restricted budget frontier; these values were derived analytically, **not observed** in real reviewer populations.

**Fallible-check strict-zero boundary [S2].** If a bounded number of imperfect reports always leaves each candidate's invalid-witness state at positive posterior probability on every reached history, \(\delta=0\) cannot permit nonempty warrant-certified publication. Safe quarantine and abstention may remain possible. This does not apply to \(\delta>0\), an exact validator, or a truly zero-false-positive observation.

\Needspace{15\baselineskip}

### 3.3 T3 — Fixed-Budget Multi-Candidate Recovery Frontier

Another distinct model has one unsafe residual old identity \(x_0^-\) and \(n\ge2\) staged successors; only checked-valid \(x_0^+\) publication can retire \(x_0^-\) without quarantine. Witness-validity bits \((E_0,\ldots,E_{n-1})\) have full-support arbitrary joint law, and each purchased exact check and the one permitted quarantine costs one. Under terminal \(\delta=0\), budget \(K=2\), let \(p_i=\Pr(E_i=1)\), \(j_{0i}=\Pr(E_0=1,E_i=1)\) for \(i>0\).

**Proposition T3 (restricted [S3]).**

\[
V_2=\max\Big\{\max_{1\le i<n}p_i,\quad
p_0+\max_{1\le i<n}j_{0i}\Big\}.
\]

A quarantine-first path can inspect one nonrescue candidate, yielding \(p_i\). Alternatively check rescue witness \(E_0\); on PASS inspect the best secondary candidate, and on FAIL quarantine the old identity, yielding \(p_0+j_{0i}\). The full-support failure branch rules out gaining an extra unchecked rescue through the other ordering at this budget. This is a **fixed-\(K=2\)** maximum requiring only \(O(n)\) comparisons *once* all \(p_i,j_{0i}\) values are supplied. It is not an \(O(n)\) solver for constructing those probabilities from an exponential joint table and not an optimality claim for larger \(K\).

### 3.4 G9 — Pre-Invalidation Record-Sufficiency Baseline

Let \(\Theta\) be a finite set of complete worlds, \(f\) a future invalidation event, and \(R_f(\theta)\) the nonempty correct positive terminal actions available in world \(\theta\). An **ideal** pre-event encoder sees the whole \(\theta\), stores a finite record, then a post-event decoder obtains at most budget \(B\) in *perfect* deterministic queries before choosing a valid action common to all remaining possible worlds. Define \(\operatorname{Good}_f(C,B)\) as whether a common safe future decision tree exists for all worlds in cell \(C\). Form a hypergraph \(\mathcal H_B\) whose hyperedges are inclusion-minimal sets of worlds failing that property for some future event. Its exact finite coding characterization is

\[
 m^*(B)=\left\lceil\log_2\chi_{\mathrm{weak}}(\mathcal H_B)\right\rceil.
\]

This is a **known-style compatibility-partition/weak-hypergraph-coloring reduction**, not a confirmed novel theorem. The broad RP-007 originality claim was explicitly **N0/STOP** [S4]. The ideal encoder can read hidden full world state, which an operational lawful archive often cannot; hence this G9 formula cannot be silently composed with the post-event stochastic results. G9 remains a separately retained basis for further claim-specific study.

## 4. Diagnostic Controls across Evidence and Serving Layers

A recovery policy relies on two different kinds of facts: which verification outcomes authorize a successor, and which old or new version can actually reach a consumer. The controls below were designed to **separate these evidentiary layers**. The finite-world suites check transition semantics and risk accounting against stipulated truth; C1 and P2 expose specific software observation gaps. Together they motivate the observability requirements that an operational successor of MH-2 would have to address. They are not trials estimating the MH-2 optimum.


**X0-A [S5,S6]**

**Observed unit:** 12 fixed synthetic fixture families; one bounded suite PASS

**What it establishes in its declared setting:** Version-transition and warrant-scoring conformance, including false PASS, hidden truth and safe abstention

**Interpretation boundary:** Stipulated synthetic truth; not real W1 or deployed retirement


**X0-B [S7]**

**Observed unit:** 8 synthetic atoms, 3 policies, 24 exact world-policy evaluations, 7 test groups

**What it establishes in its declared setting:** Visibility and conditional-risk arithmetic under a finite prior/validator model

**Interpretation boundary:** A different observation and action contract from MH-2


**Audit allocation [S8]**

**Observed unit:** 16 atoms × 2 laws × 4 policies = 128 **deterministically scored rows**, 7 tests

**What it establishes in its declared setting:** Conditional versus unconditional risk and audit-budget accounting with stipulated verifier errors

**Interpretation boundary:** 128 rows are not 128 independent trials; risk tolerance here is \(\delta=1/5\)


**C1 [S9,S10]**

**Observed unit:** One retained-versus-restarted `urllib3` process comparison; separate one-input fresh-process gzip check

**What it establishes in its declared setting:** Installed-package metadata does not identify every loaded process version within the tested boundary

**Interpretation boundary:** One isolated consumer and a distinct local gzip observation


**P2 [S11,S12]**

**Observed unit:** Four scripted client-pipe deliveries across two fixed worlds

**What it establishes in its declared setting:** Identical pre-egress records can coexist with different delivered answers

**Interpretation boundary:** Scripted output modification; source-relative P4a rather than independent W1/P4b


The audit allocation control yielded conditional unsafe probability \(101/560\le1/5\) on relevant publishing histories and unconditional unsafe probability \(101/800>0\). These are exact values from its **separate imperfect-verifier model**. C1 independently distinguishes installed-versus-loaded version state and a fresh-process gzip output; the two are not one continuous causal trace. P2 isolates the final egress layer using scripted worlds. The controls therefore identify **where additional authenticated evidence would be required** to move from the finite decision model to a real service. Appendix C preserves the original measurements and study boundaries.

## 5. Related Work and Interpretation

**Cascade repair and retained-state exposure.** MemoRepair by Zhao et al. [R1, §§2.2–2.4] defines barrier-first withdrawal, candidate validation and predecessor-closed republication, and discusses hard repair-selection budgets as well as validation/provenance ablations. Its **Theorem 1** is a fixed-candidate, fixed-cost and fixed-λ *value-minus-cost selection* result reducible to one min-cut. The **restricted MH-2** problem instead purchases witness-truth observations sequentially, branches on PASS/FAIL and must reserve quarantine operations under a hard **worst-path check-plus-quarantine budget**, maximizing the expected count of **warranted newly published successors** while ensuring **terminal zero unsafe risk on every reached history**. This difference isolates the finite contingent verification/quarantine question addressed here; it does not imply that established repair or diagnosis theory cannot represent the same problem. MemoRepair's external benchmarks are not datasets used in this study.

**Classical sequencing as a baseline; knowledge recovery as the decision contract.** Classical first-failure reward sequencing provides a direct mathematical benchmark for the \(K=3\) expected-value calculation. The contribution of MH-2 is to specify and solve a **different operationally motivated finite decision contract**: two potentially stale servable identities must be covered at termination by same-identity warranted replacements or individually paid quarantines, even when a check fails, subject to one hard worst-path check-plus-quarantine budget. Its four-first-action proof shows both attainability and the fallback-reserve lower bound. These explicit obligations explain why a reward ordering alone is not a complete specification of this knowledge-recovery decision problem; they do not establish that a richer established planning framework could not encode it.


**Objective**

**MH-2:** Maximize expected checked-valid new publications under terminal safety

**Garey (1973) [R6]:** Optimize expected task cost/reward until first failure, respecting precedence

**Duffuaa–Pollock (1999) [R7]:** Minimize expected inspection cost for dependent characteristics


**Witness dependence**

**MH-2:** Known full-support joint law \(u,v,j\), allowing \(j\ne uv\)

**Garey (1973) [R6]:** In the no-precedence two-task specialization, independent successes yield \(j=uv\)

**Duffuaa–Pollock (1999) [R7]:** Dependent characteristic fitness is part of the original model


**Safety/resource contract**

**MH-2:** Mandatory same-identity old-version coverage by valid publication or paid quarantine; hard worst-path check-plus-quarantine \(K\)

**Garey (1973) [R6]:** No explicit old-version quarantine or such fallback \(K\) in the original task statement

**Duffuaa–Pollock (1999) [R7]:** A different cost objective; MH-2's old-serving replacement obligation is not specified in the matched comparison


**Demonstrated relation**

**MH-2:** Constructed correlated two-task first-failure reward model has the same **optimal expected value** at \(K=3\)

**Garey (1973) [R6]:** Exact special-case optimum agreement when \(j=uv\)

**Duffuaa–Pollock (1999) [R7]:** Shared dependent-inspection motivation, not an established same-objective reduction


Garey's full 20-page original article was examined in a preceding documented source review [S19,S20]. Printed pp.38–42 give the conditional predecessor-success assumptions, rewards via negative costs, first-failure reward examples, and Theorem 3.1's merit-ratio exchange condition. For no precedence, independent success and unit reward per success, order \(a,b\) earns \(u+uv\) and order \(b,a\) earns \(v+uv\). Their optimum \(\max(u,v)+uv\) agrees with MH-2 when \(j=uv\). By contrast, keeping \(u=0.9,v=0.8\) while changing the full-support joint probability from \(j=0.72\) to \(j=0.78\) changes MH-2's \(V_3\) from 1.62 to 1.68. The no-precedence independent Garey specialization does not distinguish these two laws from the same marginals. More general task representations or prior decision-theory results may still encode this contract; the comparison establishes **the scope of the direct classical match**, not absolute novelty.

Duffuaa–Pollock [R7] explicitly considers dependent inspection outcomes but minimizes expected inspection cost, whereas the MH-2 objective is expected warranted recovery under pathwise fallback and terminal safety. The difference matters for interpreting an ordering, yet by itself does not prove that no broader reduction is possible. Its full theorem equations were not independently rechecked in this revision; the distinction is limited to the verified original-source comparison.

**Classical task ordering and dependent inspection.** Garey [R6] studies tasks sequentially executed until first failure or completion, with expected-cost/reward optimization. Duffuaa and Pollock [R7] study inspecting **dependent characteristics**, joint validity distributions and dynamic-programming order selection. These are close predecessors of the proposed \(n\)-hazard first-failure ordering extension [S16]; a particular knowledge-repair interpretation does not establish that inspection ordering or higher-order joint probabilities are novel. Garey's previously inspected original pages and Duffuaa–Pollock's published/archived material support this overlap; a complete same-objective theorem-equivalence proof remains outstanding [S19,S20].

**Sequential information acquisition and active diagnosis.** Zong et al. [R2] study cost-optimal stochastic Boolean function evaluation with distributions over assignments and paid observations. Haar et al. [R3] analyze active diagnosis and memory-minimal controllers. These directly challenge the originality of generic adaptive checking, dependence-sensitive decision trees and minimum memory. Our finite equations may be special cases of broader known frameworks. The strict conditional terminal safety and nonempty warranted recovery objective must be matched precisely against their outcomes, including zero-risk branches and quarantine actions, before claiming a new algorithmic principle.

**Active diagnosis with explicit costs and rewards.** Haddad, Lefaucheux and Schwoon [R5, §3; Theorems 24–26, 33–34] analyze partial-observation fault diagnosis under worst-run cost and reward thresholds, with nondeterministic and probabilistic settings. This establishes that contingent diagnosis with severe cost/reward restrictions is existing theory. Their published target concerns *detection of faults* and absorbing faulty states, while MH-2 concerns *repair and publication of warranted successors* after invalidation; these different problem statements do **not** establish a theorem-level originality separation, since a richer diagnosis/planning model may represent the repair task.

**Risk-constrained POMDP and safe reachability.** Santana, Thiébaux and Williams [R8] formulate chance-constrained finite-horizon POMDP planning for expected performance with execution-risk bounds. Wang, Chaudhuri and Kavraki [R9] consider bounded policies with both safety and goal-reaching probabilities. These sources establish that uncertainty, probabilistic safety and positive utility/reachability are **not** newly combined here. Their risk may concern paths or accumulated execution; MH-2's explicit definition concerns the specified **terminal** old/new unsafe event. Identical theorem objectives and action rights have not been established.

**Belief-state decision models.** Ross et al. [R4] review POMDP planning. The state-based recurrence in [S15] realizes MH-2 as standard finite contingent planning; thus no new general planning algorithm is claimed. Yet a small exact expression for a particular residual-old-version model can be more interpretable than a black-box numeric policy value. Its originality cannot be inferred merely because the printed equation differs from one prior theorem.

**Pre-event memory and provenance.** G9's partition/weak-coloring identity intersects well-established functional compression and active-diagnosis concepts [R3,S4]. Its current broad claim was specifically stopped as novel in the recorded G9 audit [S4]. The empirical C1/P2 contrasts are also known-style observational equivalence controls: a same-version installed record cannot identify every running version, and identical generated text cannot determine every final delivered response. Their role is to diagnose **which layer is actually evidenced**, not to rename these phenomena new discoveries.

**Warrant production is a distinct engineering and scientific task.** The source/serving audit analyses [S13] distinguish genuine reference creation, provenance channel closure, independent semantic assessment, lawful and context-valid citation, route completeness, effective old retirement and fresh serving readbacks. Proof of a source digest or an issuer's documented release status is not proof of every successor claim's truth. A complete W1 producer and a matched end-to-end cost advantage have not been demonstrated. Operational readiness is therefore a separate axis from the finite frontiers in Section 3.

## 6. Limitations and Conditions for a Submission-Ready Study

**Model restrictions.** The MH-2, T1 and T3 expressions involve *different old-hazard configurations*. They assume perfect paid checks, known full-support witness distributions, correct and already staged successor content, valid independent source origin, terminal publication with same-identity retirement, and \(\delta=0\) at reached terminal histories. Budget \(K\) excludes substantial real staging/repair, legal adjudication and evidence upkeep. No generalized algorithm, arbitrary-horizon optimality, robust unknown-model guarantee, fully fallible-check theorem, integrated pre/post-event memory frontier or n-hazard optimal \(\gamma\)-frontier is shown.

**Proof status.** Appendix A.5 provides the corrected four-first-action argument, including the previously omitted quarantine-first continuation; [S15] supplies an internal Bellman rederivation. An independent human or formal proof assessment has not yet been completed. The derivation process and use of AI tools are disclosed in the Author Contributions and AI-Assistance Declaration.

**Theory–controls relationship.** The completed finite-world and software controls diagnose particular transition, observability, and risk-accounting assumptions. Their different models and units are documented in §4 and Appendix C; they do not serve as direct estimates of MH-2's optimal frontier.

**Data and experimental validity.** X0-A, X0-B and the Audit Allocation Pilot are deterministic fixtures/exact probability enumerations, **not independent real-world datasets** or sample-based estimates. C1 tests one disposable package environment and a single authored streaming input. P2 tests a deliberately constructed final-answer override across four local responses. No real LLM answer-population study, field failure incidence, causal treatment effect or representative cross-domain generalization is estimated. Repeating the same synthetic checks would not automatically resolve those limitations.

**Source truth, rights and serving coverage.** Frozen PyPI issuer metadata permits only source-relative P4a consistency claims. No independently qualified W1/P4b semantic assessor, complete historical source-channel closure, rights audit or authenticated all-route nonservability certificate is confirmed. C1/P2 do not jointly prove a continuous end-to-end W1-safe recovery chain. An exact past C1 raw byte archive was not retained, and independently authenticated historical runtime-output capture cannot be reconstructed from summaries alone.

**Risk estimands and prices.** The strict mathematical \(\delta=0\) guarantee is not the Audit Allocation Pilot's predeclared \(\delta=1/5\) conditional tolerance, nor a statistical confidence statement \(\alpha\), nor the unconditional event mass. No real auditor sensitivity calibration, reviewer money/time, storage and renewal price, privacy costs, human rights review or total cost superiority is measured. A shorter certificate or a computational SHA-256 assertion cannot be treated as zero-price ground truth.

**Interpretation and scholarly priority.** The exact MH-2 frontier gives a self-contained worked characterization of the **cost of safe fallback** in a small knowledge-invalidation model. Classical first-failure/dependent inspection [R6,R7], active diagnosis [R5] and risk-constrained POMDP results [R8,R9] establish substantial methodological precedent. The contribution claimed here is the explicit finite recovery-and-quarantine formulation, solution and evidence-boundary analysis; theorem-level historical priority for this particular combination has not been established. No new general planner, production-safety guarantee or empirical superiority claim is made.

**Separate future evidence-realizability question.** Existing EBR-1 [S17] is a scoped *research proposal*, not an experimental result, asking when a lawfully accessible, authenticated independent W1/P4b claim reference and versioned serving-route coverage can produce a warranted recovery certificate with actual full-lifecycle cost. No verified complete producer or price advantage has been demonstrated. This unresolved direction is intentionally not presented as a theorem of the current manuscript, nor as a subject beyond all established provenance/diagnosis research.

## Data and Code Availability

The finite-model definitions, exact results and Appendix A.5 proof are included in this manuscript. Detailed synthetic fixtures, selected source code, execution receipts and research reviews are held in the author's **private** research repository `k3ijo-miyamoto/AssuredKnowledgeEvolution` [S0]. The internal record identifiers [S0–S20] in Appendix B identify evidence roles but **do not provide public download access**; the complete file paths and frozen Git blob identifiers remain in the private research source of record. At this preparation stage, no rights-cleared public supplementary code, fixture set, independent W1 producer, or complete replication bundle is offered. Consequently readers can examine the analytical derivation and reported bounded observations, but cannot independently rerun every control from the PDF alone. If a separately authorized public bundle is released, its exact contents, licenses, checksums and persistent URL/DOI must be supplied in a revised availability statement.

## References (primary works and claim-scoped context)

**Evidence depth for added prior art:** [R6] original full 20-page paper inspected in the documented preceding review [S19,S20] (printed pp.38–42 and Theorem 3.1); the full text was **not reread directly for this v0.6.1 editorial update**. [R7] original research article/archived paper and prior internal §4 audit; [R8] official AAAI publication abstract; [R9] author-hosted original article and institutional bibliographic record. Full same-objective published-theorem identity to MH-2 has **not** been established.


[R1] Yang Zhao, Chengxiao Dai, Mengying Kou, and Yue Xiu (2026). *MemoRepair: Barrier-First Cascade Repair in Agentic Memory*. arXiv:2605.07242. \url{https://arxiv.org/html/2605.07242} . **Compared at original problem/model and section 2.4 theorem context; identical-result equivalence not certified.**

[R2] Xia Zong, Tuomo Lehtonen, and Jussi Rintanen (2026). *Cost-Optimal Decision Diagrams for Stochastic Boolean Function Evaluation*. arXiv:2606.24672. https://arxiv.org/html/2606.24672 . **Exact paid-Boolean-query setting overlaps; objective equivalence to these recovery frontiers remains unverified.**

[R3] Stefan Haar, Serge Haddad, Tarek Melliti, and Stefan Schwoon (2017). *Optimal Constructions for Active Diagnosis*. Journal of Computer and System Sciences 83, 101–120. https://doi.org/10.1016/j.jcss.2016.04.007 . **Active diagnoser complexity/memory reference, not asserted to contain exactly MH-2.**

[R4] Stéphane Ross, Joelle Pineau, Sébastien Paquet, and Brahim Chaib-draa (2008). *Online Planning Algorithms for POMDPs*. Journal of Artificial Intelligence Research 32, 663–704. https://pmc.ncbi.nlm.nih.gov/articles/PMC2748358/ . **General framework, not the same-objective recovery proof.**

[R5] Serge Haddad, Engel Lefaucheux, and Stefan Schwoon (2026). *Active Diagnosis with Costs and Rewards*. Proceedings of CONCUR 2026, LIPIcs 391, Article 37. https://doi.org/10.4230/LIPIcs.CONCUR.2026.37 . **Original §3 and Theorems 24–26/33–34 assessed for costs, rewards and partial observation; same-objective equivalence to MH-2 unverified.**

[R6] M. R. Garey (1973). *Optimal Task Sequencing with Precedence Constraints*. Discrete Mathematics 4(1), 37–56. https://doi.org/10.1016/0012-365X(73)90113-1 . **Original full paper examined in [S19,S20]: printed p.38 conditional predecessor independence; p.39 negative reward costs; pp.40–41 reward examples; p.42 Theorem 3.1. Special-case independent optimum matches MH-2 at \(j=uv\); complete theorem identity not shown.**

[R7] S. O. Duffuaa and S. M. Pollock (1999). *Optimal Sequencing of Inspection of Dependent Characteristics*. Journal of Optimization Theory and Applications 103(3), 557–565. https://doi.org/10.1023/A:1021731907266 . [Archived author manuscript](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/45190/10957_2004_Article_411720.pdf?sequence=1). **Jointly dependent characteristics and optimal inspection sequencing by DP; expected cost objective rather than MH-2's newly warranted publication count.**

[R8] Pedro Santana, Sylvie Thiébaux and Brian Williams (2016). RAO\*: An Algorithm for Chance-Constrained POMDP's. Proceedings of AAAI 30(1), 3308–3314. https://doi.org/10.1609/aaai.v30i1.10423 . **Finite-horizon risk-constrained expected-performance policies; underlying path-risk specification need not match MH-2 terminal risk.**

[R9] Yue Wang, Swarat Chaudhuri and Lydia E. Kavraki (2018). *Bounded Policy Synthesis for POMDPs with Safe-Reachability Objectives*. AAMAS 2018, 238–246. https://arxiv.org/abs/1801.09780 . **Safe reachability differs from simple terminal-only version hazard.**

**G9 background source note:** Functional-compression and graph-coloring antecedents discussed in [S4] remain internal contextual sources; no verified external bibliographic item is assigned to them here.

## Author Contributions and AI-Assistance Declaration

The author directed the research question, scope, assumptions to investigate, interpretation of the evidence, and decisions about the study and its release. AI tools assisted literature comparison, mathematical derivation and checking, code and diagnostic-instrument preparation, and manuscript drafting and editing. The author is responsible for the scientific claims and final text. These analyses have not undergone independent human mathematical peer review or formal proof certification.

© 2026 Yukitake Miyamoto. Original author-owned manuscript material is licensed under CC BY 4.0; the license does not automatically apply to cited third-party works, software or repository records.

## Appendix A. Additional Formal and Interpretive Checks

**A.1 Terminal versus continuous safety.** In MH-2 a candidate can remain staged and unserved while a check is performed; at termination a checked-valid successor may atomically retire the old identity. Thus a PASS response and a published successor are distinct state transitions. A policy can be safe at all reached terminals but still require an independent implementation invariant to guarantee that intermediate service never leaks old content.

**A.2 Minimum budget is not an expectation of cost.** A policy with \(K=3\) may use fewer than three steps along some histories, but must reserve the full worst-path budget to be admissible. The formulas give expected warranted successor **count** subject to that cap; they do not minimize expected verification expense in general.

**A.3 Dependence and provenance independence differ.** Two independently rooted source records may have statistically dependent validity errors. Conversely, several quoted reports from one contaminated root can be perfectly correlated without constituting independent corroboration. The joint success term \(j\) belongs to the probability law, whereas source-origin validity is a separate witness-legitimacy assumption.

**A.4 Known assumption-based impossibility.** With strict \(\delta=0\) and a finite sequence of noisy checks that never rules out witness invalidity on any reached observation history, a truly warranted **nonempty publication** cannot be certified by those messages alone. This conditional support fact must not be extrapolated to \(\delta>0\), calibrated confidence bounds, or tests with an actual exact source oracle.

### A.5 Complete mathematical proof of Proposition MH-2

Under §2 and §3.1's full-support and allowed-action premises, let \(S\) be the checked-PASS newly published successor identities and \(Q\) the quarantined *old* identities. A zero-risk terminal branch needs and, **within this ideal model**, can attain the covering condition \(S\cup Q=\{a,b\}\). Write \(m\) for checks, \(F\) for check-FAIL outcomes, \(s=|S|\) for published checked-valid successors and \(q\) for old quarantines. Then \(m\ge s+F\) and \(q+s\ge2\), giving the **necessary** covering bound \((A): m+q\ge2+F\). The two outcome bits \((E_a,E_b)\) have strictly positive probability in all four cells, so each unchecked witness retains a possible FAIL after any observed prefix; no old-staleness truth is disclosed by checks. Publication occurs **only at terminal time**, and a quarantined old identity does not prevent a later *new* successor publication if checked-valid. Staging and rights are stipulated and not charged to \(K\).

**Proof.**

**Case \(K<2\).** By (A) every safe terminal branch needs \(m+q\ge2\). Thus no admissible policy exists.

**Case \(K=2\).** Quarantining both old identities at cost 2 and publishing none is safe and gives W=0. Suppose any policy attempts a witness check. Let the *first* check be \(C_i\); regardless of any previous quarantine, by full support its FAIL branch has strictly positive probability. That terminal branch must satisfy \(m+q\ge2+F\ge3\), contradicting the pathwise K cap. Therefore no admissible policy purchases a check and the maximum recoverable W is 0. Randomizing does not help: any positive-probability choice of such an inadmissible path would violate the zero-risk/worst-budget class.

**Case \(K=3\).** A safe policy cannot terminate immediately because both old versions would remain unisolated. Its first paid action, after any zero-cost decision, must be one of **exactly four** choices: \(C_a,C_b,Q_a,Q_b\). Each has a safe policy that attains the optimum conditional on that first action; we derive a matching upper bound for each.

- **First \(C_a\):** With probability \(1-u>0\), FAIL requires quarantining both old versions with the two remaining units, giving W=0; another check after this FAIL would expose a positive-probability second failure and violate (A). On initial PASS (probability u), the policy can defer publishing \(a^+\) until terminal; one unit may purchase \(C_b\), and if its result is FAIL the remaining unit quarantines \(b^-\). If both checks PASS, publish both at termination. This tree is fully safe and has
  \[
  \mathbb E[W]=\Pr(E_a=1)+\Pr(E_a=E_b=1)=u+j.
  \]
  No continuation can yield more: after \(E_a=0\), safely covered old versions leave no budget for positive publication; after \(E_a=1\), \(a^+\) is at most one unit of W and any increment from \(b^+\) requires observing its own PASS. Hence the maximum conditioned on first \(C_a\) is \(u+j\).
- **First \(C_b\):** symmetric maximum \(v+j\).
- **First \(Q_a\):** Two units remain, and old \(b^-\) must still be covered. The second action can only meaningfully be \(Q_b,C_a,C_b\) (a repeated Q is prohibited/unhelpful).
  * If second is \(Q_b\), both old identities are already isolated. One remaining check may certify a single candidate, giving expected W at most \(\max(u,v)\), attainable.
  * If second is \(C_a\), last action **must** be \(Q_b\) on either result. Spending it on \(C_b\) instead admits a positive-probability FAIL of \(E_b\) with old \(b^-\) still served; no terminal publication can fix that. Thus expected W at most u, attainable by publishing \(a^+\) on its PASS.
  * If second is \(C_b\), then on FAIL the last action must be \(Q_b\), yielding W=0; on PASS \(b^+\) can retire \(b^-\) at terminal, and the last action can check \(E_a\). Since old \(a^-\) is already quarantined, all outcomes are safe. Publish \(b^+\) and, if the last check also passes, \(a^+\). The expected W is \(v+j\), attainable.
  Therefore the maximum among such policies is \(\max(u,v,v+j)=\max(u,v+j)\).
- **First \(Q_b\):** by symmetry the maximum is \(\max(v,u+j)\).

Taking the maximum over all four possible initial actions yields
\[
V_3=\max\{u+j,\ v+j,\ \max(u,v+j),\ \max(v,u+j)\}
=\max(u+j,v+j)=\max(u,v)+j.
\]
All branches in the described attaining policies obey the K cap and satisfy terminal covering. The **quarantine-first continuation \(Q_a\to C_b\to C_a\) on \(E_b=\mathrm{PASS}\)** is explicitly included; the historical first-quarantine upper-bound argument that ignored it is not relied upon.

A randomized policy is a distribution over these admissible finite action trees, conditional on the same information available at each history, and its expected value is a convex combination of deterministic-policy branch values. It cannot exceed the maximum already attained.

**Case \(K\ge4\).** The attainable upper bound is \(\mathbb E[W]\le\mathbb E[\mathbf 1_{E_a=1}+\mathbf 1_{E_b=1}]=u+v\), since publication requires genuine validity and each candidate appears only once. To attain it, buy both exact checks (2 units), quarantine the old identity of each checked-FAIL candidate (at most 2 further units), and at terminal publish every checked-PASS corresponding successor. Any branch costs at most 4, all served old versions are quarantined/retired and every new publication is valid. Thus \(V_K=u+v\) for all \(K\ge4\).

Finally, strict positivity of \(\Pr(10)\) and \(\Pr(01)\) gives \(\max(u,v)+j<u+v\). Combined with the K<2/K2/K3/K4 frontier this yields the asserted \(\gamma\)-threshold formula. **QED (within stated finite mathematical model).**

## Appendix B. Research Evidence Roles and Access Status

These identifiers describe research records retained in a **private** source-of-record repository. They are **not public download links, an open dataset, or a reproducibility package**. Full internal report filenames and Git blob hashes are preserved in the canonical private manuscript, not distributed in this print edition.

- **[S0]** Current program status v0.2 before manuscript
- **[S1]** Corrected MH-2; old erroneous intermediate bound retained separately
- **[S2]** T1 and fallible-observation zero-risk boundary
- **[S3]** T3: n-candidate \(K=2\) formula
- **[S4]** G9 finite baseline, original broad RP-007 N0/STOP
- **[S5]** Synthetic X0-A operational semantics, not a field model
- **[S6]** Approved attempt-02: **12 tests PASS** across 12 fixed fixture families; prior attempt-01 NO-GO preserved
- **[S7]** 8 atom, 24 world/policy, 7 test group bounded arithmetic PASS
- **[S8]** 128 exact rows, pilot PASS with positive unconditional unsafe mass
- **[S9]** C1 published run evidence, installed vs loaded observation
- **[S10]** C1 analysis separates version and fresh-process gzip tests
- **[S11]** Four physical client pipe deliveries in deterministic gateway
- **[S12]** Source-relative P4a, not independent W1/P4b
- **[S13]** Independent verifier **feasible in principle**, complete W1 source not verified
- **[S14]** Exact prior-result comparison with MemoRepair/SBFE/CONCUR 2026/Bayesian Probing; **REFINE**, not scientific N2 acceptance
- **[S15]** Bellman rederivation; δ=0 per-positive-history/global terminal equivalence, internal AI check only
- **[S16]** Stronger full-support \(n\)-old first-failure ordering proposal, not accepted proof; classical task ordering overlap
- **[S17]** One-source/one-route EBR-1 D-stage candidate; no independent validated W1 producer
- **[S18]** Complete four-first-action internal proof; exact **constructed** task-reward mapping; original-published theorem identity unresolved
- **[S19]** 20-page Garey original text reviewed in earlier turn; specialized equality and no full-theorem-identity conclusion
- **[S20]** Verbatim source-depth/budget/independence handover, current scope limitation

**Access:** The analytical proof is self-contained in Appendix A.5. The cited supporting reports, code, fixed fixtures, and run receipts are not publicly available through these source IDs. Independently rerunning all previously reported controls requires separately authorized, rights-cleared evidence. The controls and bibliographic priority have not been newly certified here.

## Appendix C. Detailed Previously Reported Controls (relocated without changing quantitative claims)

This appendix relocates the full historical text, observations, metrics and caveats of **v0.3 §4**; the section numbers alone are changed from 4.x to C.x. Nothing below is new experimental work or a direct MH-2 theorem verification.

### C.1 Evidence accounting and the “dataset” question

The experiments below are **not several independent external empirical datasets**. Most of the recorded rows are finite synthetic worlds, predetermined fixtures or exact analytical evaluations. We therefore report distinct units—logical fixture, world/policy evaluation, measured process, response and unit test—rather than equating each output row to an independently sampled unit.


**X0-A deterministic**

**Exact input/evaluation units:** 12 fixed logical fixture families, including expected rejection/negative controls

**Source type and actual status:** Hand-specified synthetic version/dependency/warrant states; bounded PASS

**What the result tests:** Transition/scoring semantics and deliberate hidden-truth separations


**X0-B exact-eight-atom**

**Exact input/evaluation units:** 8 probability atoms; 3 fixed policies; 24 world/policy comparisons; 7 test groups

**Source type and actual status:** Synthetic known-law exhaustive arithmetic; PASS

**What the result tests:** Fraction/Bayes calculations, allowable observations, terminal state scoring


**Audit Allocation Pilot v0.1**

**Exact input/evaluation units:** 16 atoms × 2 stipulated conditions × 4 policies = **128 scored rows**; 7 tests

**Source type and actual status:** Synthetic exact enumeration, **not** 128 independent subjects/trials; PASS

**What the result tests:** Conditional terminal risk, adaptive policy logic and limited audit cost accounting


**C1 one consumer**

**Exact input/evaluation units:** One retained worker versus one restarted worker; **separate** two-version, one-input gzip check; 3 unit tests

**Source type and actual status:** Public PyPI records and real pinned library versions in a disposable Python environment; bounded engineering PASS on separate axes

**What the result tests:** Installed/loaded-version disagreement and one local streaming difference


**P2 final egress**

**Exact input/evaluation units:** 2 scripted deterministic worlds × 2 predetermined queries = **4 delivered responses**; 5 unit tests

**Source type and actual status:** Local non-generative gateway with controlled post-generation override; instrument PASS

**What the result tests:** Pre-egress equivalence and actual final client-response distinction


X0-A, X0-B and the audit pilot use synthetic stipulated truth and do not estimate a natural population's model performance or source error rates. C1 downloads two specific public software wheels and public release metadata, rather than sampling external AI knowledge bases. P2 reuses the C1 public metadata snapshot; it collects no new real-world knowledge corpus and does not execute a large language model. The repository records no use of private customer records or human-subject datasets for these scoped pilots, but rights/licensing and redistribution details still require review before manuscript submission.

### C.2 X0-A: deterministic transition and warrant-scoring conformance

The X0-A testbed [S5,S6] fixes the event, old historical influence graph (potentially incompletely logged), active successor support graph, published/servable/staged/withdrawn version sets \(M,B,Q,P\), and a W1 witness associated with a staged successor. An independent post-replay scorer can consult sealed synthetic truth, while the policy-visible transition may not. The twelve frozen fixture families cover such cases as: a stale descendant omitted from logged reachability; a valid independently warranted positive recovery; a **correct-content but contaminated-origin** invalid warrant; a false-positive validator report; un-staged publication rejection; atomic same-identity replacement; optional-budget boundaries; safe abstention without positive recovery; identical visible traces under different hidden correctness; failed repairs; and preservation of unrelated valid old knowledge.

Recorded result: the approved bounded X0-A conformance suite passed its twelve fixture obligations as reported in the later final X0-A report [S6]. **Interpretation:** software behaves in accordance with this stipulated finite synthetic contract. Neither the offline gold scorer nor a check label is a deployed truth witness. We do not interpret the twelve families as independent field experiments.

### C.3 X0-B: exact finite prior/validator model

The X0-B final report [S7] uses exact rational arithmetic (Python's Fraction class) over eight stipulated \((H,C,V)\) atoms, where \(H\) denotes old hazard, \(C\) successor correctness and \(V\) an observed validation result. Synthetic parameters \(h=1/4,\ c=3/4,\ t=4/5,\ f=1/5\) are **not estimated from auditors**. The 24 world/policy comparisons and seven test groups matched frozen independent expectations in one suite invocation. Its conditional unsafe risk after a publication-relevant PASS under the stated strategies is \(1/13\); the full report also distinguishes reachable FAIL histories and undefined histories from numerical zero risks.

Observed policy aggregates in that fixed testbed:


**\(\pi_0\) (no paid validation)**

**\(\Pr(\mathrm{GlobalUnsafe})\):** \(1/4\)

**\(\mathbb E[W]\):** \(0\)

**Interpretation:** residual old hazard not fixed by abstention


**\(\pi_R\) (repair/check/conditional replacement)**

**\(\Pr(\mathrm{GlobalUnsafe})\):** \(11/80\)

**\(\mathbb E[W]\):** \(3/5\)

**Interpretation:** may retain old unsafe risk after failed check


**\(\pi_Q\) (quarantine before repair/check)**

**\(\Pr(\mathrm{GlobalUnsafe})\):** \(1/20\)

**\(\mathbb E[W]\):** \(3/5\)

**Interpretation:** suppresses the residual old-serving component at an extra action and retained-old cost


The stipulated difference \(11/80-1/20=7/80\) is **not a measured causal effect in real knowledge stores**. X0-B is not the MH-2/T1/T3 exact-check model and does not establish their zero-risk frontiers.

### C.4 Audit Allocation Pilot: known-Bayes synthetic control

The separate Audit Allocation Pilot [S8] exactly enumerated two stipulated laws (L/R), 16 positive-probability atoms and four policies. One test-suite invocation passed seven checks; across conditions there were **128 scored table rows**, not 128 random draws or replicates. In each condition, the appropriate fixed paid-audit arm and its exact optimized comparator attained expected newly warranted recoveries \(\mathbb E[W]=459/800\); the inappropriate fixed arm and immediate quarantine attained zero. For publishing histories under the predeclared appropriate policy:

\[
\Pr(\mathrm{GlobalUnsafe}=1\mid\mathrm{publishing\ history})
   =\frac{101}{560}\ \approx0.18036\le\delta=\frac15.
\]

The corresponding **unconditional** unsafe mass is \(101/800>0\), not zero. The optimized comparator's expected post-event paid-action count is \(13/10\), with worst-path \(K=2\). Its objective was maximal expected \(W\) with **expected \(K\) used only to break ties**, not general monetary cost minimization. The verifier sensitivity \(9/10\), false PASS \(1/10\), independence assumptions and probability table were stipulated synthetic inputs.

The model explicitly counts preparation and publication administration separately: a schematic expected full cost is

\[
\mathbb E[C_{\mathrm{full}}]
 =\mathbb E[K]+S+A\,\Pr(\mathrm{publication}),
\]

where \(S\) and \(A\) are **symbolic, unpriced**. This is not an empirical monetary efficiency comparison. The synthetic \(\delta=1/5\) audit control cannot be reported as verification of the \(\delta=0\) mathematical theorems.

### C.5 C1 — Installed-versus-Loaded State with a Separate Streaming Control

In the C1 isolated Python environment [S9,S10], an old worker had imported `urllib3 2.0.0` before an on-disk upgrade to `2.0.2`. The post-update **complete `pip inspect` records were byte-identical** across the retained-worker and restarted-worker conditions and reported on-disk `2.0.2`. Yet a probe of the retained worker returned loaded version `2.0.0` (PID 17), while a new worker returned `2.0.2` (PID 29). These processes ran sequentially and were stopped/reaped. Within this declared one-consumer boundary, installed metadata alone did not identify the imported-version response.

**Separately**, a locally authored in-memory gzip input representing a finite closing compressed stream was tested in **fresh subprocesses** for the two library versions. The expected uncompressed reference length was 262,144 bytes; the old version yielded 1,024 bytes in one chunk, while version 2.0.2 yielded the full 262,144 bytes in 256 chunks, with a SHA-256 match to the locally authored reference. These streaming responses were **not measured through retained worker PID 17**. The two C1 observation axes must not be merged into a fictitious continuous old-worker streaming trace, nor extrapolated to arbitrary HTTP flows or universal package correctness.

The original streaming program printed size, digest and equality summaries; its original raw compressed/reference/returned bytes were not archived as independent detached evidence. C1's one-input equality is a legitimate bounded software observation, but not a complete independent W1/P4b semantic certificate.

### C.6 P2 — Generated-versus-Delivered Response Control

The P2 gateway [S11,S12] reuses the frozen original C1 **PyPI issuer-declared release state** for `urllib3 2.0.0` (`yanked=true` at the retained snapshot). It evaluates exactly one knowledge identity `x`, one local stdin/stdout route R, and two query contexts \(\{q_1,q_2\}\) under two sequential deterministic conditions. In GOOD, both delivered answers state `yanked=true`. In STALE_EGRESS, source/store/retrieval/generated semantic records remain the same but a **deliberately scripted** post-generation override changes only the final \(q_2\) answer to `yanked=false`.


\Needspace{9\baselineskip}
\begin{center}
\small
\begin{tabular}{lcccc}
\hline
World & Query & Generated & Received & Source match? \\
\hline
GOOD & $q_1$ & true & true & yes \\
GOOD & $q_2$ & true & true & yes \\
STALE\_EGRESS & $q_1$ & true & true & yes \\
STALE\_EGRESS & $q_2$ & true & false & no \\
\hline
\end{tabular}
\end{center}

All four actual client pipe byte receipts match the separately recorded gateway-sent bytes and their SHA-256. Consequently \(q_1\) alone does not distinguish the two **constructed** worlds, while \(q_2\) does. Five unit tests passed in one invocation, no additional answer sequences were run, and OpenTelemetry was **not installed**; the supplementary OTel axis was SKIPPED and its standard-library logical spans are not represented as OTel traces.

This is an **instrument conformance result under scripted deterministic corruption**, not the discovery of an unexpected production cache bug, a live LLM benchmark, an authenticated all-route service audit, or a proof of independently correct successor knowledge. Its source-fidelity scorer checks **P4a**, i.e. whether an answer matches *what PyPI reported at the captured version-specific snapshot*. It does not establish **P4b/W1**, i.e. independent, substantively sound knowledge with complete source-origin independence and lawful contextual use.
