# 14. Observability, reliability, security, and operations

[← 13. A worked Squid-like system design](13-a-worked-squid-like-system-design.md) | [↑ Table of contents](../../README.md) | [15. Founding-engineer judgement: what not to overbuild →](15-founding-engineer-judgement-what-not-to-overbuild.md)

---

### 14.1 Measure the user’s outcome

Separate SLIs/SLOs:

- API acceptance latency/error rate.
- Queue wait and end-to-end completion latency by workload class.
- Successful validated studies, not merely HTTP 200 responses.
- Correctness/safety counters: stale publication blocked, invalid tool calls, cross-tenant violations.
- Freshness of derived views.

A system can have excellent API uptime while every study is stuck waiting for a solver. Conversely, a valid “no feasible option found” answer can be a successful product outcome.

### 14.2 Trace across asynchronous boundaries

Propagate `tenant_id`, request/run/step IDs, model version, attempt/generation, tool call ID, provider request ID, and solver job ID through the workflow.

A trace should expose time in queue, model inference, tools, database, solver, and human review separately. Human-review time belongs in business lead-time reporting but often needs separate treatment from compute-latency SLOs.

Log structured summaries and artifact references, not unrestricted confidential models or raw secrets. Control access and retention for prompts/tool outputs. A trace is not a substitute for an append-only business audit record.

Keep high-cardinality run/attempt IDs in logs and traces rather than turning each into an unbounded metrics label. Track outbox age, oldest eligible job, uncertain external outcomes, and orphan artifacts: a job can disappear from the queue while remaining unfinished in the business system.

### 14.3 Recovery objectives

**RPO:** how much data loss the business can tolerate. **RTO:** how long restoration can take. Ask these before advocating multi-region active-active.

Test backups and restores, not just backup creation. Replication, point-in-time recovery, object versioning, and retention solve different risks. Graceful shutdown, lease expiry, reconciliation, and compatible workflow deployments matter in ordinary releases as well as disasters.

Recovery must restore **authority**, not just rows. Restoring yesterday’s database while today’s workers still run can resurrect outbox events, lose idempotency records, or roll ownership generations backwards. Quiesce/fence old execution, verify referenced artifacts and keys, reconcile external jobs, and avoid generation reuse before reopening dispatch. A recovered database alone is not proof of a recovered distributed application.

### 14.4 Tenant isolation

Propagate tenant scope through database rows, object paths, queue payload validation, caches, vector retrieval, logs, and exports. Application checks are necessary; row-level security can add defence in depth.

Postgres documents that superusers and `BYPASSRLS` roles bypass row policies, and owners normally do unless forced. Therefore “we enabled RLS” is not sufficient if the application uses an inappropriate role or leaks tenant context through pooled connections.[19]

Some customers may require dedicated databases, buckets, keys, worker pools, regions, or deployments. Shared infrastructure versus isolated deployment is a product/compliance/cost trade-off, not a universally correct answer.

### 14.5 Load and failure testing

Test realistic distributions of file sizes, job durations, fan-out, tenant skew, and model tokens. An average-size synthetic request misses expensive outliers.

Include bursts, long soak tests, cold starts, provider throttling, database connection exhaustion, duplicate delivery, worker termination, lease expiry, out-of-order events, stale approval, permission revocation, and prompt injection.

Use an arrival-rate-driven test where appropriate: a closed-loop test client that waits for each response can reduce offered load when the system slows, concealing queue growth. Measure at the client boundary as well as internally.

---

---

[← 13. A worked Squid-like system design](13-a-worked-squid-like-system-design.md) | [↑ Table of contents](../../README.md) | [15. Founding-engineer judgement: what not to overbuild →](15-founding-engineer-judgement-what-not-to-overbuild.md)
