# 12. Data-intensive and scientific-computing design

[← 11. LLM inference, retrieval, security, and evaluation](11-llm-inference-retrieval-security-and-evaluation.md) | [↑ Table of contents](../../README.md) | [13. A worked Squid-like system design →](../05-applied-architecture/13-a-worked-squid-like-system-design.md)

---

### 12.1 Do not confuse user count with workload size

A small number of engineers can submit enormous model imports or fan out thousands of analyses. Relevant workload dimensions include assets/edges per model, file bytes, version frequency, change density, scenario count, solver time/memory, collaboration conflicts, and retention.

A single JSON expansion can consume much more RAM than the compressed file. Prefer streaming/chunked parsing when possible, bounded intermediate structures, resumable ingestion, and early rejection of invalid inputs. Preserve original source files and conversion provenance.

### 12.2 Choose storage by access pattern

| Store/pattern | Good fit | Important limitation |
|---|---|---|
| Relational database | Transactions, permissions, branch heads, job status, indexed asset queries | Large analytic scans can compete with interactive traffic |
| Object storage | Original exports, immutable snapshots, result artifacts | Not a relational transactional query engine |
| Columnar files/tables | Scan a few fields across many assets/scenarios; compression and vectorised processing | Not ideal for arbitrary tiny in-place transactional edits |
| Geospatial indexes | Viewport/bounding-box and geographic queries | Geographical proximity is not electrical connectivity |
| Search/vector index | Text and semantic retrieval | Usually derived; not the authoritative engineering state |
| Graph representation/database | Connectivity and traversal-heavy queries | Graph structure alone does not prove a graph database is necessary |

The vacancy’s explicit mention of relational databases, columnar formats, and object storage is a strong reason to practise this mixed-storage explanation.[2]

Start with measured query plans, appropriate composite indexes such as `(tenant_id, model_version_id, asset_id)`, pagination, pooling, and avoiding N+1 queries. Partitioning, read replicas, materialised projections, or a separate analytical engine are later tools, each with freshness and operational costs.

### 12.3 Reproducible study manifests

A proposed manifest contains:

```text
study_id, tenant_id, request_id
model_snapshot_id + content digest
scenario_id + assumption_set_id + units
source/conversion/schema versions
solver name/build + configuration + numerical tolerances
container/environment digest where applicable
random seed where applicable
LLM model identifier + prompt/tool schema versions
input/output artifact references + checksums
execution attempts + timings + validation status
approval and publication references
```

Not all providers expose an immutable underlying model build; record that limitation rather than pretending an API alias fully pins inference.

### 12.4 Parallelise scenarios before partitioning the physics

An electrical network is a coupled mathematical system. Splitting a graph into arbitrary chunks does not make the resulting physical calculations independent: boundary conditions and interactions still matter.

Independent study cases—different demand assumptions, reinforcement options, or contingencies—are usually a clearer horizontal-scaling unit than cutting one load-flow solve into microservices. If one huge solve is the bottleneck, investigate the solver’s supported parallel algorithms and memory requirements with domain expertise.

A scheduler should account for CPU, RAM, solver licences, software/runtime compatibility, and potentially data locality. Container count alone is not capacity. A job that uses native threads can oversubscribe a machine if each container assumes it owns every core.

### 12.5 Classify failures correctly

- **Infrastructure failure:** worker crash, preemption, timeout, unavailable dependency.
- **Input/data failure:** missing parameter, invalid units, inconsistent topology.
- **Numerical failure:** solver did not converge under its settings.
- **Engineering result:** solver completed and found a constraint violation.

The last is not a system failure; it may be the most important result. Non-convergence is not automatically evidence of an impossible network. Retrying an unchanged deterministic invalid input is usually wasteful; changing settings must be explicit, validated, and recorded.

Conversely, **numerical convergence does not prove engineering feasibility or compliance**. For example, MATPOWER documents that its default AC power-flow solve ignores several operating-limit classes unless handled separately. Validate the required thermal, voltage, generator, contingency and other conditions explicitly for the chosen study and engine.[26]

---

---

[← 11. LLM inference, retrieval, security, and evaluation](11-llm-inference-retrieval-security-and-evaluation.md) | [↑ Table of contents](../../README.md) | [13. A worked Squid-like system design →](../05-applied-architecture/13-a-worked-squid-like-system-design.md)
