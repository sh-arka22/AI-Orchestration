# Quick revision sheet

[↑ Table of contents](../../README.md) | [← 18. Revision priorities and self-testing](../06-interview-and-revision/18-revision-priorities-and-self-testing.md)

---

# Squid interview: quick revision

Companion to the full study guide. These are proposed interview answers, not Squid’s disclosed architecture or confirmed interview questions.

## The one sentence to remember

**Pin the model; bound the work; persist progress; make retries safe; validate the results; approve the exact artifact.**

## Start every design with these questions

- What is the workload: model bytes/assets, study fan-out, duration, concurrent tenants?
- What must never be wrong: model identity, tenant isolation, approvals, publication?
- Which latency matters: API acceptance, first progress, complete validated study?
- What can lag or degrade? What must fail closed?
- What is constrained: CPU, RAM, database, token quota, solver licences, budget?

## Core concepts

| Concept | The answer you need |
|---|---|
| Scaling | Increase useful capacity while meeting correctness, latency, reliability and cost requirements. |
| Concurrency | Multiple tasks in progress; not necessarily simultaneous computation. |
| Parallelism | Computations executing at the same time. |
| Distribution | Components communicate across distinct processes/failure domains. |
| Little’s law | Average in-flight work = arrival rate × average time in the system, in a stable measurement regime. |
| Saturation | Near capacity, queueing and tail latency can grow sharply; keep measured headroom. |
| Backpressure | Stop accepting or producing work faster than downstream systems can sustain. |
| Partial failure | One dependency can fail while the rest of the system keeps running. |
| Timeout | Unknown outcome, not proof the remote action did not execute. |
| Replication | More copies of the same data. |
| Sharding | Different subsets of data have different owners. |
| Linearizability | Operations appear atomic and respect real-time precedence. |
| Serializability | Concurrent transactions have an effect equivalent to a serial execution. |
| CAP | Under a partition, you cannot guarantee both linearizability and successful responses everywhere. |
| Consensus | A protocol establishes one agreed history under specified failure assumptions. |
| Idempotency | Repeating the same logical operation does not create another intended effect. |
| Outbox | Commit database changes and dispatch intent together; publish later, duplicate-safely. |
| Lease | Temporary ownership that can expire without stopping the old process. |
| Fencing | The receiving resource rejects stale ownership generations atomically. |
| Durable workflow | Persist progression so work resumes across crashes, waits and deployments. |
| Agent replay | Reuse recorded outcomes; do not regenerate past LLM decisions during orchestration replay. |

## Three crash windows to draw

### A. Queue redelivery

```text
work done → worker crashes → ACK missing → redelivery
```

Handle duplicate delivery using stable identities, atomic state transitions, and idempotent effects.

### B. External action ambiguity

```text
external action succeeds → worker crashes → local success record missing
```

Local deduplication alone cannot solve this. Use external idempotency, a durable provider job ID and reconciliation, safely repeatable effects, or explicit uncertain-outcome handling.

### C. Database plus message

```text
database commits → process crashes → queue message never sent
```

Use transactional outbox or suitable change-data capture. Consumers still need deduplication.

## A minimal proposed architecture

```text
UI → authenticated API → Postgres metadata + immutable object storage
                             ↓
                   durable run state / outbox
                             ↓
                fair, bounded work scheduling
                     ↙                 ↘
             LLM/tool activities     solver workers
                     ↘                 ↙
                     result validation
                             ↓
                  review exact proposal
                             ↓
                 transactional publication
```

Begin with a modular application and separate workers. Split into more services only for demonstrated scaling, fault-containment, deployment or ownership needs.

## The agent-specific answer

The LLM proposes; deterministic code authorises and validates. A prompt is not a security boundary. Keep conversation memory separate from workflow state and authoritative engineering data. Record model/prompt/tool versions, approved inputs, external job IDs and outputs. Cap steps, tokens, wall time, cost, and tool permissions. Model fallbacks are behavioural changes requiring evaluation.

## The Squid-specific answer

