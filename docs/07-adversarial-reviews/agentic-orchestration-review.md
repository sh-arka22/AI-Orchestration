# Adversarial review: agentic orchestration and AI-serving correctness

[↑ Table of contents](../../README.md)

Independently produced companion review focused on `docs/04-agentic-and-data-systems`: durable execution, evaluation, retrieval, inference-serving economics, and failure scenarios for LLM-driven agents.

---

# Squid interview: agent orchestration, scientific jobs, and LLM serving

## Scope and evidence boundary

**Verified product context:** Squid describes a governed model repository with versioned baselines, scenario branches/merges, source lineage, and engineer review. Its analysis description is explicit: “AI plans the study. The solver does the physics.” The agent assembles approved inputs, invokes an analysis engine, compares outputs, and returns a replayable result.[28]

**Not verified:** Squid’s internal architecture, workflow engine, queue, inference provider, solver deployment topology, or workload sizes. Everything below labelled **proposal**, including Postgres/object storage/columnar files, is an interview design recommendation—not a claim about their implementation. Supplied hiring context emphasizes production applications, relational databases, columnar formats, and object storage; prioritize those and simulation scheduling over ML training.

Primary documentation was fetched directly and retained in `agentic-evidence/`. The source block contains verified excerpts. Numbering belongs to this document’s separate ledger, not the parent research ledger. Live documentation can change; the original vLLM article is historical evidence for the mechanism, not a current performance benchmark.

## 1. Start with authority, not with an agent framework

**First principle:** planning a computation, executing it, and approving its business meaning are different authorities. A convincing explanation must never substitute for a solver result or an engineer’s approval.

Anthropic distinguishes predefined workflows from agents that dynamically direct their own steps; it recommends increasing complexity only when it demonstrably helps.[14] **Proposal:** use an agent inside a controlled scientific workflow, not an agent with unrestricted control over the workflow:

```text
User request → permission-scoped retrieval → proposed structured study plan
 → deterministic validation / required approval → immutable study manifest
 → durable orchestration → resource-aware solver scheduler
 → versioned outputs → numerical/domain checks → engineer review
 → separately authorized publication
```

Keep three logical responsibilities separable; they need not start as separate microservices:

- **Control:** identities, scenario/version metadata, authorization, workflow state, approvals, scheduling policy.
- **Data:** original exports, immutable snapshots, inputs, logs, checkpoints, and result tables.
- **Execution:** short API/tool activities, isolated solver processes, and optional LLM-serving workers. A slow solver must not occupy a web request or starve interactive metadata APIs.

Expose narrow tools such as `get_model_snapshot`, `propose_scenario_patch`, `submit_study`, `get_study_status`, and `compare_results`. The server resolves identity and checks resource scope; a model-supplied tenant identifier is never authority. A typed JSON response is a parsing contract, **not** evidence of valid units, correct topology, authorization, or physical feasibility.

## 2. Make the study manifest the reproducibility boundary

**Proposal:** before execution, resolve moving aliases such as “approved baseline” into immutable identifiers. A manifest should bind:

| Area | What to pin or record |
|---|---|
| Network and data | Network commit; scenario patch/commit; source object digests; forecast/queue versions; mapping and schema versions; units and per-unit bases |
| Scientific method | Engine/version or build; solver settings; convergence tolerances; contingency definitions; initial conditions; seeds where applicable; adapter/container digest |
| Agent decisions | Provider and model identifier; prompt/template version; tool-schema and agent-code versions; retrieved object IDs; actual structured proposals and responses |
| Results and authority | Attempt IDs; artifact digests; diagnostics; validation-rules version; approver identity; approved manifest/result digest; publication target |

Distinguish **historical replay** (show recorded decisions/results), **workflow recovery** (resume a durable process), and **scientific recomputation** (run the same specified experiment again). Only the last exercises the solver again. Pinning versions supports reproducibility but is not, by itself, a contract for bitwise-identical LLM or numerical results. Define acceptable numerical tolerances and retain original outputs.

**Storage proposal aligned with the hiring emphasis:**

- **Postgres:** transactional identities, permissions, version DAG metadata, study/attempt states, idempotency records, review records, and artifact manifests. Use constraints and compare-and-swap/version checks for correctness.
- **Object storage:** immutable source exports, engine input bundles, large logs/checkpoints, and result files. Persist durable references rather than huge payloads in workflow history.
- **Columnar files, e.g. Parquet:** immutable per-study/scenario result tables for scanning asset/time/contingency columns. Include schema and unit metadata; avoid representing approvals or mutable job state as a collection of files.

