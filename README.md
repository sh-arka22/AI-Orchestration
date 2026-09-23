# AI Orchestration — First-Principles Study Guide

A from-first-principles study guide on **distributed systems, distributed machine learning, and AI-agent orchestration**. It began as preparation for a founding-engineer interview at a power-grid engineering-data company ([Squid](https://www.squid.energy)) and is kept here as a general-purpose reference for anyone building agentic systems on top of transactional data, durable workflows, and LLM-driven decision-making.

**31 sections in nine parts.** Sections 1–18 build the service-level argument: what a system is, where capacity goes, why distribution is hard, and how to make agent workflows durable and auditable. Sections 19–31 go a level down, to the question underneath it — **when many machines must agree on one evolving value, what does the agreement cost, and what do you give up by weakening it?** — and then show that LLM agent orchestration is that same problem with tokens in place of gradients.

> **Scope note.** This repository does **not** claim to describe Squid's actual internal architecture or its real interview questions. Verified company facts (product description, job requirements, security posture) are cited to primary sources in [`sources/`](sources/). Everything else — system designs, capacity numbers, and interview questions — is explicitly a *proposal* or a *worked hypothetical*, built to reason correctly about the class of problems the company's public materials point to.

## How this repository is organized

| Path | What it is | Why it exists |
|---|---|---|
| `docs/01`–`06` | The 18-section study guide, one file per section, cross-linked prev/next | The core, first-principles-to-applied argument — read in order |
| `docs/07-adversarial-reviews/` | Two independent adversarial reviews (distributed systems; agentic orchestration) | Stress-tests the guide's claims with 15 + 10 hard questions, traps, and follow-ups from a separately-run research pass with its own citation ledger |
| `docs/08-revision/` | Condensed quick-revision sheet | Same content, compressed for last-mile rehearsal |
| `docs/09`–`11` | **Parts VII–IX: scaling and distributed learning, sections 19–31** | The mechanics underneath agent orchestration — communication cost models, collectives, data/model parallelism, parameter servers, gossip, federated learning, multi-agent RL, and the isomorphism to LLM agent systems |
| `docs/12-appendix/` | Source appraisal of the three documents behind Parts VII–IX | States plainly which claims rest on settled ground and which rest on a single paper's assertion |
| `sources/ledger.json` | Every source touched during research (75 entries) | Full provenance trail |
| `sources/cited-sources.json` | The subset of sources actually cited in `docs/` (70), each with a verified excerpt | What every `[n]` marker resolves to |
| `sources/calculations.json` | The hypothetical numeric examples (queueing, tokens/min, capacity) worked out separately from prose | Keeps invented numbers auditable and separate from claims |
| `sources/verification.json` | Structural self-checks (section count, balanced code fences, required disclaimers present) | Machine-checked instead of asserted |
| `scripts/verify_citations.py` | Re-runs the citation check on this exact repo layout | `python3 scripts/verify_citations.py` |
| `scripts/verify_structure.py` | Checks every internal link resolves, every doc is reachable from this README, code fences are balanced, and every Mermaid block is well-formed | `python3 scripts/verify_structure.py` |

## Reading order

### Part I — First principles

1. [What Squid actually does—and how that changes your preparation](docs/01-first-principles/01-what-squid-actually-does-and-how-that-changes-your-preparation.md)
2. [First principles: what is a system?](docs/01-first-principles/02-first-principles-what-is-a-system.md)
3. [Scaling, concurrency, parallelism, and distribution are different](docs/01-first-principles/03-scaling-concurrency-parallelism-and-distribution-are-different.md)
4. [Capacity, queues, backpressure, and tail latency](docs/01-first-principles/04-capacity-queues-backpressure-and-tail-latency.md)
5. [What makes distributed systems hard?](docs/01-first-principles/05-what-makes-distributed-systems-hard.md)

### Part II — Consistency and transactions

6. [Replication, partitioning, consistency, CAP, and consensus](docs/02-consistency-transactions/06-replication-partitioning-consistency-cap-and-consensus.md)
7. [Transactions, concurrent edits, and safe publication](docs/02-consistency-transactions/07-transactions-concurrent-edits-and-safe-publication.md)

### Part III — Messaging and reliability

8. [Queues, delivery guarantees, retries, and idempotency](docs/03-messaging-reliability/08-queues-delivery-guarantees-retries-and-idempotency.md)
9. [Outbox, sagas, leases, and fencing](docs/03-messaging-reliability/09-outbox-sagas-leases-and-fencing.md)

### Part IV — Agentic orchestration and data systems

10. [Why agents need durable workflows](docs/04-agentic-and-data-systems/10-why-agents-need-durable-workflows.md)
11. [LLM inference, retrieval, security, and evaluation](docs/04-agentic-and-data-systems/11-llm-inference-retrieval-security-and-evaluation.md)
12. [Data-intensive and scientific-computing design](docs/04-agentic-and-data-systems/12-data-intensive-and-scientific-computing-design.md)

### Part V — Applied architecture

13. [A worked Squid-like system design](docs/05-applied-architecture/13-a-worked-squid-like-system-design.md)
14. [Observability, reliability, security, and operations](docs/05-applied-architecture/14-observability-reliability-security-and-operations.md)
15. [Founding-engineer judgement: what not to overbuild](docs/05-applied-architecture/15-founding-engineer-judgement-what-not-to-overbuild.md)

### Part VI — Interview delivery and revision

16. [Interview question bank with answer spines](docs/06-interview-and-revision/16-interview-question-bank-with-answer-spines.md)
17. [How to deliver a strong answer aloud](docs/06-interview-and-revision/17-how-to-deliver-a-strong-answer-aloud.md)
18. [Revision priorities and self-testing](docs/06-interview-and-revision/18-revision-priorities-and-self-testing.md)

### Part VII — Distributed learning foundations

19. [Why one machine is not enough: the three walls](docs/09-distributed-learning-foundations/19-why-one-machine-is-not-enough-three-walls.md)
20. [The cost of a message: alpha, beta, and the hierarchy](docs/09-distributed-learning-foundations/20-the-cost-of-a-message-alpha-beta-and-the-hierarchy.md)
21. [The primitives of distributed communication](docs/09-distributed-learning-foundations/21-the-primitives-of-distributed-communication.md)
22. [Data-parallel SGD and ring all-reduce](docs/09-distributed-learning-foundations/22-data-parallel-sgd-and-ring-all-reduce.md)
23. [The parameter server, and what "the parameters at time t" means](docs/09-distributed-learning-foundations/23-the-parameter-server-and-the-meaning-of-time.md)
24. [When the model does not fit: model, pipeline, tensor, and fully-sharded parallelism](docs/09-distributed-learning-foundations/24-when-the-model-does-not-fit-model-pipeline-fsdp.md)

### Part VIII — Decentralised and multi-agent learning

25. [Removing the centre: gossip, consensus, and why topology is destiny](docs/10-decentralized-and-multi-agent/25-removing-the-centre-gossip-consensus-and-topology.md)
26. [Federated learning: when the data cannot move](docs/10-decentralized-and-multi-agent/26-federated-learning-when-the-data-cannot-move.md)
27. [When workers have their own goals: multi-agent reinforcement learning](docs/10-decentralized-and-multi-agent/27-when-workers-have-their-own-goals-multi-agent-rl.md)
28. [Robustness: Byzantine aggregation, and how to read a claim](docs/10-decentralized-and-multi-agent/28-robustness-byzantine-aggregation-and-reading-claims.md)

### Part IX — Agentic orchestration at scale

29. [LLM agent orchestration: architecture and protocols](docs/11-agentic-orchestration-at-scale/29-llm-agent-orchestration-architecture-and-protocols.md)
30. [The isomorphism, and the two laws that are genuinely new](docs/11-agentic-orchestration-at-scale/30-the-isomorphism-and-the-two-laws.md)
31. [The unified ladder, and how to say it out loud](docs/11-agentic-orchestration-at-scale/31-the-unified-ladder-and-how-to-say-it.md)

### Appendix

- [Source appraisal: the three documents behind Parts VII–IX](docs/12-appendix/source-appraisal-three-documents.md)

### Independent adversarial reviews

- [Distributed-systems adversarial review](docs/07-adversarial-reviews/distributed-systems-review.md) — 15 hard questions, correct-answer principles, common traps, architecture critique
- [Agentic-orchestration adversarial review](docs/07-adversarial-reviews/agentic-orchestration-review.md) — 10 scenarios on durable execution, evaluation, retrieval, and inference-serving economics

### Revision

- [Quick-revision sheet](docs/08-revision/quick-revision.md)

## The one idea that ties every section together

> **Pin the model. Bound the work. Persist progress. Make retries safe. Validate the results. Approve the exact artifact.**

Everything from Little's Law (§4) to CAP (§6) to durable workflow replay (§10) to tool-call validation for LLM agents (§11) is a specific instance of this same discipline: **distribution creates ambiguity about what happened; the system must resolve that ambiguity explicitly rather than assume the happy path.**

Parts VII–IX restate the same idea as a cost:

> **Splitting work is free. Re-agreeing is not.**

Ring all-reduce, parameter servers, FSDP, gossip, FedAvg, MCP, and A2A are all different answers to one
question: *how do N workers get back into agreement without paying more for the agreement than they saved by
splitting?* Section 31 tabulates every answer against the same three questions — who holds the truth, how do
the copies agree, and what does agreeing cost.

And one thing in the agentic layer is genuinely new (§30). In distributed training a message is delivered or
it is not. In an agent system a message can be delivered, well-formed, schema-valid, confident, fluent, **and
wrong** — a semantically lossy channel with no checksum. With per-agent reliability `p`, a chain of `n` agents
succeeds with `p^n`. That is why validation gates are error correction rather than bureaucracy.

## Verifying the citations yourself

```bash
python3 scripts/verify_citations.py
python3 scripts/verify_structure.py
```
This walks every `docs/**/*.md` file, confirms every `[n]` marker resolves to an entry in `sources/cited-sources.json`, and confirms that entry carries a verified excerpt (not just a bare link).

Sources `[73]`–`[75]` are the three PDFs that Parts VII–IX were built from. They are recorded with a `local:`
URL scheme because they were read directly as supplied documents rather than fetched from the web; their
bibliographic details are in the ledger and their appraisal is in [the appendix](docs/12-appendix/source-appraisal-three-documents.md).

## Provenance

Built in three passes:

1. **First-principles research pass** — sections 1–18, the service-level argument.
2. **Two independent adversarial review passes** — separate citation ledgers, later merged into
   `sources/ledger.json` with stable ids.
3. **Distributed-learning pass** — sections 19–31 and the appendix, built from three primary documents
   (sources `[73]`–`[75]`) and grounded against 22 further sources fetched and excerpt-verified during the
   pass: the foundational papers for ring all-reduce and collectives[49], decentralised SGD[50], federated
   averaging[51][58][63], gradient compression[52], large-batch limits[53][62], pipeline and sharded
   parallelism[54][55][56][57], multi-agent RL[59][60][61][64], Byzantine robustness[65], and the agentic
   orchestration protocols and their scaling critiques[66][67][68][69][70][71][72].

Every `[n]` marker in `docs/` resolves to an entry in `sources/cited-sources.json` carrying a verified
excerpt. See `sources/verification.json` for the machine-checked structural claims, and run both scripts in
`scripts/` to reproduce them.
