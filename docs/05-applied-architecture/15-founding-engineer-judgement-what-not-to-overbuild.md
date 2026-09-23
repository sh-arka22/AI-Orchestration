# 15. Founding-engineer judgement: what not to overbuild

[← 14. Observability, reliability, security, and operations](14-observability-reliability-security-and-operations.md) | [↑ Table of contents](../../README.md) | [16. Interview question bank with answer spines →](../06-interview-and-revision/16-interview-question-bank-with-answer-spines.md)

---

### A plausible initial decision set

These are proposals, not a prescribed stack:

- Managed relational database for transactional metadata.
- Object storage for large immutable artifacts.
- Modular application backend and separately scalable workers.
- A job queue or database-backed job table; a workflow engine when orchestration warrants it.
- Existing hosted models before running an inference fleet, unless constraints dictate otherwise.
- Infrastructure as code, CI, migrations, observability, backup/restore testing, and explicit tenant boundaries from the start.

### Decisions and revisit triggers

| Initial choice | Why | Revisit when |
|---|---|---|
| Modular monolith | Fast iteration, local transactions, lower operational cost | Independent scaling/deployment or ownership boundaries become real constraints |
| One regional authoritative write path | Simpler ordering and recovery | Proven availability/residency/latency requirements exceed it |
| Postgres plus object storage | Separates transactional state from large artifacts | Measured query/storage bottlenecks require specialised projections |
| Bounded single-agent planner | Easier evaluation, cost control, provenance | Independent subtasks demonstrably improve with specialised agents |
| Managed services | Buys operational reliability | Economics, capabilities, privacy, or portability justify ownership |

Do not adopt Kafka just because there are messages; ask whether you need retained ordered logs and multiple independently replaying consumers. Do not adopt a graph database just because the domain contains a graph. Do not adopt multi-region writes just because the product is important.

### Make your judgement falsifiable

Instead of “this will scale,” say:

> “I would measure queue age and service-time distributions. If a dedicated solver pool remains saturated while the metadata database has headroom, I would add compatible solver capacity within licence limits. If database locks dominate, more solver workers may make things worse; I would fix the transaction or ownership model first.”

That is a testable engineering argument with a clear bottleneck and alternative explanation.

---

---

[← 14. Observability, reliability, security, and operations](14-observability-reliability-security-and-operations.md) | [↑ Table of contents](../../README.md) | [16. Interview question bank with answer spines →](../06-interview-and-revision/16-interview-question-bank-with-answer-spines.md)