A database and an object store do not become one transaction because the application writes to both. Upload complete immutable artifacts first, verify them, then transactionally expose a result manifest. Failed publication can leave unreferenced objects for delayed garbage collection; it must not expose half-written results. Likewise, a transactional outbox can bind a study-state change and dispatch intent, but its relay can still deliver duplicates: consumers need deduplication.

**Subtle distinction:** an idempotency key identifies one caller’s intended operation; a study fingerprint identifies equivalent scientific inputs for possible cache reuse. Two intentional reruns can have identical inputs and different operation IDs. AWS explicitly warns that identical request parameters need not mean duplicate intent.[11]

## 3. Durable execution does not make nondeterministic work deterministic

Temporal’s model requires workflow code to emit a compatible command sequence during replay; its documentation explicitly places API calls, LLM calls, and database queries in Activities outside the deterministic replay path.[39]

**Proposal:** let deterministic orchestration branch on *recorded* activity results. A completed and recorded LLM activity supplies its prior result on workflow replay; do not call the model again to reconstruct an old decision. Use workflow-aware timers/time APIs, not arbitrary wall-clock branching. Read mutable configuration through recorded activities or immutable workflow inputs.

Three failure classes require different answers:

1. **Replay incompatibility:** code emits commands inconsistent with existing history. Fix/version the orchestration code; retrying the LLM is irrelevant.
2. **Ambiguous external completion:** a solver job was submitted, but the worker died before recording the acknowledgement. An activity retry may repeat the external call. Durable history cannot atomically cover an unrelated scheduler.
3. **Domain failure:** invalid topology, nonconvergence, infeasible constraints, or denied authorization. Classify explicitly; do not spend resources blindly retrying an unchanged deterministic failure. Temporal supports non-retryable application errors.[41]

For ambiguous completion, use stable operation IDs, downstream idempotency where available, reconciliation by operation ID, and a persisted external job ID. AWS’s idempotent-API design ties caller identity and request ID to an atomic mutation and recommends rejecting the same key with different intent.[11] **If the external engine cannot deduplicate or be queried reliably, say so:** at-most-once physical submission is not guaranteed. Fence result publication, bound duplicate expenditure, or require reconciliation before resubmitting. An outbox alone does not close that external atomicity gap.

Code deployments are another source of replay incompatibility. Temporal supports pinning executions to a Worker Deployment Version; auto-upgrading executions still require replay-safe changes.[42] **Proposal:** replay representative histories in CI, pin/version long-running orchestration deliberately, and retain compatible workers until they drain. Workflow-code versioning and scientific-engine versioning are separate obligations.

## 4. Long-running simulations: recover jobs, not just Python functions

Temporal heartbeats can persist small progress details for the next attempt, but the application must implement checkpoint/resume logic; heartbeats are not snapshots of arbitrary solver memory.[25] Activity cancellation is delivered through heartbeats and can be ignored by the activity; it is not proof that a remote process has stopped.[40]

**Proposal:** choose the boundary to match the engine:

- If the engine is an external scheduler/service, submit a job, persist its ID, and await completion using authenticated callbacks or bounded polling activities plus durable timers. Reconcile missing callbacks and duplicate/out-of-order events.
- If the engine runs inside a worker, isolate its process, enforce resources, heartbeat, and checkpoint only at engine-supported safe boundaries. A wrapper’s “50% complete” message does not mean a crash can resume halfway through a Newton solve.
- If mid-solve checkpointing is unavailable, make the independently reproducible unit a scenario/contingency/time segment and restart that unit. A time segment is independent only when its boundary/initial state is correctly specified.

Track **workflow**, **logical study**, **external job**, and **attempt** separately. Distinguish `execution_succeeded` from `scientifically_valid`, and both from `approved` or `published`.

Use per-attempt timeouts, overall deadlines/retry budgets, and short failure-detection heartbeats for different purposes. A heartbeat demonstrates communication, not necessarily useful numerical progress: monitor iteration/progress stagnation separately. Never silently loosen tolerances on retry; changed solver settings create a new manifest or an explicit child experiment.

**Cancellation protocol:** record `cancel_requested`; issue engine cancellation; wait for acknowledgement or reconcile; keep uncertainty visible. Release scarce concurrency/license capacity only when the resource is genuinely free under the engine’s contract. A lease expiry is not proof of death. Use an attempt/generation fencing token to reject stale result publication; this protects the result record but cannot physically stop an unfenceable external process.

