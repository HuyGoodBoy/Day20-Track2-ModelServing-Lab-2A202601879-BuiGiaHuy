# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.4 | 3647.1 | 3647.5 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.1 | 2831.4 | 2831.5 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 2985.4 | 2985.5 |

Mean per stage (ms): embed **0.0** · retrieve **0.2** ·
llm **3154.6** · total **3154.8**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real (required -- replace this line)

_List each of N16, N17, N18, N19 as real or stubbed. Stubbing costs no points;
misrepresenting it does. Then answer: is the dominant stage above what you expected?
If you had to halve this pipeline's latency, which stage would you attack and why?_
