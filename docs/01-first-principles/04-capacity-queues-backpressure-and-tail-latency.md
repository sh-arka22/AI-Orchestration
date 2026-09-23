# 4. Capacity, queues, backpressure, and tail latency

[← 3. Scaling, concurrency, parallelism, and distribution are different](03-scaling-concurrency-parallelism-and-distribution-are-different.md) | [↑ Table of contents](../../README.md) | [5. What makes distributed systems hard? →](05-what-makes-distributed-systems-hard.md)

---

### 4.1 Latency versus throughput

**Latency** is how long a unit of work takes. **Throughput** is how many units finish per unit time. Batching can improve throughput while making an individual request wait longer. More concurrent requests can increase useful throughput up to saturation, then mostly increase waiting.

Break end-to-end latency into:

\[
T=T_{queue}+T_{network}+T_{compute}+T_{storage}+T_{dependencies}
\]

A slow request does not prove CPU is the bottleneck. It might be waiting for a database connection, model quota, solver licence, remote response, or an overloaded queue.

### 4.2 Little’s law

**Intuition:** if ten people enter a café per minute and each stays for a long time, the café needs room for many people—even if entry is quick.

For a stable system over an appropriate measurement interval:

\[
L=\lambda W
\]

- `L`: average work in the system, including waiting.
- `λ`: average arrival/throughput rate in steady state.
- `W`: average time in the system.

**Hypothetical:** 20 agent requests per minute, each active for an average of 90 seconds, imply **30 requests in flight on average**. That is not 30 CPU cores: many requests may be waiting on external operations. It is also not a tail-capacity guarantee; bursts and long-running jobs need separate consideration.

### 4.3 Why latency deteriorates near saturation

An illustrative M/M/1 queue has Poisson arrivals, exponential service times, one server, and stable arrival rate `λ < μ`. Its mean response time is:

\[
W=\frac{1}{\mu-\lambda}
\]

With service capacity `μ = 100 requests/second`:

| Arrival rate | Utilisation | Mean response time in this toy model |
|---:|---:|---:|
| 50/s | 50% | 20 ms |
| 90/s | 90% | 100 ms |
| 99/s | 99% | 1 second |

Do not apply this exact formula to a production multi-worker agent system. The transferable lesson is that **headroom matters**, especially when service times vary. A server at near-maximum utilisation may have disastrous latency even before throughput stops increasing.

### 4.4 Queues buy time, not capacity

A queue separates accepting work from executing it and can absorb short bursts. If arrivals exceed sustainable completion capacity for long enough, backlog grows without bound unless work is rejected, deferred, cancelled, or capacity increases.

Useful controls:

- Bounded queues and explicit maximum queue age.
- Admission control before accepting expensive work.
- Per-tenant concurrency and spend limits.
- Separate interactive and batch queues.
- Backpressure upstream: slow acceptance instead of letting memory grow.
- Deadline-aware scheduling; do not run already-useless work.
- Fair scheduling so a large tenant cannot occupy every slot.

Google’s overload guidance emphasises prioritisation and throttling rather than treating every request as equally entitled to scarce resources.[21]

**Good answer:** “I would scale workers using queue age, arrival rate, service time, and resource saturation—not just API CPU. I would also cap downstream demand, because adding workers cannot create more provider quota or solver licences.”

### 4.5 Tail latency and fan-out

Percentiles describe a latency distribution. p50 is the median; p99 is a threshold met by 99% of observations. A good average can conceal a poor experience for a significant minority.

If one request waits for `n` independent calls, each with probability `p` of exceeding a given latency threshold:

\[
P(\text{at least one slow call})=1-(1-p)^n
\]

With a hypothetical 1% slow probability per call, waiting for 100 independent calls creates about a **63.4%** chance that at least one is slow. Correlated failures change the calculation; independence is an explicit simplifying assumption. Tail amplification is a central observation in Dean and Barroso’s *The Tail at Scale*.[6]

For an agent, latency follows the critical path of its dependency graph. Parallelising independent study cases helps, but the comparison still waits for required results. Do not add component p99s and pretend that yields an exact end-to-end p99.

**Mitigations:** bounded fan-out, smaller critical paths, separate resource pools, deadline budgets, progressive results, and optional-work degradation. Hedged requests can reduce latency for suitable idempotent reads, but consume spare capacity and can worsen overload. Do not casually hedge side-effecting tool calls.

---

---

[← 3. Scaling, concurrency, parallelism, and distribution are different](03-scaling-concurrency-parallelism-and-distribution-are-different.md) | [↑ Table of contents](../../README.md) | [5. What makes distributed systems hard? →](05-what-makes-distributed-systems-hard.md)
