# Day 20 — Model Serving & Inference Optimization (Track 2)

Lab cho **AICB-P2T2 · Ngày 20**.

Bạn dựng một inference stack thật trên laptop của mình, đo **TTFT / TPOT / P50 / P95 /
P99**, đẩy nó tới điểm bão hoà bằng load test, rồi tune một knob và viết report về thay
đổi tạo ra speedup lớn nhất **trên chính máy bạn**.

> ### 👉 Bắt đầu ở đây: **[GUIDE.md](GUIDE.md)**
> Hướng dẫn từng bước, có lệnh cụ thể và checkpoint. Đọc [`rubric.md`](rubric.md) trước
> để biết grader chấm gì.

---

## Lab này chạy trên máy nào cũng được

| | |
|---|---|
| **Model** | **Gemma 4 E2B** (Apache-2.0, Unsloth GGUF) — **một** model cho cả lab |
| **Runtime** | **llama.cpp prebuilt binary** — tải 11–33 MB (bản Windows CUDA 140–240 MB), **không compile** |
| **Cần** | Python ≥ 3.10 · **8 GB RAM** · ~10 GB đĩa |
| **Không cần** | GPU · compiler · Docker · API key · tài khoản trả phí |
| **OS** | Windows · macOS (Intel + Apple Silicon) · Linux |
| **Windows** | Không có `make` → dùng **`.\lab.ps1 <target>`** (tên target giống hệt) |
| **RAM < 8 GB?** | Dùng [`cloud/`](cloud/README.md) — Colab/Kaggle, **điểm không đổi** |

> **Số liệu của bạn không so sánh được với bạn cùng lớp.** Chỉ so **before vs after trên
> chính máy bạn**. Rubric chấm độ rõ ràng của setup + đo lường + **lập luận**, không chấm
> tốc độ tuyệt đối. Một bạn dùng Air M1 8 GB và một bạn dùng RTX 5090 đều có thể đạt
> 100/100. Toàn bộ 100 điểm base **không cần GPU, không cần compiler**.

---

## Luồng làm lab

Làm **theo đúng thứ tự này**. Đừng nhảy vào bonus trước khi base xong.

```
┌─ 1 ─ BASE TRACK ────────────────── 100 điểm · bắt buộc · ~2 giờ ─┐
│                                                                  │
│   make probe                 hardware.json                       │
│   make setup                 runtime + Gemma 4 E2B               │
│   make bench                 TTFT / TPOT / percentiles, 2 quant  │
│   make tune                  thread sweep → before/after của bạn │
│   make serve   + make smoke  OpenAI-compat API + /metrics        │
│   make load-10 / load-50     load test                           │
│   make metrics               continuous batching (chạy CÙNG load)│
│   make load-report           server bão hoà ở đâu                │
│   make pipeline              RAG → llama-server                  │
│   viết submission/REFLECTION.md                                  │
│   make verify                phải exit 0                         │
└──────────────────────────────────────────────────────────────────┘
                                 │
                    base xong, verify exit 0
                                 ▼
┌─ 2 ─ BONUS TRACK ──────────── +20 điểm · optional · ~1-2 giờ ────┐
│                                                                  │
│   B1  make build-llama && make compare-builds                    │
│       compile cho CPU của bạn → so với prebuilt binary           │
│       (máy yếu thắng đậm nhất ở đây)                             │
│   B2  make sweep-quant / sweep-ctx / sweep-batch / sweep-gpu     │
│   B3  ghi before/after vào REFLECTION §6                         │
│   B4  1 challenge trong bonus/CHALLENGES.md (C1–C7)              │
│   B5  make mlx-compare  ·  make semantic-cache  ·  make embed-demo│
│       (4 lựa chọn — mọi nền tảng đều đạt được)                   │
│                                                                  │
│   Chọn 1-2 cái. MỘT insight giải thích rõ > năm bảng số nông.     │
└──────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─ 3 ─ SUBMIT ──────────────────────────────────────── ~5 phút ────┐
│   make verify → exit 0  ·  repo PUBLIC  ·  paste URL vào LMS      │
└──────────────────────────────────────────────────────────────────┘
```

Chạy `make` để xem toàn bộ target.

---

## Vì sao lab không dùng vLLM / SGLang

