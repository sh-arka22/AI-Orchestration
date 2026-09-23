# 18. Revision priorities and self-testing

[← 17. How to deliver a strong answer aloud](17-how-to-deliver-a-strong-answer-aloud.md) | [↑ Table of contents](../../README.md) | [19. Why one machine is not enough →](../09-distributed-learning-foundations/19-why-one-machine-is-not-enough-three-walls.md)

---

### Highest priority

Explain aloud, with one failure scenario each:

- Bottlenecks, Little’s law, queue stability, tail latency.
- Partial failure, timeout ambiguity, idempotency, at-least-once delivery.
- Transactions, isolation, optimistic concurrency, immutable versions.
- Replication versus sharding, CAP, consensus basics.
- Durable agent workflows and recorded nondeterministic outputs.
- Outbox, leases/fencing, safe external effects.
- Tenant isolation, approval binding, reproducible studies.

### Second priority

Inference/KV cache/batching, columnar and object storage, caching correctness, tracing/SLOs, cancellation, recovery objectives, and load testing.

### Specialist depth if the interview goes there

Consensus log rules, quorum read protocols, distributed transactions, vector clocks/CRDT limitations, multi-region failover, solver parallelisation, and GPU parallelism.

### Four focused study sessions

**Session A:** derive capacity and queue behaviour, then explain why more instances can fail to help.

**Session B:** draw the crash windows for queue delivery, external effects, and dual writes; solve each without claiming magical exactly-once behaviour.

**Session C:** design the complete Squid-like model-to-study-to-approval flow on a blank page; include manifests and permission boundaries.

**Session D:** answer the practice questions aloud, then inject failures: stale worker, stale approval, cross-tenant retrieval, unavailable provider, non-convergent solver, missing artifact.

### Self-test scoring

For each answer, ask:

- Did I define the term precisely?
- Did I explain why the problem exists?
- Did I tie it to this product?
- Did I state a trade-off and a failure case?
- Did I separate verified facts from assumptions?
- Did I propose a metric or test that could show my design is wrong?

The strongest interview performance is not the largest vocabulary. It is a clear chain from **requirement → invariant → failure model → minimal design → measurement**.

---

## Research scope and methods

This is an engineering interview research brief, not a systematic literature review or a 60-reference manuscript packet. Evidence prioritised Squid’s own pages, its public vacancy, original distributed-systems material, and official operational documentation. Product marketing statements were not treated as independently audited architecture disclosures. The PagedAttention and scientific-skills arXiv pages were read at the abstract/metadata level; no claim of full-paper review is made for them. The CAP perspectives paper was extracted; an initially downloaded CAP-proof PDF had unreadable text and was not used as supporting evidence.

Parallel source extraction initially worked, but subsequent Parallel requests returned an insufficient-credit error; the installed Parallel CLI was not authenticated. No completed Parallel Deep Research report is claimed. The brief instead uses direct public-page retrieval, other search/extraction services, and independent engineering review. Generic search returned an unrelated company, getsquid.ai; that entity was excluded.

Research Lookup and Scientific Brainstorming supplied evidence-separation and adversarial-review procedures. Methods attribution: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, https://doi.org/10.48550/arXiv.2609.00065. Current metadata was checked; this methods reference is not evidence for the engineering conclusions.[20]

## Sources

[1] https://www.squid.energy — Squid: The grid has a repo now
[2] https://www.ycombinator.com/companies/squid/jobs/9fYL446-software-engineer — Software Engineer at Squid | Y Combinator
[5] https://www.squid.energy/security — Squid security
[6] https://research.google/pubs/the-tail-at-scale — Dean and Barroso: The Tail at Scale
[7] https://raft.github.io — Raft consensus
[9] https://www.postgresql.org/docs/current/transaction-iso.html — PostgreSQL transaction isolation
[11] https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs — AWS: Making retries safe with idempotent APIs
[12] https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html — AWS: Transactional outbox
[13] https://docs.temporal.io/workflow-execution — Temporal workflow execution
[14] https://www.anthropic.com/engineering/building-effective-agents — Anthropic: Building effective agents
[15] https://docs.langchain.com/oss/python/langgraph/durable-execution — LangGraph durable execution
[16] https://arxiv.org/abs/2309.06180 — PagedAttention / vLLM
[17] https://genai.owasp.org/llmrisk/llm01-prompt-injection — OWASP prompt injection
[18] https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html — Amazon S3 consistency and storage
[19] https://www.postgresql.org/docs/current/ddl-rowsecurity.html — PostgreSQL row-level security
[20] https://arxiv.org/abs/2609.00065 — Scientific Agent Skills methods attribution
[21] https://sre.google/sre-book/handling-overload — Google SRE handling overload
[22] https://lamport.azurewebsites.net/pubs/time-clocks.pdf — Lamport: Time clocks and ordering
[23] https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf — Perspectives on the CAP Theorem
[25] https://docs.temporal.io/design-patterns/long-running-activity — Temporal long-running activities and checkpoints
[26] https://matpower.app/manual/matpower/ACPowerFlow.html — MATPOWER AC power flow
[27] https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — Anthropic: Demystifying evals for AI agents

---

[← 17. How to deliver a strong answer aloud](17-how-to-deliver-a-strong-answer-aloud.md) | [↑ Table of contents](../../README.md) | [19. Why one machine is not enough →](../09-distributed-learning-foundations/19-why-one-machine-is-not-enough-three-walls.md)
