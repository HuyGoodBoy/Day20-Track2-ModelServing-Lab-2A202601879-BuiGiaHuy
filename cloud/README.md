# Cloud fallback — Colab / Kaggle

**For students whose laptop cannot run the lab.** Gemma 4 E2B needs ~4 GB of RAM for
inference, so the lab's floor is **8 GB**. Below that — or if setup fails for a reason
you cannot fix — run [`Day20-lab.ipynb`](Day20-lab.ipynb) instead.

## This does not cost you points

The rubric grades the clarity of your setup, measurements and reasoning — never
absolute speed. It already assumes no two students have comparable hardware.

You **must** declare it, though: say in **REFLECTION §1** that you used the cloud
fallback and why. The notebook writes `runtime_environment: "colab"` (or `"kaggle"`)
into `hardware.json` automatically, so this is a one-line note, not paperwork.

## Open it

| Platform | How |
|---|---|
| **Colab** | [colab.research.google.com](https://colab.research.google.com) → File → Open notebook → GitHub → paste your fork's URL → pick `cloud/Day20-lab.ipynb` |
| **Kaggle** | [kaggle.com/code](https://www.kaggle.com/code) → New Notebook → File → Import Notebook → upload `cloud/Day20-lab.ipynb` |

**Kaggle: turn Internet ON** in the settings sidebar first, or the model download fails.

Edit `REPO_URL` in the first cell to point at **your** fork before running.

## CPU or GPU?

The notebook defaults to `RUNTIME = 'cpu'` and that is genuinely fine — the whole core
path works, just slowly (expect a few minutes per benchmark on 2 vCPUs).

Why not the GPU by default: llama.cpp publishes **no prebuilt Linux CUDA binary**, and
Colab/Kaggle images normally ship no Vulkan driver either, so the accelerated prebuilt
assets have nothing to bind to. To actually use a T4 you have to compile with
`-DGGML_CUDA=ON`, which cell 4b does in about 8 minutes.

That compile is not wasted effort — it earns bonus **B1**, and having both a CUDA build
and the Vulkan prebuilt on one machine is challenge **C6** ready-made.

## Same artifacts, same filenames

The notebook runs the same scripts as the laptop path, so it writes the same files:

```
hardware.json
models/active.json
benchmarks/01-quickstart-results.md
benchmarks/01-tuning-tg128.md
benchmarks/02-server-results.md
benchmarks/02-server-batching-u50.md  +  02-server-metrics-u50.csv
benchmarks/locust-10_stats.csv  ·  locust-50_stats.csv
```

`scripts/verify.py` needs no cloud-specific branch.

## Then finish locally

The last cell zips the evidence (not the weights). Download it, unzip into your own
clone, then:

1. Replace every **"required — replace this line"** section in `benchmarks/*.md` with
   your own observations — `make verify` fails while any remain.
2. Fill in `submission/REFLECTION.md`, including the §1 declaration.
3. Add your 5 screenshots, taken from the notebook's cell outputs.
4. `make verify` → exit 0. Push to your **public** repo, submit the URL.

## Gotchas

| Problem | What to do |
|---|---|
| Session disconnected mid-run | Re-run from section 3. The clone and download skip work already on disk. |
| Kaggle "no internet" | Settings sidebar → Internet → On. |
| Colab free tier timed out | Shorten the load runs: set `LOAD_DURATION = '30s'` in cell 1. |
| `unknown model architecture: 'gemma4'` | The runtime fetch was skipped or failed. Re-run section 4. |
| Out of disk | Free tiers give plenty for 5.2 GB, but delete `models/*Q2*` if you must — then you lose rubric items 3/4's second row. |

## A caveat worth writing about

A cloud VM is not your laptop: different core count, different memory bandwidth, a
hypervisor in the way, and neighbours competing for the same host. Your tuning result
describes **the VM you were given**, and the thread-count curve in particular can look
very different from a physical machine's. Say so in §5 — noticing that limitation is
exactly the kind of reasoning the rubric rewards.
