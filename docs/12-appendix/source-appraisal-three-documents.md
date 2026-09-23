# Appendix — Source appraisal: the three documents behind Part VII–IX

[← 31. The unified ladder](../11-agentic-orchestration-at-scale/31-the-unified-ladder-and-how-to-say-it.md) | [↑ Table of contents](../../README.md)

---

Sections 19–31 were built by reading three documents that look unrelated and are in fact the same problem at
three altitudes. This appendix records what each one is, what it is good for, and where it should not be
trusted — so that a reader can tell which claims in Part VII–IX rest on settled ground and which rest on a
single paper's assertion.

### The three altitudes

| Document | Altitude | A "worker" is… | A "message" carries… |
|---|---|---|---|
| CS4787 Lecture 20, *Distributed Machine Learning and the Parameter Server*[75] | Metal | A GPU or process | fp32/fp16 gradients |
| *Scalable Multi-Agent Orchestration for Federated and Distributed AI Learning* (ICDCA 2026)[73] | Learning agents | An RL agent with its own reward | Policy information, local updates |
| *The Orchestration of Multi-Agent Systems* (arXiv:2601.13671)[74] | LLM agents | An LLM with a role and tools | Tokens, plans, task results |

All three ask the same three questions: **who holds the truth, how do the copies agree, and what does agreeing
cost?** Section 31 tabulates the answers side by side.

---

## 1. CS4787 Lecture 20 — Distributed ML and the Parameter Server[75]

**What it is.** Course material from an established systems-for-ML curriculum. Covers point-to-point and
collective communication patterns, overlapping computation and communication, all-reduce SGD, the parameter
server model (synchronous, asynchronous, sharded), model parallelism, pipeline parallelism, and FSDP.

**What Part VII takes from it.** The entire mechanical backbone of §21–§24, including two framings this guide
treats as load-bearing:

- The question *"what should we consider to be the value of the parameters at a given time?"*, which turns the
  parameter server from a performance trick into a **consistency model** (§23).
- The explicit naming of **stalls** and the principle of overlapping computation and communication (§21).

**Trust: high.** These are settled results with decades of validation and production implementations. Where
this material conflicts with either paper below, it wins.

**What this guide adds.** The lecture *states* that all-reduce scales; §22 derives why (ring decomposition,
the `M→∞` limit, the bandwidth-optimality argument) and adds the α–β cost model (§20) the lecture assumes
rather than states.

---

## 2. The CIO framework paper (ICDCA 2026)[73]

**What it is.** Proposes a "Collective Intelligence Optimization" framework for coordinating large-scale
multi-agent systems: decentralised decision-making, adaptive coordination, selective communication, consensus
formation, conflict resolution, and compression. Reports simulation results at 20/50/100 agents against a
multi-agent RL baseline.

**What Part VIII takes from it.** The *architectural inventory*. Its graph formulation `G = (A, E)` maps
directly onto §25's gossip model, and its five named mechanisms are each a real technique from a literature
where they have proofs. §27 tabulates that translation explicitly — selective communication is gradient
sparsification (and needs error feedback[52]); adaptive weighting is a learned mixing matrix (and needs double
stochasticity[50]); consensus is average consensus (and needs a spectral gap).

**Trust: low on results, medium on architecture.** Section 28 works through the appraisal in detail. In
summary:

- Recomputing per-agent latency from the paper's own table yields exactly 6.0 ms for the baseline at every
  scale and exactly 4.5 / 4.0 / 3.5 for the proposed method — a perfect arithmetic sequence. Both reward
  columns are also perfect arithmetic sequences. Real measurements do not behave this way.
- No error bars, no seeds, no named environment, no released code, no evidence of baseline tuning.
- The reference list is dominated by same-cluster citations on unrelated topics.

**How to use it.** As a well-chosen **menu of mechanisms**, each of which should be cited to its rigorous
source rather than to this paper. The framework's central claim — that decentralisation scales — is *true*,
and §25 supplies the proof and the missing precondition (spectral gap) that the paper itself never states.

---

## 3. The orchestration survey (arXiv:2601.13671)[74]

**What it is.** A survey and position paper on orchestrated multi-agent LLM systems: a taxonomy of specialised
agents (worker / service / support), a five-unit orchestration layer (planning, policy, execution-and-control,
state-and-knowledge, quality-and-operations), a treatment of MCP and A2A as complementary communication axes,
and a set of enterprise case studies.

**What Part IX takes from it.** The vocabulary and the decomposition, both of which are genuinely good:

- Worker / service / support maps cleanly onto **plant / controller / observer**, which tells you which
  components may mutate workflow state (§29).
- The separation of **policy constrains before** from **quality validates after**, and of **operational state**
  from **knowledge state** (§29).
- The framing of MCP and A2A as orthogonal axes rather than competitors — a framing both protocols' own
  documentation confirms independently.[70][71]

**Trust: medium.** The paper runs **no experiments of its own**. Its headline figures — "over 95% accuracy",
"20× faster approvals with 80% cost reduction", "up to 80% of support incidents resolvable", "over 50%
reduction in development time" — trace to vendor blog posts, a consultancy report, and a low-tier journal.
Treat the taxonomy as a contribution and the ROI numbers as marketing.

**What this guide adds.** The two quantitative laws the survey never states (§30): error compounding `p^n`,
which turns the quality unit from governance into error correction, and Amdahl's cap on agent parallelism,
including the `O(N²)` token cost of broadcast context. It also connects the survey's own acknowledgement of
static-structure limitations to §25's spectral gap, via two independent 2025 results.[66][67]

---

## Reading discipline, generalised

The checklist from §28, restated for reuse:

1. **Recompute a derived quantity the authors did not show** — per-unit cost, ratio, efficiency. Synthetic
   tables rarely survive it.
2. **Look for variance.** No error bars, no seeds, no claim.
3. **Check whether the baseline was tuned.** An untuned baseline is not a baseline.
4. **Check the reference list for topical coherence.**
5. **Separate the architecture from the evidence,** and cite each to the appropriate source.

This is the same discipline §1 applies to company claims and §15 applies to architectural fashion: **cite what
was verified, label what was assumed.**

---

[← 31. The unified ladder](../11-agentic-orchestration-at-scale/31-the-unified-ladder-and-how-to-say-it.md) | [↑ Table of contents](../../README.md)
