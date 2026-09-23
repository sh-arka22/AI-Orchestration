# 10. Why agents need durable workflows

[← 9. Outbox, sagas, leases, and fencing](../03-messaging-reliability/09-outbox-sagas-leases-and-fencing.md) | [↑ Table of contents](../../README.md) | [11. LLM inference, retrieval, security, and evaluation →](11-llm-inference-retrieval-security-and-evaluation.md)

---

### 10.1 Workflow versus agent

A **workflow** follows a code-defined sequence or graph. An **agent** lets a model choose some subsequent actions. Anthropic’s engineering guidance distinguishes these and recommends starting with the simplest solution that meets the task, since agentic flexibility can add latency and cost.[14]

For a governed engineering product, a useful design is:

> A constrained agent inside a deterministic workflow—not an unconstrained agent replacing the workflow.

For example, the model may propose which approved study templates to run, but code enforces valid tool parameters, version binding, budgets, access control, and publication policy.

### 10.2 Turn the agent loop into explicit state

```text
CREATED → VALIDATING → PLANNING → WAITING_FOR_STUDIES
        → CHECKING_RESULTS → AWAITING_REVIEW → PUBLISHED

Any appropriate state → FAILED / CANCELLED / NEEDS_RECONCILIATION
```

Persist run identity, pinned inputs, step states, tool-call identities, external job IDs, outputs, attempts, budgets, and review records. An in-memory loop disappears with the process; a durable state machine can recover.

LangGraph’s persistence documentation distinguishes checkpointed thread/run state from long-term stores. This is a useful separation: **conversation memory, execution state, and authoritative engineering data are different things**.[15]

### 10.3 Queue versus workflow engine

A queue moves units of work. A workflow engine additionally manages durable progression, dependencies, timers, retries, signals, and recovery across multiple units.

A single parse job may only need a queue. “Run cases, wait overnight for engineer approval, resume, publish, recover across deployments” has workflow semantics. Temporal documents event history and replay as the mechanism by which a workflow reconstructs progress.[13]

A workflow engine is not a requirement for every startup. You can begin with a database state machine, provided you deliberately implement claim/lease, retry, timeout, reconciliation, and recovery semantics. At some complexity, buying those semantics is cheaper than maintaining them.

### 10.4 Nondeterminism and replay

A second LLM call can produce a different plan even for the same prompt. Temperature zero is not a universal reproducibility guarantee across serving systems and model versions.

Therefore:

- Keep external I/O and nondeterministic model calls in activities/tasks.
- Persist successful outputs and their model/tool/prompt/input versions.
- Replaying orchestration uses recorded outcomes rather than regenerating past decisions.
- A failed activity may run again if its successful completion was not durably recorded; idempotency and the external crash window still matter.
- Version workflow code carefully so old histories can resume compatibly.

Temporal’s replay compares generated commands with an existing event history; this is a constraint on orchestration determinism, not a promise that every outside action happens once.[13]

### Long-running work: a heartbeat is not a checkpoint

A heartbeat can show that a worker can still communicate and carry a small progress record. It is not a snapshot of arbitrary solver memory. Temporal explicitly requires application checkpointing/state-management logic and safe partial reprocessing.[25]

For an external solver, persist a stable submission identity, reconcile ambiguous submission, retain its job ID when known, and reattach/query rather than blindly resubmit after worker death. If the solver supports real checkpoints, persist them at supported boundaries. Otherwise restart the smallest valid independent case—not an invented “50% complete” state. Time slices are independent only when initial/boundary state and any time coupling are handled correctly.

Likewise, `cancel_requested` is not `execution_stopped`. Do not release a scarce licence slot merely because the caller timed out or a lease expired: the old process may still consume it. Track physical execution state separately from permission to publish.

### 10.5 Durable execution is not deterministic inference

These are separate guarantees:

1. **Resumability:** continue after a crash.
2. **Audit replay:** reconstruct what actually occurred.
3. **Recomputation:** rerun the same declared inputs and environment.
4. **Numerical reproducibility:** results agree within defined tolerances.
5. **Bitwise reproducibility:** every output byte is identical.

A workflow engine can help with the first two. Pinning model and solver versions helps with the others but may not guarantee them, especially with external model services and parallel numerical libraries. Define the promised level explicitly.

### 10.6 Parallel agents and shared state

More agents do not automatically improve quality. They add communication, duplicated work, cost, and conflicting proposals.

Use independent generation for genuinely separable alternatives, with fixed budgets and explicit aggregation. Keep a coordinator responsible for the authoritative transition. If several agents propose edits, give them branches based on a pinned baseline; merge only after domain checks. Do not have all agents freely mutate the same “memory” record.

A simple reliability illustration: if a task requires 20 independently successful steps, each with hypothetical 98% success, the joint probability is about **66.8%**. Real errors are correlated, and this is not an empirical agent benchmark. It demonstrates why reducing unnecessary steps and validating critical transitions matters.

---

---

[← 9. Outbox, sagas, leases, and fencing](../03-messaging-reliability/09-outbox-sagas-leases-and-fencing.md) | [↑ Table of contents](../../README.md) | [11. LLM inference, retrieval, security, and evaluation →](11-llm-inference-retrieval-security-and-evaluation.md)