## 5. Scale independent studies before distributing one mathematical solve

**Proposal:** admit work using tenant budgets, queue age, deadline, memory/CPU requirements, engine compatibility, and license availability—not just queue length. Separate interactive queries from long simulations; limit scenario expansion before an agent creates a huge fan-out. Retry backoff, a retry budget, and admission control must work together during downstream failure.

**Illustrative calculation, not Squid data:** 6 incoming studies/minute × 20 minutes of mean execution requires 120 concurrent executions merely to match offered load. If licensing permits only 40 concurrent runs, the idealized ceiling is 2 completed studies/minute; more pods cannot fix the deficit. Variance, failures, and headroom make practical capacity worse. Queueing is a workload/resource issue, not an autoscaler setting.

A graph database or a sharded graph does not automatically create a distributed power-flow solver. MATPOWER’s AC formulation solves coupled nonlinear equations and its Newton method repeatedly forms and factorizes a Jacobian.[26] PETSc documents that memory bandwidth can saturate with only a fraction of available CPU cores.[46]

**Engineering implications, to validate against the approved engine:**

- Parallel independent scenarios/contingencies first; distinguish this outer parallelism from threading or MPI inside one solve.
- A geographic graph partition leaves electrical coupling across boundaries. It requires a mathematically valid decomposition/boundary-exchange method, not independent calculations followed by summing results.
- Profile sparse assembly, factorization, fill-in/memory, communication, imbalance, and serial work before proposing distributed linear algebra. More nodes may increase synchronization and transfer cost.
- Preserve time coupling where present: storage state, ramp constraints, or dynamic state make arbitrary time slices non-independent.
- Reuse symbolic sparsity analysis or warm starts only when the engine supports it and the relevant structure/assumptions remain valid. A topology edit can invalidate reuse.

A particularly useful interview distinction: **convergence is not security or compliance.** MATPOWER notes that its default AC power flow ignores several operating limits; a converged solution still needs the study’s required voltage, thermal, and other engineering checks.[26]

## 6. Prompt injection is an authorization problem as well as a model problem

OWASP explicitly includes indirect instructions from websites/files as prompt injection and requires downstream authorization rather than letting the LLM decide permission.[17][45]

**Proposal:** treat imported studies, spreadsheet cells, asset descriptions, retrieved documents, and tool outputs as untrusted data even when their source is an authorized utility. A trusted source can contain attacker-controlled text. Delimiters and another LLM guard can help detection, but neither is the security boundary.

- Scope retrieval **before** data enters the prompt. Prevent unauthorized snippets, metadata, and source citations from entering context, rather than attempting to redact them afterward.
- Enforce tenant/project/object authorization at every tool and artifact download. Use short-lived, scoped execution credentials; keep raw secrets and ambient cloud credentials out of model context.
- Prefer narrow tools over shell/SQL/URL super-tools. Restrict filesystem mounts and egress for parsers and solver workers; an exfiltration path can be a URL, report link, or output artifact, not only an API write.
- Separate proposal, execution, baseline merge, and publication privileges. Bind human approval to the exact manifest/result digest, action, and destination. Recheck current permission and expected baseline version at commit time.
- If data or the target baseline changes while an approval waits, preserve the original decision but require explicit revalidation/reapproval for the new content. Never let approval of one artifact authorize a mutated one.
- Audit the effective actor, resource, tool arguments, artifact versions, policy decision, and approval—not just the model’s explanation.

OWASP recommends granular functionality, least privilege, execution in the user’s context, and human approval for high-impact actions.[45] Human review is an additional control, not a cure for hidden data leakage or an unreadable bulk approval screen.

## 7. Evals should grade scientific outcomes and forbidden side effects

Anthropic distinguishes the final environment outcome from the agent’s transcript, recommends deterministic graders where possible, calibrated model/human graders where needed, and clean isolated trials.[27]

**Proposed Squid evaluation layers:**