A model version, its assumptions, solver configuration, and outputs must stay connected. Parallelise independent scenarios before trying to partition coupled physics. Distinguish invalid input, infrastructure failure, numerical non-convergence, and a valid finding of a constraint violation. A merge must pass semantic checks; text merging or CRDT convergence does not establish electrical validity. Approval must bind to the exact reviewed proposal and be rechecked for stale baseline/permissions.

## Common traps

- “Exactly once” without naming its boundary.
- “More workers” without checking database, model quotas or solver licences.
- “CAP means pick any two” without discussing partitions and definitions.
- “Serializable means the latest value everywhere.”
- “The lock expired, so the old worker stopped.”
- “Temperature zero guarantees reproducibility.”
- “S3 is eventually consistent” as a blanket claim.
- “Vector search is the source of truth for topology.”
- “The LLM judged it correct, so the engineering result is valid.”
- “A queue solves sustained overload.”
- “A graph-shaped problem requires a graph database.”
- “Replication is a backup.”

## Scaling and distributed learning (§19–31)

### The one sentence for this half

**Splitting work is free. Re-agreeing is not.**

### Diagnose the wall before choosing the tool

| Wall | Symptom | Tool |
|---|---|---|
| 1. Compute | Too slow; model fits | Data parallelism + ring all-reduce (§22) |
| 2. Memory | Does not fit (Adam = 16 B/param fp32) | FSDP / tensor / pipeline (§24) |
| 3. Data mobility | Data cannot legally move | Federated learning (§26) |
| 4. Divergent goals | Workers own their rewards | Multi-agent RL, CTDE (§27) |
| 5. Roles | Heterogeneous workflow | LLM orchestration (§29) |

### Cost model

`T(n) = α + β·n` (+ γ per byte reduced). Six orders of magnitude from DRAM to WAN.

- **Latency-bound** (`α ≫ βn`) → fewer, bigger messages.
- **Bandwidth-bound** (`βn ≫ α`) → fewer bytes: compress, sparsify, lower precision.
- Distribute only when compute per chunk ≫ `α + βn`.

### Primitives

| | Concatenate | Reduce |
|---|---|---|
| Onto one | Gather | Reduce |
| Onto all | All-Gather | **All-Reduce** |
| Sharded | (Scatter) | **Reduce-Scatter** |

**`All-Reduce = Reduce-Scatter + All-Gather`** — the most load-bearing identity in the guide.

Barrier costs `max_m T_m`, not the mean: synchronisation turns variance into latency. Overlap communication
with computation or accept a stall; `T_overlap = max(T_comp, T_comm)`.

### Ring all-reduce

```
T_ring = 2(M−1)α + 2·((M−1)/M)·N·β + ((M−1)/M)·N·γ
```

Bandwidth term → `2Nβ` as M → ∞: **independent of worker count**, and bandwidth-optimal. Latency term is
linear in M → use a tree for small payloads.

### Data-parallel SGD

*Provably identical* to sequential minibatch SGD (induction: identical `w_t` ⟹ all-reduced sum is the full
minibatch gradient ⟹ identical `w_{t+1}`). Hyperparameters transfer. Dies at the **critical batch size** — a
statistical limit, not a hardware one.

### Parameter server

Answers "what are the parameters at time t?" **by decree** (all-reduce answers it by construction).

| | Sync | Async |
|---|---|---|
| Utilisation | Low (stragglers) | High |
| Progress/step | Full | Degraded by staleness τ |
| Reproducible | Yes | No |

Staleness forces `η ≲ 1/(L(1+τ_max))`. **Statistical efficiency traded for hardware efficiency** — the same
trade as FedAvg's local steps K.

### Sharding

- Model parallel: solves memory, destroys utilisation (~1/P).
- Pipeline: bubble fraction `(P−1)/(m+P−1)`; more micro-batches, more activation memory.
- Tensor: per-layer collectives → latency-bound → **inside a node only**.
- FSDP: all-reduce decomposed, compute interleaved. Same bytes, `O(N/M)` memory.
- 3D parallelism maps the chattiest axis onto the fastest link.

