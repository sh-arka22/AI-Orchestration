# 2. First principles: what is a system?

[← 1. What Squid actually does—and how that changes your preparation](01-what-squid-actually-does-and-how-that-changes-your-preparation.md) | [↑ Table of contents](../../README.md) | [3. Scaling, concurrency, parallelism, and distribution are different →](03-scaling-concurrency-parallelism-and-distribution-are-different.md)

---

### Intuition: a workshop

A workshop has materials, workers, a job list, tools, and a record of completed work. More customer orders can overwhelm different things: the receptionist, the workbench, a specialist machine, or the filing system. Hiring more receptionists does not fix a shortage of specialist machines.

A software system is similar:

- **State:** information that must persist—models, jobs, permissions, approvals.
- **Computation:** transformations—parsing, validation, inference, simulation.
- **Communication:** moving inputs, outputs, and commands.
- **Resources:** CPU, memory, disk I/O, network, GPU memory, API quota, money.
- **Rules:** things that must remain true despite concurrent work and failures.

A useful abstraction is a state transition:

\[
(s, c) \rightarrow (s', e)
\]

Here `s` is current state, `c` a command, `s′` the next state, and `e` emitted results/events. For an agent, the proposed command may be probabilistic. **Whether it is allowed to change authoritative state should not be.**

### Safety and liveness

- **Safety:** nothing invalid happens. Example: an unapproved scenario never becomes the approved baseline.
- **Liveness:** valid work eventually progresses. Example: a queued study eventually runs when capacity and dependencies are available.

These are different. Refusing every write is safe but useless. Accepting every write may be available but incorrect. Distributed-systems trade-offs often involve deciding what progress is permissible when knowledge is incomplete.[23]

### Start with invariants

Before drawing infrastructure, say what must not break:

1. Every study references a specific immutable model version.
2. A tenant cannot read or mutate another tenant’s data.
3. Duplicate delivery cannot publish the same logical decision twice.
4. Approval is bound to the exact model, assumptions, results, and proposal reviewed.
5. A stale worker cannot overwrite the result of a newer authorised attempt.
6. An invalid, missing, or non-converged study cannot silently become a successful comparison.

These are proposed design requirements. Confirm them with the interviewer rather than presenting them as Squid’s internal rules.

---

---

[← 1. What Squid actually does—and how that changes your preparation](01-what-squid-actually-does-and-how-that-changes-your-preparation.md) | [↑ Table of contents](../../README.md) | [3. Scaling, concurrency, parallelism, and distribution are different →](03-scaling-concurrency-parallelism-and-distribution-are-different.md)
