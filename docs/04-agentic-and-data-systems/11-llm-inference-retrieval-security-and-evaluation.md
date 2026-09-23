# 11. LLM inference, retrieval, security, and evaluation

[← 10. Why agents need durable workflows](10-why-agents-need-durable-workflows.md) | [↑ Table of contents](../../README.md) | [12. Data-intensive and scientific-computing design →](12-data-intensive-and-scientific-computing-design.md)

---

### 11.1 Three scaling planes

Do not bundle these together:

- **Application/orchestration:** requests, sessions, workflow transitions.
- **LLM inference:** token production, context/KV memory, model quotas.
- **Scientific execution:** CPU/RAM/licence-constrained simulations and data processing.

Scaling one does not necessarily help another. A low-CPU API may still be blocked by tokens-per-minute or a solver licence pool.

### 11.2 Inference from the hardware up

For a conventional autoregressive transformer:

- **Prefill:** process input tokens, producing attention state for the prompt.
- **Decode:** generate output tokens sequentially, reusing cached attention keys/values.
- **KV cache:** memory that grows with active sequence lengths, layer count, KV head configuration, and precision.

A rough cache-memory model for a conventional full-attention layout is:

\[
M_{KV}\approx 2\times B\times S\times L\times H_{KV}\times d_{head}\times b
\]

`B` is active sequences, `S` tokens per sequence, `L` layers, `H_KV` KV heads, `d_head` head dimension, `b` bytes per element. Real engines, heterogeneous lengths, paging, sliding windows, and other architectures change the details.

More long-context users can exhaust memory before compute throughput is fully used. PagedAttention/vLLM addresses inefficient KV-memory management using paging-inspired techniques; the original paper supports the mechanism, not a guarantee of a particular performance improvement for your workload.[16]

**Continuous batching** admits and removes active sequences as generation progresses. Larger batches can improve throughput but affect per-request latency. **Data parallelism** replicates the model to serve different requests. **Tensor parallelism** splits operations/weights across devices, useful for fitting models but requiring frequent communication. **Pipeline parallelism** splits layers, adding scheduling and pipeline-efficiency considerations.

**Priority for this interview:** understand inference limits and hosted-provider rate control before memorising distributed-training algorithms. Self-hosting is justified by measured cost, quality, privacy, latency, or deployment requirements—not because using GPUs sounds advanced.

### 11.3 Token and cost accounting

Track requests/minute, tokens/minute, concurrent requests, prompt length, output length, and provider error rates. Use a gateway/admission layer to allocate budgets fairly across tenants and workflows.

For model calls `i`:

\[
C_{run}=\sum_i(t_{in,i}p_{in,i}+t_{out,i}p_{out,i})+C_{tools}+C_{compute}+C_{storage}
\]

Units must match the vendor’s pricing units. Prices, cache discounts, and quota accounting are provider-specific; verify them before budgeting.

Optimise **cost per successfully completed, accepted task**, not just cost per token. A smaller model that causes more retries or invalid studies can be more expensive overall. Model fallback is a behavioural change, so version and evaluate it.

Streaming improves time to first visible output. It does not necessarily reduce total work or completion time. Distinguish accepted-job latency, time to first token/progress, and time to validated result.

### 11.4 RAG is not the authoritative model database

For a power-system agent, use:

- Structured queries/tools for exact topology, asset IDs, versioned parameters, and constraints.
- Retrieval for manuals, study reports, explanations, and supporting evidence.
- The approved solver for numerical analysis.

A vector similarity result is not a substitute for a foreign-key relationship or an authoritative current rating. Hybrid retrieval and reranking can improve document selection, but correctness still requires source/version identifiers and permission checks.

Separate failure diagnosis:

1. Was the right source available and indexed?
2. Was it retrieved?
3. Was it current and authorised?
4. Was it interpreted correctly?
5. Did the correct tool run with valid inputs?
6. Was the output validated and communicated accurately?

### 11.5 Cache design

Different caches have different correctness boundaries:

- **Exact computation cache:** same complete simulation inputs and environment assumptions.
- **Prefix/KV cache:** reuse prompt computation, not necessarily output text.
- **Response cache:** same question/context under a declared equivalence rule.
- **Semantic cache:** approximate similarity, requiring greater caution.

A simulation cache key may include tenant, immutable model version/content digest, assumptions, scenario, solver build, algorithm, tolerances, and schema/conversion versions. Canonicalise inputs if using content hashes. A change in ambient configuration invalidates naive cache reuse.

A semantic cache should not casually answer “can this asset safely accept this load?” from a similar but different scenario. Permission and model-version boundaries apply to cache hits too.

Protect against stampedes: coordinate identical in-flight computations and use controlled expiry. Serving stale content is appropriate only when the product can safely label and tolerate it.

### 11.6 The model is not a security boundary

An imported document or tool result can contain adversarial instructions. OWASP describes indirect prompt injection through external content and recommends least privilege, constrained functions, human approval for privileged operations, and adversarial testing.[17]

Proposed controls:

- Treat external content and model output as untrusted data.
- Validate structured tool arguments against schemas and domain constraints.
- Derive tenant/principal identity from trusted authentication, not a model-supplied field.
- Enforce authorisation in every tool/backend operation.
- Separate read, propose, approve, and publish capabilities.
- Use short-lived scoped credentials, controlled egress, and sandboxed code execution.
- Keep secrets outside prompts and ordinary logs.
- Bind approval to exact artifacts; recheck authority when the delayed action executes.

A system prompt saying “do not leak data” is not equivalent to an access-control check. Also remember the product’s public boundary: this is planning software, not an agent writing to operational grid-control systems.[5]

### 11.7 Evaluate agents as systems

Do not measure only whether the final answer sounds good. Evaluate:

- Correct model/version and assumptions selected.
- Tool-call validity and permissions.
- Topology/parameter validation and solver status.
- Numerical agreement within declared tolerances.
- Completeness of required scenarios.
- Citation/lineage coverage.
- Unsafe action attempts and approval bypasses.
- Task success, cost, latency, and retry count.

Use deterministic assertions for exact properties, domain-approved benchmark cases, and human review for high-value engineering judgement. LLM-as-judge can help assess explanations but should not be the sole authority on electrical validity. The public role explicitly includes benchmarks and evaluation on customer tasks.[2]

Run evaluation trials in clean, isolated environments; leftovers, cached artifacts, or shared resource exhaustion can distort apparent quality. Score the final environment outcome and forbidden side effects, not only the transcript. Anthropic’s agent-evaluation guidance explicitly distinguishes outcomes from transcripts and explains why isolation matters.[27]

Use held-out networks/templates and keep closely related scenarios together when splitting evaluation data. Track performance by critical slice rather than letting a blended score hide unsafe publication or tenant leakage. Repeated success matters: “one of several runs was right” is not a production guarantee, especially without a reliable way to select that run.

---

---

[← 10. Why agents need durable workflows](10-why-agents-need-durable-workflows.md) | [↑ Table of contents](../../README.md) | [12. Data-intensive and scientific-computing design →](12-data-intensive-and-scientific-computing-design.md)
