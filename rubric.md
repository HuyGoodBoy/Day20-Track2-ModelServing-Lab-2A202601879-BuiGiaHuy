# Day 20 Lab — Grading Rubric (100 core + 20 bonus)

Track-2 Daily Lab weight = 30%.

> **This is a personal report.** Every student runs the lab on their own laptop.
> Your numbers are **not comparable** to your classmates' — the only comparison
> that counts is **your machine before vs your machine after**. The grade rewards
> the clarity of your setup, your measurements and your reasoning, **not absolute
> speed**. An 8 GB laptop and an RTX 5090 workstation can both score 100.
>
> Nothing in the core 100 points requires a GPU, a compiler, or Docker.

Everything is graded against **what is actually committed to your repo**, not what
you say you did.

---

## Core (100 pts)

| # | Track | Criterion | Evidence | Pts |
|---|---|---|---|--:|
| 1 | 00-setup | Hardware probed. If you ran on Colab/Kaggle instead, that is declared in REFLECTION §1 | `hardware.json` committed + screenshot `01-hardware-probe.png` | 5 |
| 2 | 00-setup | Model manifest committed and well-formed | `models/active.json` names the repo + both quantizations | 5 |
| 3 | 01-measure | Latency table for **both** quantizations | `benchmarks/01-quickstart-results.md`, 2 rows, percentiles filled | 10 |
| 4 | 01-measure | TTFT and TPOT reported **separately** (not just end-to-end) | same file; values plausible and non-zero | 5 |
| 5 | 02-serve | `llama-server` serves OpenAI-compatible `/v1/chat/completions` | screenshot `03-serve-and-smoke.png` — server log **and** a successful `make smoke` | 10 |
| 6 | 02-serve | `/metrics` shows non-zero `llamacpp:tokens_predicted_total` after a request | same screenshot (`make smoke` prints it) | 5 |
| 7 | 02-serve | Load tests at `-u 10` **and** `-u 50`, 60s each | screenshots `04-locust-10.png` + `05-locust-50.png` | 10 |
| 8 | 02-serve | **Saturation reading** — RPS plateau, P95 inflation, effective concurrency | `benchmarks/02-server-results.md` with your written reading | 5 |
| 9 | 02-serve | **Continuous batching observed** — peak `n_busy_slots_per_decode` under load | `benchmarks/02-server-batching*.md` or `02-server-metrics*.csv` | 5 |
| 10 | 03-integrate | `pipeline.py` runs end-to-end on 3 queries and prints retrieved-context provenance | REFLECTION §4 (paste or screenshot) | 10 |
| 11 | 03-integrate | Which N16–N19 pieces are real vs stubbed, **and** the embed/retrieve/LLM latency split | REFLECTION §4 | 5 |
| 12 | submission | REFLECTION.md fully filled in — no template placeholders, no unanswered generated sections | `make verify` exits 0 | 10 |
| 13 | submission | **"The single change that mattered most"** — a real before/after from your own machine, explained | REFLECTION §5 reads as an argument, not a bullet dump | 10 |
| 14 | repo | Reproducible: a clean clone plus `make setup && make bench && make verify` would reproduce your numbers | commit history + `make verify` output | 5 |
|  |  | **Core total** |  | **100** |

### Getting item 13 without any bonus work

`make tune` sweeps thread counts using the prebuilt `llama-bench` — no compiler, no
GPU — and writes `benchmarks/01-tuning-tg128.md` with a before/after and a speedup
ratio. That file is enough for item 13. Changing the quantization, `--ctx-size`, or
`--parallel` and re-measuring also counts. What is graded is the *explanation*, not
the size of the number.

---

## Bonus (20 pts, optional)

Every criterion is reachable on **any** platform. B5 deliberately offers four
alternatives so that Apple Silicon is an option, not a requirement.

| # | Criterion | Evidence | Pts |
|---|---|---|--:|
| B1 | Built llama.cpp from source and compared it to the prebuilt binary | `benchmarks/bonus-build-compare-*.md` (`make build-llama && make compare-builds`) | 4 |
| B2 | Ran at least one sweep — quantization, context length, batch size, or GPU offload | `benchmarks/bonus-*-sweep.md` with a non-trivial table | 4 |
| B3 | A **bonus-track** speedup quantified with before/after numbers | REFLECTION §5 or §6, in `before: X / after: Y / speedup: Z×` form, from B1 or B2 (not the core `make tune` result) | 4 |
| B4 | Attempted at least one open challenge C1–C7 | writeup in REFLECTION §6 or `bonus/<challenge>.md` | 4 |
| B5 | **A runtime or regime comparison — pick ONE:** MLX vs llama.cpp (Apple Silicon) · C8 semantic caching · C9 embedding serving · C6 Vulkan vs CUDA | the matching `benchmarks/bonus-*.md` | 4 |
|  | **Bonus total** |  | **20** |

Bonus never hurts your core grade; skipping it entirely is fine. A **strong** bonus
submission earns a written instructor review focused on the quality of your
reasoning, not the size of your numbers.

**Do not attempt everything.** One well-explained finding beats five shallow tables.

---

## Required screenshots (5)

Full list and tips: [`submission/screenshots/README.md`](submission/screenshots/README.md).
All five come from the core path — none require bonus work.

1. `01-hardware-probe.png` — `make probe`
2. `02-bench.png` — `make bench` results table
3. `03-serve-and-smoke.png` — `make serve` running + `make smoke` output
4. `04-locust-10.png` — `make load-10` summary
5. `05-locust-50.png` — `make load-50` summary

---

## Submission

**No PR needed — submit your public GitHub URL to the VinUni LMS.**

1. Fork or copy this repo to your own GitHub account and make it **public**.
2. Complete the four core tracks: `00-setup` → `01-measure` → `02-serve` → `03-integrate`.
3. Add your screenshots to `submission/screenshots/`.
4. Fill in `submission/REFLECTION.md` — this is what the grader reads most carefully.
5. Run `make verify` at the repo root and make sure it **exits 0**.
6. Push, then paste the public repo URL into the Day 20 submission box in the LMS.

**Your repo must stay public until grades are released.** A private repo the grader
cannot open scores 0.

---

## How the grader runs your repo

```bash
git clone https://github.com/<you>/Day20-Track2-ModelServing-Lab
cd Day20-Track2-ModelServing-Lab
cat hardware.json models/active.json          # items 1, 2
cat benchmarks/01-quickstart-results.md       # items 3, 4
cat benchmarks/02-server-results.md           # item 8
cat benchmarks/02-server-batching*.md         # item 9
ls submission/screenshots/                    # items 5, 6, 7
cat submission/REFLECTION.md                  # items 10-13
make verify                                   # item 12 — exits 0?
ls benchmarks/bonus-*.md                      # bonus
```

`make verify` only checks **committed** files. The model weights and the runtime
binaries are gitignored on purpose, so their absence on the grader's machine is
never a failure — do not commit them.

---

## Late policy / regrade

Standard Track-2 policy applies — see `INDEX-Track2.md` in the course material repo.
