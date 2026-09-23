# 6. Replication, partitioning, consistency, CAP, and consensus

[← 5. What makes distributed systems hard?](../01-first-principles/05-what-makes-distributed-systems-hard.md) | [↑ Table of contents](../../README.md) | [7. Transactions, concurrent edits, and safe publication →](07-transactions-concurrent-edits-and-safe-publication.md)

---

### 6.1 Replication versus partitioning

**Replication:** multiple copies of the same logical data. Useful for availability, disaster recovery, and sometimes read throughput.

**Partitioning/sharding:** divide different data among owners. Useful when a single owner cannot hold or serve the workload.

A system can use both: partition by tenant or network, replicate each partition. Replication does not automatically multiply write capacity; every replica may need to apply the same writes. Sharding creates new problems: routing, rebalancing, hot partitions, cross-shard joins, and transactions.

A tenant is often a convenient initial boundary, but one huge tenant can still dominate a shard. Random hashing may distribute keys while making graph traversals expensive. Choose keys based on access patterns and locality, not just even row counts.

### 6.2 Leader and replica basics

In a leader-based database, writes are ordered by one leader and propagated to replicas.

- **Synchronous replication:** wait for specified replica acknowledgements; higher write latency, potentially stronger durability for acknowledged writes under the stated failure model.
- **Asynchronous replication:** acknowledge earlier; replicas can lag, and failover may lose recently acknowledged writes depending on the system’s guarantees.

A replica reading “no approval yet” just after an engineer approved a model is not a mysterious UI bug; it may be a consistency choice. Read-your-writes can be obtained through primary routing or replication-position-aware reads, depending on database support.

Replication is not backup: accidental deletions and corrupt application writes can replicate too.

### 6.3 Name the guarantee, not just “strong consistency”

| Guarantee | Meaning | Example |
|---|---|---|
| Linearizability | Each operation appears to take effect atomically between its invocation and completion, respecting real-time precedence | A current approved-baseline pointer |
| Serializability | Concurrent transactions have an effect equivalent to some serial ordering | Multiple related database updates preserve an invariant |
| Strict serializability | Serializable transactions also respect real-time ordering | A stronger transaction contract; must be verified for the actual system |
| Causal consistency | Causally related operations are observed in causal order | A reply should not appear before the comment it replies to |
| Eventual consistency | Under suitable conditions and no continuing updates, replicas converge | A delayed search index of already committed models |

**Serializability is not a synonym for linearizability.** PostgreSQL’s Serializable level concerns transaction anomalies and may require the application to retry aborted transactions.[9]

Different parts of one product can need different guarantees. Approval and permission changes need careful authoritative ordering; derived map tiles and search indexes can often lag if clearly versioned. Eventual consistency is not permission to serve cross-tenant data.

### 6.4 CAP from the actual impossibility

Imagine two replicas that cannot communicate. One receives a write changing the approved baseline. The other receives a read that must return.

The second replica cannot know whether the write happened. If it returns the old value, it can violate linearizability. If it refuses or waits until communication recovers, it gives up the theorem’s availability requirement for that operation.

**During a partition, a distributed system cannot guarantee both linearizable consistency and a successful response to every request at every non-failing node.** This is not a general “pick any two product features” menu. Partition tolerance is a condition the network may impose. CAP’s availability definition is not the same as an uptime percentage or a latency SLO.[23]

**Squid-like answer:** continue showing a clearly identified historical model if policy permits, but do not allow an isolated node to approve a conflicting current baseline. Different operations may deliberately degrade differently.

### 6.5 Consensus: agreeing which history is authoritative

Consensus lets replicas agree on a sequence of state transitions despite specified failures. Raft separates this into leader election, log replication, and safety rules.[7]

A conceptual flow:

1. A leader proposes a log entry.
2. Followers durably replicate it.
3. The protocol’s commit rules establish that the entry is committed.
4. Nodes apply committed entries to their state machines.
5. Elections and log-matching rules protect the committed history across leader changes.

With three voting replicas, a majority is two. A connected majority can usually continue despite one replica failure, under the algorithm’s timing and failure assumptions. Simply counting acknowledgements without correct terms, log rules, durable storage, and read protocols is not Raft.

The FLP result does **not** mean practical consensus is impossible. In a fully asynchronous model, deterministic consensus cannot guarantee termination in every admissible execution with even one crash failure. Practical systems preserve safety and obtain progress under additional timing/failure assumptions, such as eventual synchrony; timeouts do not prove failure.[23]

**Founding engineer judgement:** understand consensus well enough to use managed systems correctly. Do not implement your own database consensus protocol for an early product.

### 6.6 Quorum traps

For `N` replicas, read quorum `R` and write quorum `W` satisfying `R + W > N` guarantee a read/write set intersection in the simple fixed-replica model. They do **not**, alone, guarantee linearizability. Version selection, concurrent writers, failure recovery, read repair, membership changes, and partial writes still matter.

**Interview trap:** “We use quorum reads, therefore everything is strongly consistent.” Ask which protocol and which operations have the stated guarantee.

---

---

[← 5. What makes distributed systems hard?](../01-first-principles/05-what-makes-distributed-systems-hard.md) | [↑ Table of contents](../../README.md) | [7. Transactions, concurrent edits, and safe publication →](07-transactions-concurrent-edits-and-safe-publication.md)
