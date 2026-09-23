# 8. Queues, delivery guarantees, retries, and idempotency

[← 7. Transactions, concurrent edits, and safe publication](../02-consistency-transactions/07-transactions-concurrent-edits-and-safe-publication.md) | [↑ Table of contents](../../README.md) | [9. Outbox, sagas, leases, and fencing →](09-outbox-sagas-leases-and-fencing.md)

---

### 8.1 Why at-least-once delivery appears so often

A worker receives a job, performs work, and acknowledges it.

- Acknowledge **before** the work, then crash: the work may be lost.
- Acknowledge **after** the work, then crash before the acknowledgement reaches the queue: the work may be delivered again.

At-least-once delivery chooses possible duplicates over silent loss. Queue visibility timeouts or leases make abandoned work available again, but do not prevent the original worker from still running.

### 8.2 Exactly-once: always ask “within what boundary?”

You may guarantee one committed state transition inside a transactional database. A broker may guarantee specific transactional consume/produce behaviour within its supported scope. Neither automatically guarantees exactly one external API effect, exactly one email, or exactly one paid inference.

A useful target is **at-least-once delivery with idempotent logical effects**. Sometimes duplicate computation is tolerable while duplicate publication is not.

### 8.3 Idempotency from first principles

An operation is idempotent if repeating it has the same intended effect as applying it once. “Set status to approved” is closer to that property than “increment approval count,” although permissions and version checks are still needed.

Use a stable identity for one **logical operation**, not a fresh identity for every transport attempt:

```text
(tenant_id, operation_type, client_operation_id)
```

Persist the canonical payload digest and result/status. The same identity with a different payload should be rejected, not mistaken for a retry. A database uniqueness constraint closes races between concurrent duplicates. AWS’s idempotent API guidance explicitly treats caller intent and atomic recording of request identity plus mutations as part of the contract.[11]

Important distinctions:

- **Idempotency key:** this is the same requested operation.
- **Content hash:** these bytes/normalised inputs are identical.
- **Cache key:** reuse is valid for this context and version.

Two intentionally separate requests can have identical input data. Content equality alone does not prove duplicate intent.

### 8.4 The external-effect crash window

```text
worker calls external service
external service completes the action
worker crashes before recording success
```

A local `completed = true` table cannot eliminate this gap. Options are:

- Pass a stable idempotency key to a provider that supports it.
- Use an external job ID and reconcile/query the provider’s state.
- Make the external effect itself safely repeatable.
- Accept possible duplicates when they are harmless and budgeted.
- Escalate uncertain, irreversible effects for review.

Do not claim that “check the database before retrying” alone solves it: two workers can race, or the external action may have happened before the database was updated.[11]

### 8.5 Retry policy

Retry transient transport failures, appropriate throttling responses, and known temporary errors. Do not repeatedly retry invalid schemas, permission denial, or physically invalid inputs as though time will repair them.

Use a bounded number of attempts, an overall deadline, exponential backoff with random jitter, and a retry budget. Respect provider-specific throttling guidance. Jitter spreads retry traffic; it does not create capacity. Google’s overload guidance discusses controls that prevent retries from becoming self-amplifying load.[21]

A hypothetical stack with five retrying layers and three total attempts at each layer can send **243 attempts** to the deepest dependency. Centralise retry responsibility where possible and propagate deadlines/cancellation.

A **circuit breaker** temporarily stops calls to a failing dependency; controlled probes determine recovery. A **bulkhead** separates resource pools so a failure or busy tenant cannot exhaust everything.

### 8.6 Dead-letter queues and cancellation

A dead-letter queue is not a bin to forget about. Store a reason, inputs/version references, and attempt history; alert on growth; provide safe inspect/replay tooling.

Cancellation is a state transition, not just closing the browser tab. Workers should check it at safe boundaries. A timed-out caller may leave the server working; an external solver may not support cancellation. Record that distinction and prevent late results from incorrectly publishing into a cancelled/replaced run.

---

---

[← 7. Transactions, concurrent edits, and safe publication](../02-consistency-transactions/07-transactions-concurrent-edits-and-safe-publication.md) | [↑ Table of contents](../../README.md) | [9. Outbox, sagas, leases, and fencing →](09-outbox-sagas-leases-and-fencing.md)