1. **Data correctness:** reference resolution, source lineage, unit conversion, schema validation, topology/conflict handling, correct baseline selection.
2. **Plan correctness:** requested contingencies/conditions included, constraints interpreted correctly, unsupported assumptions surfaced, no unauthorized changes.
3. **Execution reliability:** worker death, duplicate delivery, lost acknowledgement, stale callback, cancellation race, exhausted licenses, and code upgrade during a paused run.
4. **Scientific result:** independently checked residual/convergence diagnostics plus operating-limit checks; known reference cases and expert-set tolerances. The agent cannot grade its own claim that “the grid is safe.”
5. **Explanation:** every numerical claim tied to an output artifact/column and version; missing cases disclosed; comparisons use compatible assumptions.
6. **Safety and usefulness:** zero unauthorized publication/data access in the tested cases; appropriate abstention; engineer correction rate, review effort, time to accepted study, and cost per accepted study.

Use production-like engine/adapter versions, isolated fixtures, held-out networks/templates, and time-based splits where appropriate. Split related scenarios together so near-identical baselines do not leak across evaluation sets. Model-based judges can assess clarity but should not replace deterministic numerical or authorization checks.

Report slice-level results, repeated trials, uncertainty, and failures—not one blended score that allows cheaper inference to hide more unsafe outcomes. Anthropic distinguishes `pass@k` (at least one success) from `pass^k` (all trials succeed).[27] **Illustration under independent identical 90% per-trial success:** at least one success in five is 99.999%, while all five succeed is only 59.049%. Correlated failures invalidate that simple independence calculation; do not multiply aggregate rates blindly. Also, “one of five is correct” is useless unless a reliable selector can identify it.

## 8. LLM serving: optimize the accepted study, not a tokens/second headline

**Proposal:** begin with an API if it meets data handling, latency, availability, and economic requirements. Self-host when measured demand, contractual requirements, or control needs justify GPUs and operational ownership. Training a model is not a prerequisite for a reliable application.

For transformer serving, separate prompt processing (**prefill**) from autoregressive **decode**. vLLM describes chunked prefill as mixing smaller prefill chunks with decode work, balancing typically compute-bound prefill and memory-bound decode; its tuning documentation explicitly describes latency/throughput trade-offs.[48]

PagedAttention manages KV cache in non-contiguous blocks, reducing allocation waste and supporting sharing; it does not remove the need to store useful attention state or perform inference work.[43] Prefix caching reuses computed KV blocks for matching prefixes, not validated scientific conclusions.[44]

**Illustrative conventional KV sizing:** `2 × layers × KV heads × head dimension × bytes/value × cached tokens`, summed over active sequences. With 32 layers, 8 KV heads, dimension 128, and 2-byte values, this is 128 KiB/token; 10,000 cached tokens occupy about 1.22 GiB **before** weights, workspaces, allocation overhead, or other requests. This model excludes architecture-specific alternatives, sharding, cache compression, and sharing. It explains why a model that “fits” can still fail under long-context concurrency.

**Serving design implications:**

- Measure queue delay, time to first token, inter-token latency, end-to-end *structured tool decision* latency, prompt/output distributions, KV pressure, preemptions, and cost per accepted study. Streaming a partial plan does not authorize executing it.
- Use batching and chunked prefill against explicit interactive SLOs; protect short tasks from large prompts and background work. Autoscale from workload and queue signals, not GPU utilization alone. Warmup/model loading affects responsiveness.
- Prefer replicas when the model fits and the goal is request throughput; use tensor/pipeline parallelism when memory or measured latency/throughput calls for it. vLLM warns that efficient tensor parallelism needs fast communication; synchronization is not free.[47][48]
- Route validated easy tasks to smaller models and reserve expensive reasoning for cases where evals justify it. Bound loops, parallel branches, retries, context, and generated tokens. Whole-study cost includes unsuccessful LLM calls, solver time, licenses, idle capacity, storage, and human correction—not just the final response.
- Keep semantic result caching separate from KV caching. Result reuse requires the right input/engine/settings fingerprint and current access checks. vLLM supports prefix-cache salting for trust-group isolation; enforce isolation at the trusted service boundary, not by accepting an attacker’s claimed tenant salt.[44]

## Ten interview scenarios

### Scenario 1 — “The solver started, but submit timed out. Do you retry?”
**Reasoning:** the outcome is unknown, not necessarily failed. Reconcile by the original operation ID; return the already-created job when found. Use an idempotent downstream create or a scheduler uniqueness contract. A different payload under the same key is rejected; a deliberate rerun receives a new intent ID.[11]

**Verification:** kill the adapter after external job creation but before acknowledgement; deliver duplicates concurrently. Demonstrate one logical study and one accepted result. If the engine cannot deduplicate, state the possible duplicate physical work rather than claiming exactly-once execution.

