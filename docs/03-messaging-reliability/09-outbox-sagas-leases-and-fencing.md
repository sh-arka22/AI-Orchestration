# 9. Outbox, sagas, leases, and fencing

[← 8. Queues, delivery guarantees, retries, and idempotency](08-queues-delivery-guarantees-retries-and-idempotency.md) | [↑ Table of contents](../../README.md) | [10. Why agents need durable workflows →](../04-agentic-and-data-systems/10-why-agents-need-durable-workflows.md)

---

### 9.1 The dual-write problem

You save a study request in Postgres and publish a queue message. What if the process crashes between them?

- Database first: a job exists but nobody starts it.
- Queue first: a worker sees a job that does not exist or was rolled back.

**Transactional outbox:** commit the job and an outbox event in the same database transaction. A dispatcher later publishes committed events. The dispatcher can crash after publishing but before recording delivery, so consumers must still handle duplicates. The outbox solves atomic intent recording, not magical exactly-once delivery.[12]

A broker is not always required at the start: a carefully designed database-backed job table can be reasonable at low scale. Choose a dedicated queue when load, isolation, delayed delivery, or operational requirements justify it.

### 9.2 Saga versus transaction

A saga is a sequence of local transactions with explicit compensating actions for failures. Compensation is a business action, not time travel. You can cancel a reservation; you cannot guarantee that a sent email becomes unread.

Two-phase commit asks participants to prepare, then commit/abort under a coordinator. It solves a different atomic-commit problem and can introduce blocking/availability costs, depending on the protocol and failure handling. It is not interchangeable with Raft, which solves agreement on a replicated log.

For a study workflow, often prefer immutable inputs, separately recorded step outcomes, and explicit run states over holding a distributed transaction open during expensive work.

### 9.3 Lease is temporary ownership; fencing protects the resource

Suppose worker A holds a lease and pauses. The lease expires; worker B acquires it. A resumes. Both may now execute code.

A **fencing token** is a monotonically increasing ownership generation. Every protected write includes the token. The receiving resource checks it atomically and rejects stale generations. Merely logging the token or checking it once before a long operation is insufficient.

There is a subtle distinction between checking the **current authoritative generation** and remembering only the **highest token the receiver has seen**. The latter cannot reject an old owner merely because a new lease exists elsewhere: the receiver must first learn the new generation, or validate it with the authority. Define how the ownership handoff activates at every protected resource.

For a job table, claims can increment `generation`; progress and completion updates require the current generation and expected job state. For an external side effect, the external receiver must support an equivalent protection or idempotency/reconciliation must close the gap. Fencing a database result does not undo a stale solver invocation or an already sent email.

**Interview answer:** “I would distinguish execution from authority to commit. Two attempts might briefly compute, but only the current generation may publish an authoritative result.”

---

---

[← 8. Queues, delivery guarantees, retries, and idempotency](08-queues-delivery-guarantees-retries-and-idempotency.md) | [↑ Table of contents](../../README.md) | [10. Why agents need durable workflows →](../04-agentic-and-data-systems/10-why-agents-need-durable-workflows.md)
