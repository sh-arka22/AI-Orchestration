# 3. Scaling, concurrency, parallelism, and distribution are different

[← 2. First principles: what is a system?](02-first-principles-what-is-a-system.md) | [↑ Table of contents](../../README.md) | [4. Capacity, queues, backpressure, and tail latency →](04-capacity-queues-backpressure-and-tail-latency.md)

---

### Four terms worth defining precisely

- **Concurrency:** several tasks are in progress during overlapping periods.
- **Parallelism:** several computations execute at the same instant.
- **Distribution:** components communicate across separate failure domains, usually machines/processes over a network.
- **Scalability:** useful capacity grows as resources or architecture change, without unacceptable cost or degradation.

An asynchronous Python service can handle many waiting HTTP requests concurrently on one thread. That does not mean it executes many CPU-heavy parsers in parallel. A CPU-heavy operation in an event loop can prevent unrelated requests from progressing. Threads may help I/O or native libraries that release the interpreter lock; CPU work may require processes, native parallelism, or separate workers. The details depend on the Python runtime and library, so avoid saying “Python can never do parallelism.”

### Vertical versus horizontal scaling

**Vertical:** give one machine more CPU/RAM/faster storage. Simpler; often the right early move; eventually hits hardware, cost, or failure-domain limits.

**Horizontal:** add machines or worker instances. Effective for independent work; introduces coordination, deployment, network, and state-management costs.

**Stateless services** are easier to replicate: any API instance can serve a request because durable state is elsewhere. Authentication/session data cannot live only in one process. Load balancing then distributes connections or requests across healthy instances; draining prevents deployments from abruptly terminating in-flight work.

But stateless API replicas do not remove state. They move it to a database, queue, object store, or workflow service. That component can become the shared bottleneck.

### Amdahl’s law: why ten machines may not give ten times the speed

If fraction `s` of a task is inherently serial and the rest parallelises ideally across `n` workers:

\[
S(n)=\frac{1}{s+(1-s)/n}
\]

For an illustrative 20% serial fraction, ten workers give about **3.57×** speed-up; even unlimited workers cannot exceed **5×**. Communication and coordination overhead make reality less favourable.

For Squid-like work, independent scenarios can run in parallel. Parsing one huge legacy export or solving one tightly coupled system may not split so easily. Ask: **“What is the independent unit of work?”**

### An economical order of attack

1. Measure the bottleneck.
2. Remove unnecessary work and improve algorithms.
3. Fix query plans, indexes, batching, and data representations.
4. Cache reproducible results where safe.
5. Use a larger instance if that is the simplest effective change.
6. Parallelise independent tasks.
7. Distribute state only when measured constraints justify it.

“Use Kubernetes and microservices” is not an explanation of what becomes faster.

---

---

[← 2. First principles: what is a system?](02-first-principles-what-is-a-system.md) | [↑ Table of contents](../../README.md) | [4. Capacity, queues, backpressure, and tail latency →](04-capacity-queues-backpressure-and-tail-latency.md)
