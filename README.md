# Day 20 Lab — Model Serving & Inference Optimization (Track 2)

Lab cho **AICB-P2T2 · Ngày 20 · Model Serving & Inference Optimization**.

Bạn sẽ dựng một inference stack thật trên laptop của mình, đo **TTFT / TPOT /
P50 / P95 / P99**, đẩy nó tới điểm bão hoà bằng load test, rồi tune một knob và
viết report về thay đổi tạo ra speedup lớn nhất **trên chính máy bạn**.

> **Một model, một runtime, mọi laptop.**
> Model: **Gemma 4 E2B** (Apache-2.0, Unsloth GGUF).
> Runtime: **llama.cpp prebuilt binary** — tải về 10–35 MB, **không cần compiler**,
> không cần Docker, không cần API key. Chạy trên Windows / macOS (Intel + Apple
> Silicon) / Linux, có hay không có GPU.

> **Số liệu của bạn không so sánh được với bạn cùng lớp.** Chỉ so **before vs after
> trên chính máy bạn**. Rubric chấm độ rõ ràng của setup + đo lường + lập luận,
> **không** chấm tốc độ tuyệt đối. Một bạn dùng Air M1 8 GB và một bạn dùng
> workstation RTX 5090 đều có thể đạt 100/100. Toàn bộ 100 điểm core **không cần
> GPU, không cần compiler**.

## Trước khi bắt đầu

1. Mở **[`rubric.md`](rubric.md)** — biết trước grader chấm gì.
2. Mở **[`HARDWARE-GUIDE.md`](HARDWARE-GUIDE.md)** — xác nhận laptop bạn đủ điều kiện.

**Yêu cầu:** Python ≥ 3.10 · **8 GB RAM** · ~10 GB đĩa trống.
RAM dưới 8 GB → dùng **[`cloud/`](cloud/README.md)** (Colab / Kaggle), vẫn được điểm như nhau.

---

## Quick start

```bash
git clone https://github.com/<your-username>/Day20-Track2-ModelServing-Lab.git
cd Day20-Track2-ModelServing-Lab

make probe          # 00 · đọc hardware → hardware.json
make setup          # 00 · deps + llama.cpp binary + Gemma 4 E2B (~5.6 GB, 5-15 phút)

make bench          # 01 · TTFT/TPOT/P50/P95/P99, cả 2 quantization
make tune           # 01 · thread sweep → before/after speedup của bạn

make serve          # 02 · llama-server trên :8080  (terminal 1, để chạy)
make smoke          # 02 · chứng minh OpenAI-compat API + /metrics  (terminal 2)
make load-10        # 02 · locust 10 users, 60s
make load-50        # 02 · locust 50 users, 60s
make metrics        # 02 · sample /metrics 60s — chạy KHI load-50 đang chạy
make load-report    # 02 · tổng hợp 2 lần load → saturation reading

make pipeline       # 03 · RAG pipeline → llama-server
make verify         # kiểm tra trước khi push (phải exit 0)
```

`make` để xem toàn bộ target. **Windows:** `pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1`
rồi dùng `.venv\Scripts\python.exe <script>` — mọi script Python đều chạy trên Windows.

---

## Vì sao lab này không dùng vLLM / SGLang

Những engine đó cần CUDA GPU + 16 GB VRAM trở lên. Đẹp trên slide, không chạy được
trên một lớp 30 laptop hỗn hợp. llama.cpp cho bạn **cùng teaching surface** —
GGUF quantization, paged KV cache, continuous batching, OpenAI-compat API,
Prometheus `/metrics` — trên bất cứ phần cứng nào bạn đang có.

**Và vì sao là prebuilt binary, không phải `llama-cpp-python`:** Gemma 4 dùng
architecture `gemma4` (4/2026). Bản wheel `llama-cpp-python` trên PyPI vendor một
bản llama.cpp cũ hơn và sẽ báo `unknown model architecture: 'gemma4'`. Prebuilt
release binary (`b10488`) không có vấn đề đó, tải nhanh hơn, **và** cho bạn
`/metrics` + `--parallel` + `--cont-batching` ngay từ đầu — những thứ mà bản Python
không có.

---

## Track map

| Track | Nội dung | Thời gian |
|---|---|---|
| **[00-setup](labs/00-setup/)** | Probe hardware, tải runtime + model | 15 phút |
| **[01-measure](labs/01-measure/)** | Đo TTFT/TPOT/percentiles · tune thread count | 40 phút |
| **[02-serve](labs/02-serve/)** | OpenAI-compat server · `/metrics` · load test · saturation | 60 phút |
| **[03-integrate](labs/03-integrate/)** | RAG pipeline nối vào N16–N19 | 30 phút |
| **[bonus/](bonus/README.md)** | Build from source · sweeps · 9 challenges (+20 pts) | 60–120 phút |
| **[cloud/](cloud/README.md)** | Fallback Colab / Kaggle nếu laptop không đủ | — |

Core path ≈ **2.5 giờ**.

---

## Slide → track mapping

Mỗi phần của deck Day 20 map vào một chỗ cụ thể trong lab.

