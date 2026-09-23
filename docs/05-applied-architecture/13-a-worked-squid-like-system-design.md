# 13. A worked Squid-like system design

[← 12. Data-intensive and scientific-computing design](../04-agentic-and-data-systems/12-data-intensive-and-scientific-computing-design.md) | [↑ Table of contents](../../README.md) | [14. Observability, reliability, security, and operations →](14-observability-reliability-security-and-operations.md)

---

**Practice prompt:** “Design a platform that lets utility engineers import versioned grid models and ask an agent to compare reinforcement scenarios.”

### 13.1 Clarify before committing to architecture

Ask about:

- Model sizes and import frequency.
- Concurrent tenants/users and burst patterns.
- Typical/worst-case study duration and fan-out.
- Supported solvers, licences, and execution environments.
- Interactive response versus completion-time requirements.
- Availability, recovery point, and recovery time objectives.
- Collaboration/approval semantics and data residency.
- Which operations can be stale or fail closed.

Then state assumptions. Do not invent “millions of users” simply because this is a scaling interview.

### 13.2 Proposed architecture—not Squid’s disclosed stack

```text
                       Browser / engineering UI
                                  |
                         Authenticated API
                    permissions + admission control
                                  |
               +------------------+-------------------+
               |                                      |
       Postgres metadata                       Immutable object storage
  tenants, branch heads, manifests,             exports, snapshots,
  run state, approvals, audit, outbox            reports, solver artifacts
               |
        durable orchestration
               |
       fair scheduler / work queues
       +---------------+----------------+----------------+
       |               |                |                |
   ingestion       model/tool       CPU/RAM/licence    retrieval / derived
   validation      activities       aware solver       index workers
   workers         + LLM gateway    workers
       |               |                |
       +---------------+----------------+
                       |
              structured result validation
                       |
              engineer review of exact proposal
                       |
             transactional publication transition

  Cross-cutting: trace IDs, tenant isolation, secrets, quotas, audit,
  cancellation, retries, reconciliation, deployment/version compatibility.
```

This can begin as a modular backend plus separately scaled worker processes. It does not require every box to become a separately owned microservice.

### 13.3 Walk through one request

1. Authenticate the engineer; derive tenant context.
2. Resolve the chosen model version and permissions; pin the input manifest.
3. Enforce idempotency and reserve relevant budget/concurrency capacity.
4. Commit the run and dispatch intent transactionally; return a run ID.
5. Validate the model and ask the planner for a typed plan using allowed tools.
6. Validate that plan in code; expand bounded study tasks.
7. Schedule cases fairly onto compatible solver workers.
8. Each task writes immutable results; fenced state updates select authoritative completion.
9. Verify convergence, required coverage, units, and engineering constraints.
10. Produce a comparison whose numbers link to source artifacts.
11. Show a reviewable proposal; never silently treat it as an approved baseline.
12. On approval, recheck permissions and baseline concurrency, then atomically publish the exact reviewed version.
13. Emit derived updates via outbox; delayed search/map/UI projections remain explicitly versioned.

Use polling or server-sent events for progress when communication is predominantly server-to-client; use WebSockets when bidirectional live interaction is required. Disconnection should not define the lifecycle of an accepted durable job.

### 13.4 Hypothetical capacity estimate

Assume:

- 20 user requests/minute.
- Average request active duration: 90 seconds.
- Six model calls/request.
- 5,000 input and 700 output tokens/model call.
- Twelve independent solver cases/request.
- Each case occupies one solver slot for an average of 30 seconds.

Then:

| Quantity | Calculated value |
|---|---:|
| Mean in-flight user requests | 30 |
| Model calls/minute | 120 |
| Total input + output tokens/minute | 684,000 |
| Solver case arrival rate | 4/second |
| Mean simultaneously occupied solver slots | 120 |
| Nominal slots at 70% average utilisation | 172 |

The 172-slot figure is an illustrative capacity estimate, not an SLO guarantee. It assumes one case per slot and no other bottleneck; memory, licences, variance, burstiness, and scaling delay can dominate.

If a hypothetical provider counts these tokens against a 600,000-token/minute quota, that quota permits only about **17.5 requests/minute** under these assumptions. Adding web servers cannot make 20 requests/minute sustainable. Real providers differ in token accounting, cache treatment, and quota reservation.

### 13.5 Stress the design

| Failure | Expected behaviour |
|---|---|
| Browser disconnects | Run remains queryable by ID; cancellation is separate |
| Queue redelivers a case | Stable identity/claim rules prevent duplicate authoritative completion |
| Worker dies after solver submission | Reconcile using external job identity before resubmitting |
| Old worker resumes | Stale ownership generation cannot commit |
| Model branch changes while studies run | Studies keep their pinned snapshot; publication checks freshness |
| One case is invalid/non-convergent | Comparison reports incomplete/invalid coverage; no silent success |
| LLM provider returns throttling | Respect quota, backoff within budget, preserve workflow state |
| One tenant submits huge batch | Fairness and quotas protect other tenants |
| Metadata DB unavailable | Fail closed for approvals/writes; optionally serve permitted versioned reads |
| Object upload succeeds, DB commit fails | Staged orphan is reconciled/garbage-collected, not published |
| Search index lags | Authoritative reads remain correct; derived view declares version/lag |

---

---

[← 12. Data-intensive and scientific-computing design](../04-agentic-and-data-systems/12-data-intensive-and-scientific-computing-design.md) | [↑ Table of contents](../../README.md) | [14. Observability, reliability, security, and operations →](14-observability-reliability-security-and-operations.md)
