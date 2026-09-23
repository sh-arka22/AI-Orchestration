# 16. Interview question bank with answer spines

[← 15. Founding-engineer judgement: what not to overbuild](../05-applied-architecture/15-founding-engineer-judgement-what-not-to-overbuild.md) | [↑ Table of contents](../../README.md) | [17. How to deliver a strong answer aloud →](17-how-to-deliver-a-strong-answer-aloud.md)

---

These are practice questions inferred from the product and role, not reported interview questions.

### Core questions

**1. What do you mean by scaling?**

Define the workload, useful throughput, latency/quality/cost targets, and current bottleneck. Explain vertical/horizontal trade-offs and why adding instances may not remove a shared limit.

**2. How would you handle a large increase in users?**

Do not immediately shard. Estimate user activity and downstream fan-out, profile, eliminate unnecessary work, protect queues and dependencies, scale stateless/worker paths, then evaluate database/storage limits.

**3. What happens if a worker crashes halfway through an agent task?**

Durable run state, stable step IDs, pinned inputs, recorded outputs, safe retries, reconciliation of external effects, lease/generation ownership. Distinguish model replay from regenerating a model decision.

**4. How do you guarantee exactly-once execution?**

Ask the boundary. Usually guarantee one logical committed effect using idempotency and transactions, while accepting possible repeat execution. Explain the external action/crash window.

**5. What is CAP?**

Define linearizability, availability in the theorem, and a communication partition; walk through the two-replica example. Explain per-operation choices and avoid the “pick any two at all times” slogan.

**6. Why is a cache potentially dangerous here?**

A result can be for the wrong model, assumptions, solver, tenant, or permission context. Define cache keys, invalidation/immutability, correctness requirements, and stale-result policy.

**7. How do two engineers edit the same model?**

Pinned base, independent proposals, optimistic concurrency or short locking, semantic merge, revalidation, exact approval binding. Convergence is not domain validity.

**8. SQL, NoSQL, or graph database?**

Start with access patterns and invariants. Use relational metadata/transactions, object/columnar artifacts for volume, and specialised indexes only when justified by queries.

**9. Why use asynchronous jobs?**

Long/variable durations outlive request timeouts and need independent retries/capacity. Return run ID, persist status, report progress, define cancellation. Queues do not create capacity.

**10. How would you reduce agent latency?**

Trace the critical path, reduce unnecessary calls/context/output, parallelise independent work with limits, cache exact/versioned work, use evaluated smaller models, manage prefill/decode bottlenecks and quotas. Distinguish first output from completed result.

**11. Why not let the LLM run arbitrary SQL or code?**

Prompt injection and incorrect output. Constrain tools and schemas, authorise in code, sandbox execution/egress, preserve approval boundaries. No model-generated tenant identity is trusted.

**12. How do you know the agent is correct?**

Task-level evaluations, exact assertions, reference studies, solver validity, provenance, safety checks, and human review. Separate retrieval, reasoning, tool, and infrastructure failures.

### Follow-ups that expose depth

**13. A lease expired. Why can the old worker still be dangerous?**

Pauses and partitions do not stop its code. Receiver-enforced fencing rejects obsolete ownership; external effects may need their own idempotency/reconciliation.

**14. The DB committed but queue publication failed. What now?**

Outbox or suitable CDC; replayable dispatch; duplicate-safe consumption. Explain the crash after publish but before marking delivered.

**15. Does serializable mean everyone immediately reads the latest value?**

No. Distinguish serializable transaction histories from linearizability/strict serializability and replica routing.

**16. What if only one of many study cases fails?**

Persist successful cases; retry only appropriate failures; identify missing coverage; do not label a comparison complete if required cases are absent. Define partial-result policy.

**17. What would you do during a provider outage?**

Durable wait/backpressure, deadlines, circuit breaker, bounded retries, transparent status. Any model fallback must be permitted and evaluated, not silently assumed equivalent.

**18. How would you isolate customers?**

Tenant identity at every boundary, permissions/RLS and appropriate DB roles, storage/cache/index/log isolation, quotas/fairness, possibly dedicated infrastructure.

**19. When would you use microservices?**

When independent scaling, deployment, fault containment, or team ownership provides concrete value greater than network/coordination costs. An early modular monolith plus workers is often easier to operate.

**20. How would you partition a large grid simulation?**

Distinguish parallel scenarios from partitioning a coupled numerical solve. Preserve boundary conditions and solver semantics; consult supported algorithms rather than hash-partitioning physics.

**21. Does temperature zero make a study reproducible?**

No universal guarantee. Pin available model versions and prompts, record outputs, isolate nondeterminism, and distinguish audit replay from recomputation.

**22. What does a circuit breaker solve that retries do not?**

It stops repeatedly loading a failing dependency, with controlled recovery probes. Neither replaces idempotency, deadlines, capacity planning, or graceful degradation.

**23. Why can adding more workers reduce throughput?**

Database contention, pool exhaustion, provider throttling, native-thread oversubscription, network/memory saturation, and retry amplification.

**24. What does “we have backups” fail to tell you?**

Whether restoration is tested, the true RPO/RTO, whether all dependent artifacts/keys are recoverable, and whether backups share the same failure/deletion risk.

---

---

[← 15. Founding-engineer judgement: what not to overbuild](../05-applied-architecture/15-founding-engineer-judgement-what-not-to-overbuild.md) | [↑ Table of contents](../../README.md) | [17. How to deliver a strong answer aloud →](17-how-to-deliver-a-strong-answer-aloud.md)