| Slide section | Ở đâu trong lab | Pass khi |
|---|---|---|
| §0 Latency taxonomy (TTFT/TPOT/goodput) | `make bench` | Có bảng TTFT/TPOT/P50/P95/P99 |
| §1 Quantization (GGUF, INT4, FP8) | `make bench` (2 quant) + `make sweep-quant` | Số liệu side-by-side, có nhận xét về quality |
| §2 KV cache & PagedAttention | `make serve` (`--ctx-size`, `--cache-type-k/v`) | RAM thay đổi theo ctx được ghi lại |
| §2 Continuous batching | `make metrics` khi `make load-50` chạy | Peak `n_busy_slots_per_decode` được report |
| §2 Speculative decoding (MTP) | bonus **C1** — Gemma 4 E2B có sẵn MTP head | tok/s có vs không spec-decode |
| §3 Single-node serving | `make serve` | OpenAI-compat API hoạt động |
| §3 Production tuning | `make tune`, `make sweep-batch`, `make sweep-ctx` | Sweep table + đoạn giải thích |
| §3 Observability | `make smoke`, `make metrics` | `/metrics` non-zero sau request |
| §3 Backend selection (kernels) | bonus **B1** `make build-llama && make compare-builds` | Prebuilt vs native build, quantified |
| §4 Distributed (TP/PP/EP/DP) | *concept-only — ngoài scope laptop* | — |
| §5 Embedding / reranker serving | bonus **C9** `make serve-embed && make embed-demo` | Throughput curve của prefill-bound regime |
| §5 Semantic caching | bonus **C8** `make semantic-cache` | Hit-rate + threshold tradeoff |
| §5 VLM serving | bonus **C10** — Gemma 4 có `mmproj` | (mở, tự thiết kế) |
| §6 Auto-scaling & ops | *concept-only* | — |
| §7 Edge & hardware | `make probe` + `make sweep-quant` | Quant chọn khớp với RAM thật |
| §8 Goodput@SLO | `make load-report` | Saturation reading + SLO gap |

---

## Bonus track (+20 pts, optional)

> **Laptop yếu là lợi thế ở đây.** Bonus track bóc bỏ abstraction: bạn compile
> llama.cpp cho đúng CPU của mình và đo xem nó thắng prebuilt binary bao nhiêu.
> Trên CPU-only laptop, đây thường là speedup lớn nhất của cả lab.

Chi tiết: **[`bonus/README.md`](bonus/README.md)** · 9 challenges: **[`bonus/CHALLENGES.md`](bonus/CHALLENGES.md)**

```bash
make build-llama && make compare-builds   # B1 · prebuilt vs your build
make sweep-quant                          # B2 · quantization ladder
make sweep-ctx                            # B2 · prefill O(N²) curve
make sweep-batch                          # B2 · chunked prefill
make sweep-gpu                            # B2 · GPU offload (cần GPU)
make mlx-compare                          # B5 · MLX vs llama.cpp (Apple Silicon)
make semantic-cache                        # B5/C8 · cache trên KV cache
make serve-embed && make embed-demo        # B5/C9 · embedding regime
```

B5 có **4 lựa chọn** (MLX · C8 · C9 · C6) nên mọi nền tảng đều đạt được 20/20.

**Đừng làm hết.** *Một* insight giải thích rõ ăn điểm hơn năm bảng số lủng củng.

---

## Submission

**KHÔNG cần PR — chỉ submit GitHub URL công khai vào VinUni LMS.**

1. Fork/copy repo này lên GitHub của bạn, set **public**.
2. Hoàn thành 4 core tracks.
3. Add **5 screenshots** vào `submission/screenshots/` — danh sách ở
   [`submission/screenshots/README.md`](submission/screenshots/README.md).
4. Điền **[`submission/REFLECTION.md`](submission/REFLECTION.md)** — đây là phần
   grader đọc kỹ nhất.
5. `make verify` → **exit 0**.
6. Push, paste public URL vào LMS.

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader
không xem được → 0 điểm.

Đừng commit `models/` hay `runtime/` — chúng đã nằm trong `.gitignore`, và
`make verify` không đòi chúng.

---

## Repo structure

```
├── README.md · HARDWARE-GUIDE.md · rubric.md · Makefile
├── lib/labkit.py               ← plumbing dùng chung (paths, manifests, server, llama-bench)
├── labs/
│   ├── 00-setup/               probe · fetch prebuilt runtime · download model
│   ├── 01-measure/             benchmark.py · tune.py
│   ├── 02-serve/               serve.py · smoke-test.py · load-test.py · load-report.py
│   │                           · record-metrics.py
│   └── 03-integrate/           pipeline.py
├── bonus/                      README · CHALLENGES · build-from-source
│   ├── compare-builds.py       B1 · prebuilt vs your source build
│   ├── sweeps/                 quant · ctx-len · batch-size · gpu-offload
│   ├── serving-regimes/        embedding-serving.py · semantic-cache-demo.py
│   └── mlx/                    compare-mlx-vs-llama-cpp.py
├── cloud/                      Colab / Kaggle fallback notebook
├── scripts/verify.py           pre-submission check
├── benchmarks/                 (generated) reports bạn commit
└── submission/                 REFLECTION.md · screenshots/  ← bạn điền
```

---

## Vì sao lab này quan trọng

Deck Day 20 lập luận rằng **goodput@SLO** — không phải peak throughput — là metric
production. Lab này là chỗ bạn đo cả hai trên máy mình, thấy khoảng cách, và thu hẹp
nó lại. Bonus track cho bạn thấy một model 2B tăng tốc đáng kể **mà không đổi model**,
chỉ bằng cách chọn đúng compile flag và đúng thread count. Intuition đó áp dụng được
cho mọi serving engine trong deck — kể cả những cái cần 8 GPU.
