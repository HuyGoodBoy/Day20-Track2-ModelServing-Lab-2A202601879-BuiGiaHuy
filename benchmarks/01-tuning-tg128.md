# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **14 physical · 20 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 78.7 | 98% |
| 7 | 77.9 | 97% |
| 14 | 80.2 | 100% |
| 20 | 66.1 | 82% |
| 40 | 77.7 | 97% |

**Best**: `-t 14` at 80.2 tok/s
**Slowest tested**: `-t 20` at 66.1 tok/s (1.21x spread)
**Against the physical-core default** (`-t 14`, 80.2 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=14 make bench
```

## Your explanation (required -- replace this line)

_Where is the knee, and why there? If the peak sits at your physical core count
and drops above it, say what the extra threads are competing for. If your curve
does something else -- flat, or still climbing at 2x logical cores -- say that
instead and reason about why. A result that contradicts the expected shape is
worth more than one that matches it, as long as you explain it._