### Scenario 2 — “After a deploy, the agent makes a different plan during replay.”
**Reasoning:** an LLM call or mutable read leaked into deterministic workflow logic, or workflow commands changed incompatibly. Record the nondeterministic decision as an activity result; replay consumes it. Pin/version workflow code or make an explicitly replay-safe migration.[39][42]

**Verification:** recover the same recorded history on the replacement worker without invoking a fresh planning call for completed steps. If a new model should reconsider the study, start a new versioned planning step/run—not a disguised replay.

### Scenario 3 — “A three-hour study loses its worker; cancellation arrives during recovery.”
**Reasoning:** first determine whether the remote solver is alive. Reattach or reconcile before restarting. Resume only from a real engine checkpoint; otherwise restart the smallest valid work unit. Track cancellation request separately from confirmed termination; fence stale attempt results.[40][25]

**Verification:** test worker death, scheduler partition, lost cancel acknowledgement, and an old worker returning late. A surviving orphan must not publish over the current attempt, and scarce capacity must not be falsely marked free.

### Scenario 4 — “The approved network changes while a study waits for engineer approval.”
**Reasoning:** the old result remains valid evidence about its pinned input, not evidence about the new baseline. Display its relationship to current data, compute the domain-aware diff, and choose revalidation/rerun explicitly. Use compare-and-swap on the target baseline/publication state and bind approval to digests.

**Verification:** concurrently merge another scenario, mutate a proposed artifact, and revoke the reviewer’s permission. Publication should fail safely without deleting the historical study. Unrelated changes may permit reuse only under an explicit, validated dependency policy—not an LLM assertion.

### Scenario 5 — “An imported report tells the agent to upload all grid models to a URL.”
**Reasoning:** treat it as source text, not delegated authority. Enforce scoped retrieval, narrow tools, destination restrictions, and downstream authorization. A model may still produce a malicious tool call, so the service must reject it.[17][45]

**Verification:** place the payload in a retrieved PDF/spreadsheet/tool response; test exfiltration through URL fetches, rendered links, and generated artifacts. Test the boundary even when the model ignores its system prompt. Do not measure success solely by whether the chatbot refuses in prose.

### Scenario 6 — “One utility launches a huge scenario fan-out and everyone becomes slow.”
**Reasoning:** reject or stage unbounded expansion; apply tenant fair sharing, cost/concurrency quotas, resource classes, and separate interactive queues. Check license seats and memory before adding workers. Batch common immutable input staging without sharing unauthorized results.

**Verification:** load-test mixed short/long jobs, injected retries, and a saturated license pool. Measure queue-age percentiles, per-tenant accepted-study latency, resource utilization, and retry amplification. State overload behavior: defer, reject with a retry window, or negotiate the study budget.

### Scenario 7 — “Why not shard the electrical network across 100 services?”
**Reasoning:** storage locality is not mathematical independence. Explain boundary coupling, sparse Jacobian/factorization costs, and communication. Start by distributing independent studies; profile one approved-engine solve before considering a supported distributed algorithm.[26][46]

**Verification:** compare wall time, memory, communication time, convergence, and result tolerances across resource counts. Include a topology-changing contingency and any time-coupled study. Never promise linear speedup from graph partition count.

### Scenario 8 — “A cheaper model scores similarly. Can we replace the current model?”
**Reasoning:** compare the whole versioned application: model, prompt, retrieval, tools, budget, and solver integration. Gate on critical domain/security slices and actual outcomes; compare cost and review burden only among acceptable candidates. Avoid brittle grading of one prescribed tool sequence when another safe sequence is valid.[27]

**Verification:** repeated isolated trials, adversarial/ambiguous cases, historical failure regressions, and shadow execution with publication disabled. Retain rollback routing. Report whether apparent savings disappear through extra retries or engineer corrections.

### Scenario 9 — “GPU utilization is high, but first-token latency and study latency are terrible.”
**Reasoning:** split queueing, prefill, decode, parsing, tool waits, and solver scheduling. Investigate long contexts, KV exhaustion/recomputation, and batch interference. Tune chunked prefill and admission limits; consider replicas before increasing model parallelism.[48]

**Verification:** replay the real prompt/output-length mix and burst pattern, not only fixed synthetic prompts. Track tail latency and cost at a fixed acceptable-quality target. If solver waiting dominates the study, faster token generation may not improve the user’s critical path.

