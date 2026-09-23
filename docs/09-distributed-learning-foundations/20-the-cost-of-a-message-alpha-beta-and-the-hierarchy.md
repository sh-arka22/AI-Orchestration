# 20. The cost of a message: alpha, beta, and the hierarchy

[← 19. Why one machine is not enough](19-why-one-machine-is-not-enough-three-walls.md) | [↑ Table of contents](../../README.md) | [21. The primitives →](21-the-primitives-of-distributed-communication.md)

---

### The model

Sending `n` bytes from one machine to another costs, to a first approximation:

```
T(n) = α + β·n
```

- **α — latency.** Seconds per *message*, independent of size. Propagation delay, protocol overhead, kernel
  transitions, queueing at the NIC.
- **β — inverse bandwidth.** Seconds per *byte*, i.e. `1 / bandwidth`.

A third term, **γ** (seconds per byte of arithmetic), appears in reductions where the receiver must also
*combine* the data. It is usually negligible against β on a network, and never negligible on-chip.

### The hierarchy is the whole point

| Link | α (latency) | Bandwidth | β (s/byte) |
|---|---|---|---|
| DRAM, same chip | ~100 ns | ~2 TB/s | ~5e-13 |
| NVLink, GPU↔GPU in node | ~2 µs | ~450 GB/s | ~2e-12 |
| InfiniBand, node↔node | ~2 µs | ~25 GB/s | ~4e-11 |
| Datacenter Ethernet | ~50 µs | ~1.2 GB/s | ~8e-10 |
| WAN / consumer internet | ~30 ms | ~1 MB/s | ~1e-6 |

*(Order-of-magnitude figures for reasoning, not spec-sheet claims; exact numbers depend on generation,
topology, and protocol.)*

**Read the last column.** Between on-chip memory and a wide-area link there are roughly **six orders of
magnitude**. This single fact explains almost every surprising result in distributed training:

- Why tensor parallelism is confined *inside* a node (it needs the NVLink row).
- Why federated learning looks nothing like datacenter training (it lives on the WAN row, §26).
- Why "just add more machines" fails: you did not add machines, you **moved down the table**.

### The two regimes, and why they want opposite things

| | Latency-bound | Bandwidth-bound |
|---|---|---|
| Condition | `α ≫ β·n` (small messages) | `β·n ≫ α` (large messages) |
| Dominant cost | number of messages | number of bytes |
| Correct fix | **fewer, bigger** messages — batching, bucketing, fusion | **fewer bytes** — compression, sparsification, lower precision |
| Wrong fix | compressing payloads (they are already tiny) | batching (the bytes do not shrink) |

Every practical optimisation is one of these two, and applying the wrong one is worse than doing nothing
because it adds complexity for no gain. **Identify the regime before optimising.** This is the distributed
analogue of the rule in §4: measure the bottleneck first.

### The go/no-go test for distributing at all

Distribution pays only when the work per worker dwarfs the cost of coordinating it:

```
compute time per chunk  ≫  α + β·n
(FLOPs_chunk / FLOP_rate)   (comm cost per sync)
```

This is why a large convolutional network parallelises happily across hundreds of accelerators while a small
MLP cannot be meaningfully parallelised at all: for the MLP, one network round trip costs more than the entire
gradient computation. The ratio of these two quantities is the **computation-to-communication ratio**, and
PipeDream frames the whole case for pipeline parallelism in exactly those terms — data parallelism slows down
"when large models and/or limited network bandwidth induce high communication-to-computation ratios".[55]

### Worked example — is my all-reduce hidden?

A 1-billion-parameter model, fp16 gradients: `n = 2 GB`. Ring all-reduce (§22) moves about `2n` bytes per
worker. On InfiniBand at β ≈ 4e-11 s/B:

```
comm ≈ 2 × 2e9 × 4e-11 ≈ 0.16 s
```

If a training step's compute takes 0.5 s, the communication *can* be fully hidden behind backpropagation
(§21, overlapping). If the step takes 0.05 s — small model, big cluster — it cannot, and no scheduling trick
will save it; you must send fewer bytes (§23) or change the parallelism strategy (§24).

*(Illustrative: real β is lower than peak, and fp16 all-reduce may accumulate in fp32.)*

### The agentic translation — stated once, used throughout

For LLM agent systems, the same model applies with different units:

- **α** is a model round trip: queueing, prefill, time-to-first-token. Often **hundreds of milliseconds to
  seconds** — the WAN row of the table, or worse.
- **β·n** is the **token cost of the context you pass**: both wall-clock (decode time scales with tokens) and
  literal money (billed per token).

So an agent pipeline is almost always operating in the **high-α, high-β regime simultaneously** — the worst
quadrant. That is why §30 finds that the correct agentic optimisations are the same two: fewer hops (batch the
reasoning) and smaller context (summarise, do not forward transcripts).

### What to take from this section

1. `T(n) = α + β·n`, plus γ for reductions.
2. There are six orders of magnitude between the top and bottom of the interconnect hierarchy; a design is only
   correct *relative to a row*.
3. Latency-bound and bandwidth-bound demand opposite fixes. Diagnose the regime.
4. Distribute only when compute per chunk ≫ communication per sync.

---

[← 19. Why one machine is not enough](19-why-one-machine-is-not-enough-three-walls.md) | [↑ Table of contents](../../README.md) | [21. The primitives →](21-the-primitives-of-distributed-communication.md)