### Decentralised / gossip

`‖x(t) − x̄‖ ≤ ρ^t·‖x(0) − x̄‖`, `ρ = max(|λ₂|,|λ_M|)`. **Spectral gap `1−ρ` is the only number that matters.**

| Topology | Gap | Rounds |
|---|---|---|
| Ring | `Θ(1/M²)` | `O(M²)` — bad |
| Hypercube | `Θ(1/log M)` | `O(log M)` |
| **Expander** | `Θ(1)` | `O(log M)` with `O(1)` degree |

"We removed the controller, therefore we scale" is **not an argument** until someone shows the topology.
Average consensus ≠ agreement consensus (Raft/Paxos).

### Federated

Communication ~10⁵× costlier → do more local work per round. FedAvg: K local steps, weighted average of
deltas. **Client drift** under non-IID data; error floor `∝ η²K²ζ²`. Fixes: SCAFFOLD (control variates),
FedProx (proximal term). Local data ≠ privacy — updates leak.

**Staleness (async PS), drift (FedAvg), disagreement (gossip) are one phenomenon**: local progress against a
global state you no longer share.

### Multi-agent RL

- **Non-stationarity:** `P_i` depends on `π_-i`, which is changing → not an MDP → every single-agent guarantee
  is void. CTDE restores stationarity by putting the centre back *at training time*.
- **Credit assignment:** gradient SNR degrades as `1/√N`. Fixes: difference rewards, COMA, QMIX monotonicity.

### Robustness

Mean has breakdown point `1/M` — **one** Byzantine worker can set it to any vector. Median / trimmed mean /
Krum / clipping tolerate `f < M/2`, at an irreducible cost `∝ (f/M)σ`. Robustness and non-IID data conflict.

### Agent orchestration

- Worker / service / support = plant / controller / observer.
- Policy constrains *before*; quality validates *after*. Operational state ≠ knowledge state.
- **MCP** = agent↔tool, pull-shaped, `N×M → N+M`. **A2A** = agent↔agent, push-shaped, plus opacity across
  trust boundaries.

### The two laws that are new

1. **`P_success = p^n`.** p=0.95 over 10 hops = 0.60. Validation gates are error-correcting codes. Prefer
   wide-and-shallow to deep-and-narrow.
2. **Amdahl still caps it.** 20% serial planning ⟹ ≤5× from any number of agents. Broadcast context is an
   `O(N²)` token bill — use a hub with summaries (reduce-scatter for prose).

### The one line

**Distributed ML solved "how do many workers agree on one number." Agentic AI is the same problem where the
number is a meaning, the channel is unreliable in a new way, and the workers can be confidently wrong — so
every classical technique transfers, but you must add verification, because correctness no longer comes free
from the arithmetic.**

### Traps for this half

- "More agents is more throughput." (Amdahl; critical batch size; `1/√N` credit assignment.)
- "Decentralised, therefore scalable." (Show the spectral gap.)
- "Async is strictly faster." (It trades statistical for hardware efficiency.)
- "We average across agents, so one bad agent is diluted." (Breakdown point `1/M`.)
- "Federated learning is private." (Updates leak; secure aggregation and DP cost accuracy.)
- "Data parallelism will fix our OOM." (Wall 2 needs sharding, not replication.)
- "The benchmark table shows 2× at 100 agents." (Recompute the per-unit column first.)

## What to measure

API latency; queue age; completion time by task class; CPU/RAM/licence utilisation; database connection waits and lock contention; model tokens and throttling; validated task success; cost per accepted result; retries; stale commits blocked; approval/version mismatches; cross-tenant access violations; restore success.

## Final rehearsal

Explain one complete design in this order:

**Requirements → invariants → assumptions → minimal architecture → capacity → failure cases → security → metrics → evolution triggers.**

Then answer: “What if a worker dies after submitting a solver job but before recording its ID?” If your design cannot account for the uncertain external outcome, it is not finished.
