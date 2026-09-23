# 1. What Squid actually does—and how that changes your preparation

[↑ Table of contents](../../README.md) | [2. First principles: what is a system? →](02-first-principles-what-is-a-system.md)

---

### Verified public evidence

Squid describes itself as **“The model repository for power-system planning.”** Its product connects models, scenarios, assumptions, evidence, and decisions. It imports formats from specialist power-system tools and surrounding GIS/spreadsheet data, preserves model history, and supports traceable scenarios and approvals.[1]

Its particularly useful framing is **“AI plans the study. The solver does the physics.”** The described agent workflow assembles an approved model and assumptions, prepares cases, invokes an analysis engine, compares outputs, and returns a replayable result for engineer review.[1]

The public engineering vacancy describes backend, frontend, cloud infrastructure, data-heavy workflows, versioning, collaboration, approvals, auditability, and AI evaluation. It mentions Python, TypeScript, React, Postgres, relational databases, columnar formats, and object storage as relevant experience; AWS and Terraform appear as job tags. These are **hiring signals, not proof of every technology deployed internally**.[2]

An important boundary: Squid’s security page says it operates at the **planning layer**, not the control layer, and never writes to OT, SCADA, or ADMS. Do not frame your interview design as an autonomous agent switching the live electricity grid.[5]

### My inference: where to concentrate

| Public product requirement | Likely engineering concept to practise |
|---|---|
| One governed model | Transactions, invariants, permissions, authoritative state |
| Model versions and scenario branches | Immutable snapshots, optimistic concurrency, semantic merge |
| Large technical datasets | Streaming ingestion, columnar storage, indexing, spatial queries |
| Agent-driven studies | Durable workflows, bounded fan-out, tool permissions |
| External analysis engines | Resource scheduling, licensing constraints, retries, reproducibility |
| Human review and publication | Approval binding, stale-result detection, auditability |
| Multiple utility customers | Tenant isolation, noisy-neighbour protection, data residency |

This makes **data-intensive application engineering and workflow reliability** a higher-priority preparation area than distributed model training. LLM inference is relevant, but it is not the whole product.

### A useful interview opening

> “I would separate the governed model and approval path from the expensive execution path. The first needs strong correctness and clear version ownership; the second needs durable asynchronous execution, bounded concurrency, and reproducible inputs. I would measure model size, study fan-out, completion times, and tenant isolation requirements before choosing how much infrastructure to distribute.”

---

---

[↑ Table of contents](../../README.md) | [2. First principles: what is a system? →](02-first-principles-what-is-a-system.md)
