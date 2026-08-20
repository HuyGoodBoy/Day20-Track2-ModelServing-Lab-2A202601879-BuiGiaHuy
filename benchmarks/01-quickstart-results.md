# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=14` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5652 | 323 / 468 | 13.2 / 13.5 | 1157 / 1303 / 1303 | 75.5 |
| UD-Q2_K_XL | 2.24 | 5394 | 335 / 498 | 13.2 / 13.6 | 1161 / 1337 / 1337 | 75.7 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.

## Your observation (required -- replace this line)

_Is the smaller quantization worth it on your machine? Compare the numbers above,
then judge the answer quality yourself: run `make serve` on each and ask the same
question twice. Size and speed are measurable; usefulness is your call._