Những engine đó cần CUDA GPU + 16 GB VRAM trở lên. Đẹp trên slide, không chạy được trên
một lớp 30 laptop hỗn hợp. llama.cpp cho bạn **cùng teaching surface** — GGUF
quantization, paged KV cache, continuous batching, OpenAI-compat API, Prometheus
`/metrics` — trên bất cứ phần cứng nào bạn đang có.

**Và vì sao prebuilt binary, không phải `llama-cpp-python`:** Gemma 4 dùng architecture
`gemma4` (4/2026). Wheel `llama-cpp-python` trên PyPI vendor một bản llama.cpp cũ hơn và
sẽ báo `unknown model architecture: 'gemma4'`. Prebuilt release binary không có vấn đề
đó, tải nhanh hơn, **và** cho bạn `/metrics` + `--parallel` + `--cont-batching` ngay từ
đầu — những thứ bản Python không có.

---

## Slide → chỗ nào trong lab

| Slide section | Ở đâu | Track |
|---|---|---|
| §0 Latency taxonomy (TTFT/TPOT/goodput) | `make bench` | base |
| §1 Quantization | `make bench` (2 quant) · `make sweep-quant` | base + bonus |
| §2 KV cache & PagedAttention | `make serve` (`--ctx-size`, `--cache-type-k/v`) | base |
| §2 Continuous batching | `make metrics` khi `make load-50` chạy | base |
| §2 Speculative decoding (MTP) | challenge **C1** — Gemma 4 E2B có sẵn MTP head | bonus |
| §3 Single-node serving | `make serve` | base |
| §3 Production tuning | `make tune` · `sweep-batch` · `sweep-ctx` | base + bonus |
| §3 Observability | `make smoke` · `make metrics` | base |
| §3 Backend / kernel selection | **B1** `build-llama` + `compare-builds` | bonus |
| §4 Distributed (TP/PP/EP/DP) | *concept-only — ngoài scope laptop* | — |
| §5 Embedding / reranker serving | **C9** `make serve-embed && make embed-demo` | bonus |
| §5 Semantic caching | **C8** `make semantic-cache` | bonus |
| §5 VLM serving | **C10** — Gemma 4 có `mmproj` (tự thiết kế) | bonus |
| §6 Auto-scaling & ops | *concept-only* | — |
| §7 Edge & hardware | `make probe` · `make sweep-quant` | base + bonus |
| §8 Goodput@SLO | `make load-report` | base |

---

## Repo structure

```
├── GUIDE.md                    ← bắt đầu ở đây: hướng dẫn từng bước
├── rubric.md                   ← 100 điểm base + 20 bonus
├── HARDWARE-GUIDE.md           ← máy bạn cần gì, chọn backend nào
├── Makefile                    ← mọi lệnh (`make` để xem hết)
├── lib/labkit.py               ← plumbing dùng chung
├── labs/
│   ├── 00-setup/               probe · fetch runtime · download model
│   ├── 01-measure/             benchmark.py · tune.py
│   ├── 02-serve/               serve.py · smoke-test.py · load-test.py
│   │                           · load-report.py · record-metrics.py
│   └── 03-integrate/           pipeline.py
├── bonus/                      README · CHALLENGES · build-from-source
│   ├── compare-builds.py       B1
│   ├── sweeps/                 B2 — quant · ctx-len · batch-size · gpu-offload
│   ├── serving-regimes/        C8 semantic cache · C9 embedding serving
│   └── mlx/                    B5 Apple Silicon
├── cloud/                      Colab / Kaggle fallback (< 8 GB RAM)
├── scripts/verify.py           kiểm tra trước khi submit
├── benchmarks/                 (sinh ra) report bạn commit
└── submission/                 REFLECTION.md · screenshots/  ← bạn điền
```

---

## Vì sao lab này quan trọng

Deck Day 20 lập luận **goodput@SLO** — không phải peak throughput — là metric production.
Lab này là chỗ bạn đo cả hai trên máy mình, thấy khoảng cách, và thu hẹp nó. Bonus track
cho bạn thấy một model 2B tăng tốc đáng kể **mà không đổi model**, chỉ bằng cách chọn
đúng compile flag và đúng thread count. Intuition đó áp dụng cho mọi serving engine trong
deck — kể cả những cái cần 8 GPU.