### Scenario 10 — “We have matching cached results, but the data is another tenant’s—or access was revoked.”
**Reasoning:** equality of inputs/cache keys is not permission. Authenticate and authorize every read, manifest lookup, and download; isolate trust groups, including inference-prefix caches. A scientific cache hit may avoid a solve but must still create an auditable study/reuse record and satisfy review policy.[44][45]

**Verification:** same-prefix cross-tenant requests, revoked membership, guessed artifact IDs, stale signed links, and timing probes. Also perturb engine version, tolerances, and source-data version: each should invalidate reuse where it changes the experiment’s meaning.

## Closing interview position

“I would first make every result attributable to an immutable model, method, and authorized decision. Then I would make submission and recovery safe under ambiguous failures, and schedule independent studies against real resource constraints. I would keep AI inside those boundaries and use measured scientific correctness, engineer effort, latency, and cost to decide where more autonomy or inference infrastructure is worthwhile.”

## Sources

[39] https://docs.temporal.io/workflow-definition — Temporal Workflow Definition | Temporal Documentation
    > "Workflow code must be deterministic to support replay."
    > "To handle non-deterministic operations like API calls, LLM/AI invocations, database queries, and other external interactions, put them in Activities."
[40] https://docs.temporal.io/activity-execution — Activity Execution | Temporal Documentation
    > "Activities must heartbeat to receive cancellations from a Temporal Service."
[41] https://docs.temporal.io/develop/python/failure-detection — Error handling - Python SDK | Temporal Documentation
    > "Some failures are permanent and won't resolve through retries."
[42] https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning — Worker Versioning | Temporal Documentation
    > "For pinned Workflow Types, each execution runs entirely on the Worker Deployment Version where it started."
[11] https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs — references-details-empty
    > "At Amazon, our preferred approach is to incorporate a unique caller-provided client request identifier into our API contract."
    > "the process that combines recording the idempotent token and all mutating operations related to servicing the request must meet the properties for an atomic, consistent, isolated, and durable (ACID) operation."
[14] https://www.anthropic.com/engineering/building-effective-agents — Building Effective AI Agents \ Anthropic
    > "Workflows are systems where LLMs and tools are orchestrated through predefined code paths."
[27] https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — Demystifying evals for AI agents \ Anthropic
    > "Each trial should be “isolated” by starting from a clean environment."
    > "The outcome is the final state in the environment at the end of the trial."
[43] https://blog.vllm.ai/2023/06/20/vllm.html — vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention | vLLM Blog
    > "PagedAttention partitions the KV cache of each sequence into blocks, each block containing the keys and values for a fixed number of tokens."
[44] https://docs.vllm.ai/en/latest/design/prefix_caching — Automatic Prefix Caching - vLLM
    > "cache salts to isolate caches in multi-tenant environments."
[17] https://genai.owasp.org/llmrisk/llm01-prompt-injection — LLM01:2025 Prompt Injection - OWASP Gen AI Security Project
    > "Indirect prompt injections occur when an LLM accepts input from external sources, such as websites or files."
[45] https://genai.owasp.org/llmrisk/llm06-sensitive-information-disclosure — LLM06:2025 Excessive Agency - OWASP Gen AI Security Project
    > "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed or not."
[26] https://matpower.app/manual/matpower/ACPowerFlow.html — AC Power Flow
    > "By default, the AC power ﬂow solvers simply solve the problem described above, ignoring any generator limits, branch ﬂow limits, voltage magnitude limits, etc."
    > "Each Newton step involves computing the mismatch"
[46] https://petsc.org/release/manual/performance — Hints for Performance Tuning — PETSc 3.25.5 documentation
    > "only a fraction of the total number of CPU cores is required to saturate the memory channels."
[28] https://squid.energy — Squid — The grid has a repo now
    > "AI plans the study. The solver does the physics."
[47] https://docs.vllm.ai/en/stable/serving/parallelism_scaling — Parallelism and Scaling - vLLM
    > "Efficient tensor parallelism requires fast internode communication, preferably through high-speed network adapters such as InfiniBand."
[48] https://docs.vllm.ai/en/stable/configuration/optimization — Optimization and Tuning - vLLM
    > "Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests."
[25] https://docs.temporal.io/design-patterns/long-running-activity — Long-Running Activity - Tracking Progress and Handling Cancellation with Heartbeats | Temporal Documentation
    > "You must implement checkpointing logic and state management."
    > "You must handle partial reprocessing of the last checkpoint (idempotency)."
