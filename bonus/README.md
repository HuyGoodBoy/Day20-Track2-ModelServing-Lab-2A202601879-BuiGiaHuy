# Bonus track (+20 pts, optional)

> Chỉ bắt đầu khi base track xong và `make verify` exit 0 — xem
> **[GUIDE.md → PHASE 2](../GUIDE.md)**

The core lab hands you a prebuilt binary and a working server. This track takes the
abstraction away: you compile llama.cpp for *your* CPU, sweep the knobs that matter
on *your* hardware, and explain what you found.

> **Weak laptops have the advantage here.** The prebuilt binary you used all lab is
> compiled for a generic baseline CPU, because it has to run everywhere. A build
> targeted at your actual CPU can use the vector extensions it really has — and the
> gap is usually widest on modest hardware. That gap is the single largest speedup
> available anywhere in this lab.

**Time budget:** 60–120 minutes. The build alone is 5–15 minutes. Each sweep is
5–15 minutes. **Do not run everything** — pick what your hardware makes interesting.

---

## The five bonus criteria (4 pts each)

| # | What | How |
|---|---|---|
| **B1** | Build from source, compare against the prebuilt binary | `make build-llama && make compare-builds` |
| **B2** | Run at least one sweep | `make sweep-quant` · `sweep-ctx` · `sweep-batch` · `sweep-gpu` |
| **B3** | Quantify a bonus-track speedup (before/after) | REFLECTION §5 or §6 |
| **B4** | Go deep on one challenge C1–C7 | [`CHALLENGES.md`](CHALLENGES.md) |
| **B5** | One runtime/regime comparison — **pick any one** | MLX · C8 · C9 · C6 |

B5 exists in four flavours so that every platform can reach 20/20:

| Your machine | B5 option |
|---|---|
| Apple Silicon | `make mlx-compare` — MLX vs llama.cpp Metal, same model (needs `pip install 'mlx-lm>=0.31.3' mlx`) |
| NVIDIA GPU | **C6** Vulkan vs CUDA — you already have the Vulkan/prebuilt side |
| Anything at all | **C8** `make semantic-cache` — the cache above the KV cache |
| Anything at all | **C9** `make serve-embed && make embed-demo` — the prefill-bound regime |

C8 and C9 both run with `--offline` too (synthetic embeddings, no server), so you can
read and reason about the logic even while a download is still going.

Two things to know before you pick:

- **MLX**: `mlx-lm` rejects ~140 parameters in Unsloth's Gemma 4 MLX weights on a strict
  load, because Gemma 4 E2B shares KV across 20 of its 35 layers and mlx-lm builds only
  the tensors it uses while the conversion kept all of them. `compare-mlx-vs-llama-cpp.py`
  detects this, retries non-strictly, and prints a sample generation so you can confirm
  the output is coherent before trusting any number. Verified working; do check that
  sample.
- **C8 semantic cache**: the lab ships one model, so the embedding server runs a *chat*
  model in pooling mode. That is a weak encoder, and the exercise is to diagnose it
  rather than to report a hit rate. Read C8 before you start.

---

## Which sweep should *you* run?

| If your machine is… | Run | Because |
|---|---|---|
| CPU-only | **B1** `compare-builds`, then `make tune` harder | Compile flags and thread count are your whole performance story |
| RAM-constrained | `make sweep-quant` | The size/speed/quality trade is a real decision, not homework |
| Has a GPU | `make sweep-gpu` | Find where partial offload stops helping |
| Doing long-context RAG | `make sweep-ctx` | Watch prefill go super-linear — that *is* TTFT |
| Serving many users | `make sweep-batch` | Chunked prefill: throughput bought with TTFT |

Layout:

```
bonus/
├── 01-build-from-source.md   ← per-OS, per-backend build guide
├── compare-builds.py         ← B1: prebuilt vs your build, same model, same workload
├── CHALLENGES.md             ← C1-C10, pick one and go deep
├── sweeps/
│   ├── quant-sweep.py        ← Unsloth Dynamic ladder, UD-IQ2_M -> UD-Q8_K_XL
│   ├── ctx-len-sweep.py      ← prefill cost vs prompt length
│   ├── batch-size-sweep.py   ← -b / -ub, chunked prefill
│   └── gpu-offload-sweep.py  ← -ngl 0..99
├── serving-regimes/
│   ├── embedding-serving.py  ← C9, prefill-bound regime
│   └── semantic-cache-demo.py ← C8, meaning-based cache
└── mlx/
    └── compare-mlx-vs-llama-cpp.py   ← B5 on Apple Silicon
```

Reports land in `benchmarks/bonus-*.md` at the repo root. Commit them.

---

## Why this maps onto the deck

The deck talks about FlashAttention variants, PagedAttention, FA3-vs-FA4 kernel
selection, MLA — all decisions made on datacenter GPUs. You cannot run FA3 on a
laptop. You *can* make the same **kind** of decision at small scale:

| Laptop knob | Datacenter analogue |
|---|---|
| `-t` thread count | parallelism width / TP size |
| `-b` / `-ub` | chunked prefill scheduling |
| quantization choice | the FP8 / INT4 / NVFP4 decision matrix |
| `-ngl` layer offload | what runs on accelerator vs host |
| `-DGGML_NATIVE=ON` | picking FA3 for Hopper vs FA4 for Blackwell |

After this track, vLLM's `--gpu-memory-utilization` stops being a magic number and
starts being a trade-off you have personally measured.

---

## How to write it up

In `submission/REFLECTION.md` §5 (or §6 for a second finding):

```
Change:  <e.g. rebuilt llama.cpp with -DGGML_NATIVE=ON on a CPU with AVX-512>
Before:  <number + units>
After:   <number + units>
Speedup: <X.Y>x
Why it worked (1-2 paragraphs): <a mechanism, not vibes -- memory bandwidth?
                                 vector width? cache residency? scheduling?>
```

Every generated report ends with a **"required — replace this line"** section.
`make verify` fails while any of those are unanswered, on purpose: the numbers are
the easy half.

**Be honest when a result contradicts the deck.** A measurement that came out the
"wrong" way and is explained well scores higher than one that matched expectations
and was not examined. Instructors read these closely.

## Do not compare across laptops

Your numbers are not comparable to your classmate's. The only fair comparison is
your machine before vs your machine after.
