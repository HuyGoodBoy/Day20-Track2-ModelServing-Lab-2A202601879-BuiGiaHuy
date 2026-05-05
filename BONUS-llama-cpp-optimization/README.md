# BONUS — llama.cpp Optimization

Build llama.cpp from source for **your** hardware and measure how much faster you can make it. This is the part of the lab where weaker laptops have an advantage: every flag you flip is a measurable speedup, because the unoptimized baseline is more pessimistic.

> **Time budget:** 60–120 minutes. The build alone is 5–15 minutes depending on CPU. Each benchmark sweep is 5–10 minutes. You don't need to do every sweep — pick the ones that match your hardware.

## Path overview

```
BONUS-llama-cpp-optimization/
├── 01-build-from-source.md          ← step-by-step build per OS/backend
├── benchmarks/
│   ├── thread-sweep.py              ← -t threads vs tokens/sec
│   ├── quant-sweep.py               ← Q2_K → Q8_0 latency vs RAM
│   ├── ctx-len-sweep.py             ← context length vs prefill cost
│   ├── batch-size-sweep.py          ← --batch-size and --ubatch-size
│   └── gpu-offload-sweep.py         ← -ngl 0,8,16,...,99 (CUDA/Metal/Vulkan)
└── CHALLENGES.md                    ← open-ended: pick one and go deep
```

## Why this matters

The deck talks about FlashAttention, PagedAttention, FA3 vs FA4 backends, MLA kernels — all kernel-level decisions on production GPUs. On a laptop CPU you can't run FA3, but you **can** see the same kind of decision-making happen at smaller scale:

- `n_threads` is your "TP size"
- `--batch-size` / `--ubatch-size` is your "chunked prefill"
- Quantization choice (`Q2_K` → `Q8_0`) is the deck's quantization decision matrix in miniature
- `-ngl` (GPU layer offload) is the closest analogue to deck's "what runs on accelerator vs CPU"

After this track you should never look at vLLM's `--gpu-memory-utilization` flag the same way again — you'll know what kind of trade-off the engine is balancing under the hood.

## How to take this track

1. **Build from source** following [`01-build-from-source.md`](01-build-from-source.md). Pick the backend that matches your hardware (CUDA / Metal / Vulkan / CPU).
2. **Run the sweep that matches your bottleneck.** Don't run all of them blindly:
   - **CPU only?** Run `thread-sweep` and `quant-sweep` first.
   - **GPU available?** Run `gpu-offload-sweep` and `batch-size-sweep`.
   - **Plenty of RAM but slow CPU?** Run `ctx-len-sweep` to see prefill scaling.
3. **Write the result up.** Pick ONE finding and explain why it happened in the deliverable section of the main lab `benchmarks/results.md`.
4. **Optional: pick a challenge** from [`CHALLENGES.md`](CHALLENGES.md).

## Outputs land in

`benchmarks/bonus-<sweep-name>.{md,json,png}` at the repo root. The matplotlib chart is helpful for the writeup but optional.

## Don't compare across laptops

Your numbers are not comparable to your classmate's. The only fair comparison is **your laptop, before optimization, vs your laptop, after optimization**. The lab grade is based on the size of *your* speedup and the quality of your explanation, not on absolute throughput.
