# 03 — Milestone 1 Integration

Connect your `llama-server` endpoint to the platform you've been building since N16. The point isn't to build something elaborate — it's to prove the serving endpoint speaks OpenAI-compat well enough to slot into a real RAG/agent stack.

## Required pieces (from prior days)

| Day | What you should already have |
|---|---|
| **N16** Cloud / IaC | A K8s cluster (kind, k3d, or cloud) or at minimum a Compose stack |
| **N17** Data Pipelines | Something producing structured records — Airflow DAG, batch job, or notebook |
| **N18** Lakehouse | Delta Lake / Iceberg table holding processed records |
| **N19** Vector + Feature Store | Embedding index + Feast feature view |
| **N20** Serving (this day) | `llama-server` from track 02 |

## Integration target

Your demo should answer: *"Given a user query, retrieve top-K relevant rows from the vector index, optionally hydrate features from Feast, then call the local llama-server with the assembled prompt."*

A minimal flow looks like:

```
user query
   │
   ▼
[ embed via local model OR sentence-transformers ]
   │
   ▼
[ top-K from your N19 vector index ]
   │
   ▼
[ optional: feature lookup from N19 Feast online store ]
   │
   ▼
[ build prompt = system + retrieved context + user query ]
   │
   ▼
[ POST /v1/chat/completions  →  http://localhost:8080/v1 ]
   │
   ▼
   answer
```

## Deliverable

A single Python file `pipeline.py` (or notebook `pipeline.ipynb`) showing:

- Config block at top: vector store URL, Feast repo path, llama-server URL
- Function `retrieve(query: str, k: int) -> list[dict]`
- Function `build_prompt(query: str, contexts: list[dict]) -> list[dict]` returning OpenAI-style messages
- Function `answer(query: str) -> str` that ties them together
- A `__main__` that runs three example queries and prints answers + retrieved-context provenance

Plus a 1-paragraph writeup in `benchmarks/03-integration-notes.md`:

- Which N16–N19 pieces you connected
- Where you faked something (it's fine to use SQLite as a "lakehouse" if your N18 work isn't ready)
- One observation about latency: where the time goes (embed? retrieve? llama-server?) measured with simple `time.perf_counter()` blocks

## Live demo (lab session)

Be ready to show:

1. `curl localhost:8080/v1/models` works
2. Run `python pipeline.py` end-to-end with a fresh query — show the retrieved contexts and the answer
3. Show the `/metrics` endpoint reflects the call (`llamacpp:requests_processing` blipped up, `tokens_predicted_total` increased)

## Common stumbling points

- **OpenAI SDK version**: older versions don't accept `base_url`. Use `openai>=1.0.0`. Or use `httpx` directly — the API is just JSON over HTTP.
- **Token counting drift**: llama.cpp's tokenizer doesn't perfectly match OpenAI's, so retrieved-context truncation by token-budget needs to use `Llama.tokenize()` from llama-cpp-python, not `tiktoken`.
- **System prompt caching**: keep the system prompt **identical** across calls. That's how you exercise prefix caching (deck §3) — you can verify by watching `llamacpp:prompt_tokens_total` grow slower than `tokens_predicted_total` after the first call.
