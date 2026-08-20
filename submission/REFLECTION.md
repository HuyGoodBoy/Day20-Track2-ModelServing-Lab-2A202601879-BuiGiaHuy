# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** _Bui Gia Huy_
**Mã sinh viên:** _2A202601879_
**Cohort:** _A20-K3_
**Ngày submit:** _2026-08-20_

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Windows 10 (AMD64)
- **CPU:** Intel Core i7-12700H
- **Cores:** 14 physical / 20 logical
- **CPU extensions:** AVX2
- **RAM:** 15.6 GB
- **Accelerator:** NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM) + Vulkan
- **llama.cpp asset đã tải:** llama-b10488-bin-win-vulkan-x64.zip
- **Model đã dùng:** Gemma 4 E2B (gemma4-e2b)
- **Quantization:** UD-Q4_K_XL + UD-Q2_K_XL

**Chạy ở đâu:** laptop của tôi (Windows 10, 15.6GB RAM, RTX 3050)

**Setup story** (≤ 80 chữ): Lab chạy trực tiếp trên laptop. Không cần cloud fallback. llama.cpp build với Vulkan backend. Models được download về D:\day20-models\. Tất cả chạy bình thường không cần workaround.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5652 | 323 / 468 | 13.2 / 13.5 | 1157 / 1303 / 1303 | 75.5 |
| UD-Q2_K_XL | 2.24 | 5394 | 335 / 498 | 13.2 / 13.6 | 1161 / 1337 / 1337 | 75.7 |

**Quan sát** (≤ 60 chữ): UD-Q2_K_XL nhỏ hơn 0.73 GB (25%) nhưng decode speed chỉ nhanh hơn 0.3%. Trên máy này với RTX 3050, quantization thấp hơn không mang lại lợi ích đáng kể. UD-Q4_K_XL là lựa chọn tốt hơn vì chất lượng cao hơn với penalty về tốc độ rất nhỏ.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 2.51 | 2800 | 5900 | 7100 | ~3 | 0 |
| 50 | 2.62 | 17000 | 19000 | 21000 | ~4 | 0 |

- **Offered load tăng 5×, throughput thực tăng:** 1.04× (2.51 → 2.62 RPS)
- **P95 tăng:** 3.22× (5900 → 19000 ms)
- **Effective concurrency ở 50 users:** 4 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang chạy): 3.97 / 4 slots

**Saturation reading** (≤ 80 chữ): Server bão hoà rõ rệt ở ~50 users — P95 tăng 3.22× trong khi RPS chỉ tăng 1.04×, chứng tỏ queue bắt đầu fill. Peak busy slots 99% (3.97/4) xác nhận --parallel=4 gần như full. Để tăng goodput@SLO, tôi sẽ tăng `--parallel` (batch width) trước vì đây là continuous batching bottleneck.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | | stub |
| N17 Data pipeline | | stub |
| N18 Lakehouse | | stub |
| N19 Vector + features | | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.2 ms
- llm: 3154.6 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection** (≤ 60 chữ): LLM chiếm gần như 100% latency — embed/retrieve gần như instant vì dùng keyword overlap đơn giản và context nhỏ. Nếu phải giảm latency 2×, tôi sẽ tối ưu LLM stage: tăng --parallel hoặc giảm ctx ở prompt.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization, `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Tunning thread count trên CPU

```
before:  -t 20 → 66.1 tok/s
after:   -t 14 → 80.2 tok/s
speedup: 1.21×
```

**Tại sao nó work** (1–2 đoạn):

Sweep thread count cho thấy peak ở `-t 14` (đúng bằng số physical cores). Khi tăng lên `-t 20` (vượt quá physical cores), throughput giảm 18% xuống còn 66.1 tok/s.

**Cơ chế:** Intel i7-12700H có 14P-cores + 6E-cores nhưng lab OS scheduler ưu tiên P-cores. Khi dùng quá 14 threads, E-cores (yếu hơn) bị ép vào, gây thread contention và context switching overhead. Trên LLM decode (memory-bandwidth bound), mỗi thread cần liên tục access DRAM — khi có quá nhiều threads tranh đủ, memory bandwidth bị phân mảnh, làm giảm effective bandwidth per thread.

---

## 6. Bonus  *(optional — tối đa 20 điểm)*

> Bỏ trống nếu không làm. Xem `bonus/README.md`. Đừng làm hết — **một** finding sâu ăn điểm hơn năm bảng nông.

_(để trống nếu bạn không làm phần này)_

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

_(1–2 câu. Không bắt buộc, nhưng grader đọc hết.)_

P95 latency tăng 3.22× khi load tăng 5×, trong khi RPS gần như không đổi — server bão hòa rất sớm ở 4 parallel slots, cho thấy batch width nhỏ là bottleneck chính trên máy này.

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [ ] `benchmarks/02-server-results.md` committed (`make load-report`) — chưa kiểm tra
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md` đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [ ] `make verify` → **exit 0** — cần chạy kiểm tra
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã paste public URL vào VinUni LMS
- [x] **Không** commit `models/*.gguf` hay `runtime/` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không xem được → 0 điểm.
