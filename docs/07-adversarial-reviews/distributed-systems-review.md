# Adversarial review: distributed-systems correctness

[↑ Table of contents](../../README.md)

Independently produced by a second research pass (isolated citation ledger, cross-checked against the main guide's claims) to stress-test the first-principles material in `docs/01-first-principles` through `docs/03-messaging-reliability` with adversarial interview questions.

---

# Squid founding-engineer interview: distributed-systems adversarial review

## Scope and epistemic boundary

**Verified product context:** Squid describes a governed, versioned power-system model repository; scenario branches and merges; engineer approvals; and an AI-planned study executed by an approved analysis engine, with replayable results.[28] Its homepage is product evidence, **not evidence of its internal architecture or production scale**. Illustrated object counts and example studies are not capacity measurements.

**Independent, AI-assisted proposals:** The architecture choices and interview scenarios below are recommendations to challenge, not claims about Squid's stack. Default failure model: crash/recovery, delayed or lost communications, duplicate deliveries, reordered work, and partial outages. Neither database replication nor Raft by itself addresses malicious/Byzantine participants. Hypothetical workloads are explicitly labelled.

## Architecture critique: proposed starting point, not a stack inventory

- **Start with a relational control plane:** propose Postgres for tenants, model-version metadata, approvals, job state, publication pointers, idempotency records, and an outbox. Put large immutable imports/results in object storage; use columnar files for bulk analytical data. Parquet is a column-oriented file format, not a transactional database.[37] A modular application plus independently scaled worker pools is a reasonable starting proposal; a graph-shaped grid does not, alone, justify a graph database.
- **Choose explicit commit boundaries:** approval, dispatch permission, ownership transfer, cancellation, and result publication need independently specified invariants. Keep external solvers outside database transactions. Treat queue messages as prompts to examine durable state, not as the sole record of what must happen. The outbox solves the database/event dual-write gap, not arbitrary external effects.[12][36]
- **Separate artifacts from authority:** immutable objects and analytical files contain data; a transactionally published manifest identifies which complete set is authoritative. Search, graph projections, reports, and agent retrieval should advertise their source version/watermark rather than silently imply freshness. Single-key object-store atomicity does not create a transaction over all artifacts and metadata.[18]
- **Spend complexity where failure is costly:** prioritize tenant isolation, approval freshness, idempotent dispatch, stale-worker rejection, reconciliation, and recoverability. Add Kafka, specialist graph storage, cross-region writes, or sharding only against a measured bottleneck or explicit product requirement—not because the platform contains agents.
- **Questions that could overturn this proposal:** solver licensing and runtime constraints; deployment/data-residency requirements; model sizes and change rates; analytical access patterns; simultaneous editors; approval revocation semantics; tenant concentration; and recovery objectives. A requirement for isolated customer deployments, for example, may outweigh shared-platform efficiency.

## Question bank

### 1. “An engineer approves a plan. An agent edits its inputs before execution. What, exactly, was approved?”
- **Intuition:** approve a sealed package, not a moving folder.
- **Answer principles — proposal:** bind approval to tenant, immutable model/scenario revision, study-plan revision, relevant assumptions, and the permitted execution specification. Make dispatch a conditional state transition that checks that approval covers those exact inputs and the actor is authorized. Decide explicitly whether revocation prevents only new dispatches or also requires stopping in-flight work. The product's distinction between agent planning, solver execution, and engineer review motivates this boundary.[28]
- **Follow-ups:** Where is the linearization point? What if authorization changes concurrently? Is approval for one run or reusable? Which edits require reapproval?
- **Common traps:** checking a mutable `approved=true`; letting the agent both propose and authorize a consequential change; assuming an earlier authorization check remains valid indefinitely.

### 2. “A network partition isolates two regions. Can both accept authoritative baseline changes and always serve the latest baseline?”
- **Intuition:** an isolated region cannot know whether the other accepted a newer write.
- **Answer principles:** CAP's relevant consistency is a linearizable/atomic register—not the C in ACID. With partitions permitted, one cannot guarantee both that consistency and successful completion of every operation at nonfailed nodes. CAP availability is eventual completion, not a latency SLO.[23] **Proposal:** preserve a single authoritative baseline history; refuse or defer authoritative transitions where authority cannot be established. Separately offer explicitly versioned historical reads or tentative branches where the authorization/freshness contract permits them.
- **Follow-ups:** Can the majority side continue? What are users told about freshness? How are tentative edits reconciled? Why are immutable-version reads a different contract from “latest”?
- **Common traps:** “choose any two”; treating partition tolerance as a feature toggle; counting an error response as successful CAP availability; labelling the whole product CP or AP without discussing operations.

### 3. “If FLP says consensus is impossible, why use Raft? And why isn't `R + W > N` a proof of correctness?”
- **Intuition:** not hearing from a process does not reveal whether it is dead or merely slow.
- **Answer principles:** FLP rules out guaranteed termination of deterministic consensus in a fully asynchronous message-passing system permitting even one crash, while retaining the required safety properties; it does not say every execution fails.[29] Raft preserves safety without timing assumptions within its failure model; useful progress needs a communicating quorum and sufficiently stable timing/leadership. Randomized election timeouts are not a universal termination guarantee under adversarial delay.[30]
- **Quorum caveat:** `R + W > N` establishes intersection only for read/write sets drawn from the same fixed replica universe. It alone proves neither linearizability nor correct treatment of concurrent/partial writes. Ordering/version selection, durable protocol state, reads, and membership changes matter. Dynamo explicitly uses *sloppy* membership, so its quorums need not have that fixed-set intersection.[31]
- **Follow-ups:** Can a former leader serve linearizable reads? What must a new leader establish before replying? How do membership changes preserve safety?
- **Common traps:** equating consensus with leader election; assuming a majority acknowledgment makes every client read current; confusing crash tolerance with Byzantine tolerance.

### 4. “Two transactions both see enough tenant budget and independently reserve it. Both commit. Doesn't ACID prevent this?”
- **Intuition:** a consistent snapshot can still support two mutually incompatible decisions.
- **Answer principles:** identify the invariant and the actual isolation level. PostgreSQL Repeatable Read uses snapshot isolation and can admit serialization anomalies; Serializable can abort conflicting transactions, requiring a whole-transaction retry.[9] **Proposal:** for a simple budget, use a guarded update of a shared budget row plus the reservation in one transaction; for richer predicates, use correctly coordinated locks or serializable transactions. All mutation paths must follow the same invariant protocol.
- **Follow-ups:** What if there is no existing row to lock? How do transaction retries interact with caller idempotency? Can a report from a replica authorize a reservation?
- **Common traps:** “wrap it in a transaction”; assuming row locks automatically protect arbitrary predicates; retrying only the failed statement; performing irreversible solver calls inside a transaction that may abort.

### 5. “The job row commits, then the process dies before enqueueing. How does the study ever run?”
- **Intuition:** write the work and the obligation to announce it together.
- **Answer principles:** an outbox entry and the job transition commit in the same database transaction. A relay publishes committed entries and retries failures; publication followed by a crash before marking the entry sent can duplicate delivery.[12] **Proposal:** stable event IDs, per-aggregate sequence numbers where needed, and consumer inbox/deduplication recorded atomically with database-local effects. Monitor outbox age; reconcile accepted jobs with no progress. At smaller scale, a durable database job table may avoid a separate broker entirely.
- **Follow-ups:** Why not mark the event sent first? How do concurrent relays preserve required ordering? What happens when the broker is unavailable for hours?
- **Common traps:** calling outbox “exactly once”; relying on best-effort post-commit hooks; deleting deduplication state before the replay window closes; treating a dead-letter queue as successful completion.

### 6. “The solver accepted the request, but its response disappeared. Can you guarantee exactly one execution?”
- **Intuition:** a timeout reports uncertainty, not nonexecution.
- **Answer principles:** name the boundary: broker delivery, handler invocation, database effect, external execution, and billing are different guarantees. Queue redelivery can occur; Kafka's transactional guarantees do not automatically cover an external solver.[32][36] An upstream idempotency key/status lookup can make retry safe, subject to its documented scope and retention. Record caller intent with a tenant-scoped key and request fingerprint; reject reuse with different semantics. The deduplication record and a database-local effect must be atomic.[11]
- **Proposal when upstream lacks those facilities:** expose an `outcome_unknown` state, reconcile against solver records, and state the policy trade-off between possible duplicate execution and possible noncompletion. Publishing one accepted result does not prove the solver ran once.
- **Follow-ups:** What if a retry arrives after key expiry? Is a deliberate rerun the same intent? How are duplicate charges handled?
- **Common traps:** new keys on every attempt; claiming FIFO or producer deduplication makes external effects exactly once; checking a key and applying the effect in separate transactions.

### 7. “A worker pauses, its lease expires, and a replacement takes over. The old worker resumes. Who may publish?”
- **Intuition:** taking away the key does not stop someone already inside; the door to the protected resource must reject their old authority.
- **Answer principles:** lease expiry alone is insufficient. Chubby's sequencer design requires the recipient to validate lock generation and reject stale requests.[33] **Proposal:** allocate monotonically increasing ownership epochs at an authoritative handoff; require the epoch on every protected mutation. Atomically compare the current epoch and expected job state when publishing. A token checked only by the worker is not fencing.
- **Follow-ups:** Does the solver accept fencing, or only the result store? Does the sink validate current authority or merely reject tokens older than one it has seen? When is a replacement actually activated? What survives restore?
- **Common traps:** claiming highest-seen-token fencing immediately revokes old owners before the new epoch reaches the sink; treating heartbeats as proof of exclusive ownership; claiming result fencing prevents duplicate external computation.

### 8. “Cancellation and successful completion race; a duplicate success message arrives later. What should users see?”
- **Intuition:** cancellation is a contested state transition, not a magic undo.
- **Answer principles — proposal:** define a durable state machine and the permitted transitions. Serialize publication versus cancellation acceptance with a conditional update/transaction. If accepted cancellation wins, later output may be retained as an unaccepted artifact but cannot become authoritative; if publication wins, report that completion preceded cancellation. Distinguish `cancel_requested`, execution-stop confirmation, and terminal product status. Delayed messages must carry attempt identity/epoch and cannot regress state. Redelivery is a normal queue condition.[32]
- **Follow-ups:** What if the solver cannot stop? Can a user request a rerun while cancellation is pending? How do callbacks from an earlier attempt get rejected?
- **Common traps:** “last timestamp wins”; deleting the queue message to imply cancellation; compensating as though an already published external effect had never happened.

### 9. “The solver is slow, so every agent retries. Why does more availability logic cause an outage?”
- **Intuition:** retries consume the same scarce capacity as useful work.
- **Answer principles:** layered retries can multiply load; Google documents retry budgets and avoiding retries at multiple layers, while AWS explains why randomized jitter improves exponential backoff.[21][38] **Proposal:** classify retryable failures; preserve intent keys; enforce a total deadline, bounded attempts and retry budgets; use capped backoff with jitter; respect upstream throttling. Separate tenant admission, execution concurrency, and request-rate limits. Bound fan-out and queue growth before launching work.
- **Follow-ups:** Who owns retries across client, orchestrator, queue, and SDK? Do overload errors invite retries? How do poison jobs escape an infinite redelivery cycle?
- **Common traps:** unbounded queues; retrying validation failures; identical backoff schedules; circuit breakers without recovery probes; assuming a timeout cancels the remote computation.

### 10. “A result consists of metadata and many object/Parquet files. What makes it atomically visible?”
- **Intuition:** upload the pages first; publish the table of contents last.
- **Answer principles:** S3 provides strong read-after-write consistency and single-key atomicity, but not atomic updates across keys; none of that supplies a transaction with Postgres.[18] **Proposal:** write immutable, attempt-scoped artifacts, verify completeness/checksums/schema, then conditionally publish a manifest pointer in the control-plane transaction. Readers consume only committed manifests. Crash-before-publication creates collectible orphans, not a visible partial result. Coordinate garbage collection with active uploads and committed references.
- **Storage choice:** keep transactional metadata relational and bulk analytical measurements columnar; Parquet's documented purpose is efficient columnar storage, not concurrent row-level transactional updates.[37]
- **Follow-ups:** What happens if publication acknowledgment is lost? How are millions of tiny files compacted without changing the logical version? Which deletions require retention/legal-hold checks?
- **Common traps:** “S3 is eventually consistent”; treating LIST as a commit protocol; mutable shared output paths; assuming a checksum proves domain correctness.

### 11. “Two branches merge without text conflicts. Can you auto-approve the resulting power-system model?”
- **Intuition:** edits that do not overlap syntactically can still contradict each other physically.
- **Answer principles — proposal:** distinguish textual, structural, and domain-semantic conflicts. Preserve stable asset identities, units, source lineage, tombstones and merge parents; validate topology and parameters on the merged snapshot before approval. Squid explicitly describes topology/parameter checks and engineer review, rather than mere file versioning.[28] Define a study fingerprint over exact inputs, settings, solver/adapter versions and relevant execution environment. Record nondeterministic agent/tool outputs rather than assuming re-prompting recreates them.
- **Follow-ups:** One branch removes an asset and another attaches equipment to it—what happens? Does a solver upgrade invalidate a cache? Does reproducibility mean identical bits or a declared numerical tolerance?
- **Common traps:** last-writer-wins for engineering meaning; hashing raw bytes and claiming semantic equivalence; conflating provenance, replayability and deterministic numerical reproduction.

### 12. “The dashboard is green, but customers' studies never finish. What observability would reveal that?”
- **Intuition:** an accepted request is not a completed customer outcome.
- **Answer principles — proposal:** instrument accepted-to-terminal latency separately from queue wait, execution, publication, and human-review wait. Track oldest eligible job, outbox lag, unknown outcomes, orphan artifacts, stale-owner rejections, duplicate suppression, and reconciliation repairs. Correlate tenant, version, logical job, attempt and external-run identifiers. OpenTelemetry's messaging conventions use span links to connect producer and consumer work, including batches.[34] Keep a durable domain audit trail distinct from sampled diagnostic traces.
- **Follow-ups:** Which SLO excludes time deliberately awaiting approval? Can one delayed case hide behind healthy averages? How would you detect an accepted job absent from every queue?
- **Common traps:** monitoring only HTTP success and CPU; treating sampled traces as an audit log; using high-cardinality job IDs as unbounded metric labels; logging sensitive model data or signed URLs.

### 13. “A tenant identifier is in every SQL query. Is the platform isolated?”
- **Intuition:** tenant isolation is an end-to-end boundary, not a filter convention.
- **Answer principles — proposal:** derive tenant identity from trusted authorization, not arbitrary request payloads. Include it in ownership checks, composite keys, idempotency namespaces, object access, caches, analytical jobs, agent retrieval, and callbacks. Use database RLS as defense in depth with non-bypassing application roles; PostgreSQL table owners normally bypass RLS, and superuser/`BYPASSRLS` roles always bypass it.[19] Reset request-scoped context correctly with connection pools; test reads and writes through background paths. Bound each tenant's compute and queue consumption separately.
- **Follow-ups:** What happens when a pooled connection switches tenants? Can an object URL survive permission revocation? Can one tenant infer another's existence through deduplication or errors? When is dedicated deployment justified?
- **Common traps:** assuming RLS covers object storage; treating a bucket prefix as access control; sharing semantic-search caches across tenants; equating encryption at rest with authorization.

### 14. “Traffic doubles. Why might adding API servers and workers make throughput worse?”
- **Intuition:** capacity is constrained by the bottleneck resource, not the number of frontends.
- **Answer principles — proposal:** measure arrivals, study fan-out, service-time distribution, solver-license slots, CPU/RAM, database locks/connections, artifact I/O and upstream quotas separately. **Hypothetical calculation:** two studies/minute × thirty cases/study = one case/second; at thirty seconds per case, average demand is thirty busy solver slots before retries/headroom. Operating exactly at that average capacity leaves no margin for variability. Google explicitly treats resource saturation, overload protection and admission control as first-class concerns.[21]
- **Follow-ups:** How would p99 queue wait drive scaling? What if one tenant creates most work? Which data should be cached by immutable version? What measurement justifies a separate analytical store or shard?
- **Common traps:** sizing only from request rate; autoscaling into a fixed solver-license ceiling; adding workers until database contention increases; promising linear speedup for serial dependency chains.

### 15. “Restore yesterday's database while today's workers and object files still exist. What breaks?”
- **Intuition:** recovery must restore authority coherently, not merely resurrect rows.
- **Answer principles:** Postgres PITR requires a base backup and the necessary continuous WAL sequence; WAL does not back up configuration-file edits.[35] **Proposal:** define RPO/RTO per authoritative dataset, preserve referenced artifacts and keys, and reconcile cross-system state after restore. Lost idempotency records can re-enable old operations; resurrected outbox entries can replay them. Stop or fence pre-restore workers and external credentials before reopening dispatch. Avoid resetting ownership generations in a way stale workers can exploit.
- **Follow-ups:** How do you prove every restored manifest has its artifacts? What if the original primary returns? How is tenant/shard ownership transferred without dual writers? Which fault-injection test would falsify the design?
- **Common traps:** replication equals backup; database restore equals full-system restore; automatic failover without old-primary fencing; “we have backups” without timed restoration and invariant checks.

## Evaluation lens

A strong answer names **the invariant, authority, transaction/linearization boundary, failure window, recovery mechanism, and residual guarantee** before proposing infrastructure. Ask the candidate to walk through crashes immediately before and after every durable write or external call. Reject both unsafe simplicity and infrastructure-heavy answers without a concrete failure they solve.

## Retrieval notes

Primary URLs below were actually fetched and the quoted evidence checked against locally extracted text. Official Kafka documentation retrieved is version 4.1; it is cited for the stated transaction boundary, not as a claim about Squid or the latest Kafka release. The CAP source used is Gilbert and Lynch's *Perspectives on the CAP Theorem* (the URL filename is not its title).

Built-in search/extraction failed with backend 403s and a false private-address block; direct HTTPS retrieval succeeded. One AWS retry URL redirected to a contentless application shell, so the independently retrieved AWS jitter article and Google SRE chapter are used instead. An older CAP PDF had unusable text encoding and is not cited. An isolated scratch citation ledger was used; the shared ledger was not modified.

## Sources

[28] https://squid.energy — Squid — The grid has a repo now
    > "Models, scenarios and decisions stay connected, so engineers and agents validate, analyse and publish from one governed source."
[29] https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf — flp
    > "every protocol for this problem has the possibility of nontermination, even with only one faulty process."
[30] https://raft.github.io/raft.pdf — raft
    > "One of our requirements for Raft is that safety must not depend on timing:"
[31] https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf — dynamo
    > "To remedy this it does not enforce strict quorum membership and instead it uses a “sloppy quorum”"
[9] https://www.postgresql.org/docs/current/transaction-iso.html — PostgreSQL: Documentation: 18: 13.2. Transaction Isolation
    > "This level emulates serial transaction execution for all committed transactions; as if transactions had been executed one after another, serially, rather than concurrently."
[11] https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs — references-details-empty
    > "An important consideration is that the process that combines recording the idempotent token and all mutating operations related to servicing the request must meet the properties for an atomic, consistent, isolated, and durable (ACID) operation."
[12] https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html — Transactional outbox pattern - AWS Prescriptive Guidance
    > "When the flight table is updated, the outbox table is also updated in the same transaction."
[32] https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html — Amazon SQS at-least-once delivery - Amazon Simple Queue Service
    > "Design your applications to be idempotent (they should not be affected adversely when processing the same message more than once)."
[33] https://research.google.com/archive/chubby-osdi06.pdf — chubby
    > "The recipient server is expected to test whether the sequencer is still valid and has the appropriate mode; if not, it should reject the request."
[18] https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html — What is Amazon S3? - Amazon Simple Storage Service
    > "Updates to a single key are atomic."
[19] https://www.postgresql.org/docs/current/ddl-rowsecurity.html — PostgreSQL: Documentation: 18: 5.9. Row Security Policies
    > "Table owners normally bypass row security as well"
[34] https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans — Semantic conventions for messaging spans | OpenTelemetry
    > "For each message it accounts for, the “Process” or “Receive” span SHOULD link to the message’s creation context."
[21] https://sre.google/sre-book/handling-overload — Google SRE: Load Balancing with Client Side Throttling
    > "If multiple layers retried, we'd have a combinatorial explosion."
[35] https://www.postgresql.org/docs/current/continuous-archiving.html — PostgreSQL: Documentation: 18: 25.3. Continuous Archiving and Point-in-Time Recovery (PITR)
    > "you need a continuous sequence of archived WAL files that extends back at least as far as the start time of your backup."
[36] https://kafka.apache.org/41/design/design — Design | Apache Kafka
    > "When writing to an external system, the limitation is in the need to coordinate the consumer’s position with what is actually stored as output."
[37] https://parquet.apache.org/docs/overview — Overview | Parquet
    > "Apache Parquet is an open source, column-oriented data file format designed for efficient data storage and retrieval."
[38] https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter — Exponential Backoff And Jitter | AWS Architecture Blog
    > "The solution isn’t to remove backoff. It’s to add jitter."
[23] https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf — Brewer’s Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services
    > "In a network subject to communication failures, it is impossible for any web service to implement an atomic read/write shared memory that guarantees a response to every request."
