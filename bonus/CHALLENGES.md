# Bonus challenges — pick one, go deep

The sweeps are the warm-up. These are open-ended. **Pick one.** A deeply-explained
C5 beats a shallow C1 + C2 + C3.

C1–C7 satisfy bonus **B4**. C6, C8 and C9 can each satisfy bonus **B5** instead
(see [`README.md`](README.md)). Verify every flag against your own binary first —
`llama-server --help | grep <flag>` — because llama.cpp moves fast and this file
is pinned to build `b10488`.

---

## C1. Speculative decoding with Gemma 4's own MTP head

> **Needs `LAB_MODEL=gemma4-e2b`.** Qwen3.5 0.8B publishes no MTP head, so this challenge
> is Gemma-only. On the small model, pick a different challenge — C2, C5, C7, C8 or C9 all
> work with either.

Gemma 4 E2B ships an **MTP (multi-token prediction) head** as a separate GGUF, which
means you do not have to go hunting for a tokenizer-compatible draft model — the
matched draft is published alongside the target.

```bash
python labs/00-setup/download-model.py --with-mtp     # ~98 MB
llama-server --help | grep -iE "draft|mtp|spec"       # find the current flag names
```

In `b10488` the draft-model flags are `-md/--model-draft` and `--draft-max`
(**not** `--draft-model` — that is the vLLM spelling). Whether the MTP head attaches
through `-md` or a dedicated flag is exactly what you should check with `--help`
before assuming.

Measure tokens/sec with and without, at 2–3 temperatures. The deck claims EAGLE-3
reaches 3–6.5×; you will likely see far less. **Explain the gap** — acceptance rate,
draft/target size ratio, and how greedy vs sampled decoding changes it.

Also worth testing: speculative decoding is a *latency* optimization. Under heavy
concurrency the verification overhead can make it net-negative, which is why
production engines disable it above a batch-size threshold. Run `make load-50`
with and without it and see whether that shows up on your machine.

## C2. KV-cache quantization

```bash
python labs/02-serve/serve.py -- --cache-type-k q8_0 --cache-type-v q8_0
```

This is the deck's "FP8 KV cache" idea on CPU/Metal/Vulkan. Measure three things:
RAM saved (watch process RSS as `--ctx-size` grows), latency change, and — the part
people skip — **quality change**. Build a 10-prompt eval you can grade
automatically: JSON extraction, or arithmetic, anything with a checkable answer.
A memory saving that quietly costs accuracy is not a win.

## C3. Multi-LoRA serving

`--lora` accepts multiple adapters. Find or train two small LoRAs (Hugging Face has
plenty — one for SQL, one for tool-calling), serve both over the same base weights,
and measure the per-request adapter switching cost. This is the deck's Multi-LoRA
serving frame (Punica / S-LoRA) at laptop scale.

## C4. Best-of-N sampling with a reranker

Send the same prompt N times concurrently with different seeds, then pick the best
answer with a cheap reranker (a length/repetition heuristic is enough to start).
Measure end-to-end latency and quality against single-shot.

The point: "throughput" can be spent on *quality for one user* instead of *more
users*. Your `--parallel` slots do not care which you choose.

## C5. The "smallest useful model" challenge

If yours is the slowest laptop in the room, this one is for you. Walk down the
Unsloth Dynamic ladder — `UD-Q8_K_XL` → `UD-Q4_K_XL` → `UD-Q2_K_XL` → `UD-IQ2_M` —
and find where the model stops being *useful* rather than where it stops being fast.
Grade 5 prompts by hand at each level.

Deliverable: an argument for which quantization you would actually ship at your RAM
ceiling, with the failure you saw at the next step down.

## C6. Vulkan vs CUDA on the same GPU  *(also satisfies B5)*

If you have an NVIDIA GPU you are already half done: on Linux the prebuilt runtime
**is** the Vulkan build, so you have the Vulkan side measured. Build the CUDA side:

```bash
LLAMA_CMAKE_FLAGS=-DGGML_CUDA=ON make build-llama
make compare-builds
```

