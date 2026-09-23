# 5. What makes distributed systems hard?

[← 4. Capacity, queues, backpressure, and tail latency](04-capacity-queues-backpressure-and-tail-latency.md) | [↑ Table of contents](../../README.md) | [6. Replication, partitioning, consistency, CAP, and consensus →](../02-consistency-transactions/06-replication-partitioning-consistency-cap-and-consensus.md)

---

### Intuition: messages between offices

You ask a remote office to approve a document. Your call disconnects. Did they receive the request? Did they approve it? Did they approve it and lose the reply? You cannot infer the answer from silence.

A network operation has at least these outcomes:

1. The request never arrived.
2. It arrived but was not processed.
3. It was processed and failed.
4. It committed successfully but the response was lost.
5. It is still processing when you time out.

**A timeout is evidence of uncertainty, not proof of non-execution.** This is why retry behaviour and API contracts belong in the design, not as an afterthought.[11]

Even TCP’s ordered byte delivery within a connection does not give application-level exactly-once processing across crashes and reconnects. You still need message framing, application acknowledgements, operation identities, and durable records.

### Partial failure

On one machine, a crash often stops the whole process. In a distributed system, the API can be healthy while a worker is isolated; the database may accept writes while the event publisher is down; one availability zone may fail while others continue.

Therefore separate:

- **Failure detection:** “I have not heard from this worker recently.”
- **Ownership:** “This worker is currently authorised to commit.”
- **Result truth:** “This result belongs to this model version and attempt.”

A health check or heartbeat establishes none of these perfectly by itself.

### Clocks and ordering

Wall clocks can be skewed or adjusted. “The largest timestamp wins” is not automatically the same as “the latest valid business change wins.” Use wall clocks for human-readable audit times and operational measurements, but explicit versions, sequence numbers, or database ordering for correctness.

Lamport clocks capture a useful property: if event `a` causally precedes `b`, its logical timestamp is smaller. The converse does not hold. Vector clocks can distinguish causality from concurrency under their model, at a metadata cost. Neither clock system decides whether two changes to an electrical model are semantically compatible.[22]

---

---

[← 4. Capacity, queues, backpressure, and tail latency](04-capacity-queues-backpressure-and-tail-latency.md) | [↑ Table of contents](../../README.md) | [6. Replication, partitioning, consistency, CAP, and consensus →](../02-consistency-transactions/06-replication-partitioning-consistency-cap-and-consensus.md)
