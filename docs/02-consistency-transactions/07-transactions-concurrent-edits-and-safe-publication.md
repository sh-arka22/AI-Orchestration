# 7. Transactions, concurrent edits, and safe publication

[← 6. Replication, partitioning, consistency, CAP, and consensus](06-replication-partitioning-consistency-cap-and-consensus.md) | [↑ Table of contents](../../README.md) | [8. Queues, delivery guarantees, retries, and idempotency →](../03-messaging-reliability/08-queues-delivery-guarantees-retries-and-idempotency.md)

---

### 7.1 ACID in practical language

- **Atomicity:** the transaction’s database writes happen together or not at all.
- **Consistency:** the application/database preserve defined invariants; it does not automatically mean replica consistency.
- **Isolation:** the allowed interactions between concurrent transactions.
- **Durability:** committed changes survive the failures covered by the configured system’s contract.

A transaction does not automatically include an email, an object-store upload, or an external solver call. A database rollback cannot un-send a message.

### 7.2 Common anomalies

- **Lost update:** two editors read the same old value, then one overwrites the other’s change.
- **Non-repeatable read:** rereading a row sees a concurrent committed change.
- **Read skew:** related reads observe an inconsistent mixture of states.
- **Write skew:** concurrent transactions each satisfy an invariant in their snapshot, modify different rows, and jointly violate it.

PostgreSQL Read Committed uses a fresh snapshot for each statement. Repeatable Read gives a stable transaction snapshot but does not rule out every serialisation anomaly. Serializable provides stronger anomaly prevention, with transactions sometimes rejected and requiring retry.[9]

**Example of write skew:** two engineers each see another available approver and separately deactivate themselves. If the invariant requires at least one active approver, row-level protection on only their own rows is insufficient. Lock a shared governing row, enforce a suitable database constraint, or use a correct serializable transaction with retry.

### 7.3 Optimistic concurrency control

**Intuition:** “Apply my change only if the document is still the version I reviewed.”

Illustrative SQL, not production-ready application code:

```sql
UPDATE model_branches
SET head_version_id = :candidate_version,
    revision = revision + 1
WHERE tenant_id = :tenant
  AND branch_id = :branch
  AND head_version_id = :reviewed_base
  AND revision = :expected_revision;
```

If no row changes, another operation moved the branch. Return a conflict and revalidate/merge; do not silently overwrite. Include an always-increasing revision if a pointer can return to an earlier value, avoiding an ABA-style ambiguity.

Choose optimistic concurrency when conflicts are uncommon and edits take human time. Use short pessimistic transactions or locks when contention is high or you must coordinate a small critical section. Do not hold a database lock while waiting for an LLM, solver, or human review.

### 7.4 Git-like models: useful analogy, incomplete solution

A power-system model can have immutable snapshots and branches. Two proposals can start from the same baseline without modifying it. But a textual merge is not necessarily a valid engineering merge.

Two changes may touch different fields yet violate a shared electrical constraint. A semantic merge should check asset identity, topology, units, parameter bounds, and whatever domain validation is required. A CRDT can make supported operations converge; convergence alone does not establish physical validity.

A proposal should record:

```text
proposal_id, tenant_id, base_model_version, candidate_model_version
assumption_set_id, validation_report_id, study_run_ids
reviewed_artifact_digest, reviewer_id, approval_policy_version
```

Approval applies to that exact proposal. If the baseline, assumptions, relevant results, or permissions change, reassess whether approval is still valid. Do not assume yesterday’s approval authorises today’s regenerated LLM output.

### 7.5 Object storage plus a transactional manifest

Proposed pattern:

1. Upload immutable candidate objects to staged keys.
2. Validate checksums, schema, provenance, and completeness.
3. In one database transaction, insert the committed model manifest and change the relevant pointer after concurrency checks.
4. Make only committed manifests visible to readers.
5. Garbage-collect unreferenced staged objects after an appropriate retention period.

This avoids pretending object uploads and database commits are one atomic transaction. A crash may leave an orphan, which is easier to reconcile than a published model pointing to missing files.

Do not repeat the outdated claim that all object storage is eventually consistent: Amazon S3 documents strong read-after-write consistency and atomic updates to a single key. That still does not make a group of independent object writes plus a Postgres update one cross-system transaction.[18]

---

---

[← 6. Replication, partitioning, consistency, CAP, and consensus](06-replication-partitioning-consistency-cap-and-consensus.md) | [↑ Table of contents](../../README.md) | [8. Queues, delivery guarantees, retries, and idempotency →](../03-messaging-reliability/08-queues-delivery-guarantees-retries-and-idempotency.md)