Quantify the gap, then answer the real question: **why do vLLM and SGLang bother
with vendor-specific kernels** (FA3, FA4, FlashMLA, TRTLLM-MHA) instead of shipping
one portable Vulkan path? Your number is the argument.

## C7. CPU instruction-set archaeology

Build twice — `-DGGML_NATIVE=ON` versus `-DGGML_NATIVE=OFF` (a generic baseline) —
and compare. Then look up what your CPU actually has (`/proc/cpuinfo` on Linux,
`sysctl -a | grep machdep.cpu` on macOS) and try enabling extensions explicitly.

Make a table of build flag vs tokens/sec. This is the same decision the cloud side
makes choosing FA3 for Hopper vs FA4 for Blackwell: match the kernel to the silicon.

One trap to avoid: never compare a Debug build to a Release build and report the
difference as a speedup.

## C8. Semantic caching — the cache above the KV cache  *(also satisfies B5)*

The deck argues the serving stack is **three caches deep**:

```
request -> [1] semantic cache (meaning) -> [2] prefix/KV cache -> [3] full inference
```

A layer-1 hit returns a stored answer to a *paraphrased* prompt for **zero** compute
— no prefill, no decode. Layer 2 only helps when the prefix is byte-identical.

```bash
make serve &            # chat       :8080
make serve-embed &      # embeddings :8081
make semantic-cache
# no servers? logic demo + threshold sweep:
python bonus/serving-regimes/semantic-cache-demo.py --offline --sweep
```

**Important: the lab has no dedicated embedding model, so `make serve-embed` runs a *chat* model in
pooling mode.** Mean-pooled decoder states are a weak embedder — you will see genuine
paraphrases score *below* unrelated prompts. Do not report the raw hit rate as if it
meant something; the interesting deliverable is the diagnosis:

- name one **false hit** (an unrelated prompt that matched) and one **false miss**
  (a real paraphrase that did not), with their similarity scores
- show that no single threshold fixes both — that is the actual trade-off
- explain *why* a decoder trained to predict next tokens makes a poor sentence encoder,
  and what a dedicated embedding model (Qwen3-Embedding, BGE-M3, EmbeddingGemma) does
  differently

If you want the clean version of the curve, point `--embed-url` at a server running a
real embedding GGUF and compare the two similarity distributions. That comparison —
weak embedder vs proper embedder, same prompt stream — is a stronger submission than a
hit-rate table from either one alone.

Security note worth a sentence in your writeup: shared semantic and prefix caches can
leak information across users through timing side channels, so production deployments
salt the cache per tenant.

## C9. Embedding & reranker serving — the retrieval half  *(also satisfies B5)*

Embedding serving is a **different regime**: one forward pass per text, no KV cache,
no decode loop. Throughput comes from large *static* batches, not continuous batching.

```bash
make serve-embed &
make embed-demo
```

Measure how latency scales with batch size (pure prefill) and compare that curve to
your decode-bound numbers from track 02. Then explain why a chat endpoint and an
embedding endpoint want *opposite* batching strategies — and what that implies for
anyone serving both behind one autoscaler.

Note the demo reuses the chat GGUF to avoid another download. Real retrieval quality
needs a dedicated embedding model; say so in your writeup rather than pretending
otherwise.

## C10. VLM serving (open-ended)

Gemma 4 E2B is multimodal, and the repo ships `mmproj-F16.gguf` (~986 MB) — the
vision projector. Deck §5 lists VLM serving as datacenter-shaped, but you can run it:

```bash
# fetch mmproj-F16.gguf from the same repo, then:
python labs/02-serve/serve.py -- --mmproj models/mmproj-F16.gguf
```

Design your own experiment. The interesting question: how does an image in the prompt
change your TTFT and KV-cache footprint compared to the same number of text tokens?
No script is provided — that is the challenge.

---

## Writing it up

Whatever you pick, the deliverable is one section in `submission/REFLECTION.md`
(or a file at `bonus/<challenge>.md`):

- **Setup** — hardware, and exactly what you changed
- **Numbers** — a before/after table
- **One paragraph** — what this tells you that the deck did not already say

Be honest if the result surprised you. Those are the most interesting writeups, and
they score highest.
