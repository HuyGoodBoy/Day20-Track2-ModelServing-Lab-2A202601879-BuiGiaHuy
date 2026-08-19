# GUIDE — Làm lab Day 20 từ đầu đến cuối

Hướng dẫn từng bước. Làm theo đúng thứ tự. Mỗi bước có **lệnh chạy**, **bạn sẽ thấy gì**,
và **file nào được sinh ra** (file đó chính là điểm).

**Tổng thời gian:** ~2.5 giờ cho base track · +1–2 giờ nếu làm bonus.

```
PHASE 0  Setup                 ~20 phút
PHASE 1  Base track (100 pts)  ~2 giờ      ← bắt buộc
PHASE 2  Bonus track (20 pts)  ~1-2 giờ    ← optional, làm SAU khi base xong
PHASE 3  Codex review          ~10 phút    ← cổng kiểm tra trước khi submit
PHASE 4  Submit                ~5 phút
```

> **Quy tắc vàng:** mọi file `benchmarks/*.md` mà lab sinh ra đều có một section
> **"required — replace this line"**. Bạn **phải** thay nó bằng nhận xét của mình.
> `make verify` sẽ fail nếu còn sót. Số liệu là phần dễ; nhận xét là phần được chấm.

---

# PHASE 0 — Setup

## Bước 0.1 — Kiểm tra máy có chạy được không

```bash
make probe
```

Bạn sẽ thấy CPU, số core, RAM, accelerator, và model sẽ dùng.

**Quyết định ngay tại đây:**

| RAM | Làm gì |
|---|---|
| **≥ 8 GB** | Tiếp tục bước 0.2 trên laptop |
| **< 8 GB** | Dừng lại. Mở [`cloud/README.md`](cloud/README.md) → làm trên Colab/Kaggle. **Không mất điểm.** |

→ Sinh ra: **`hardware.json`** *(rubric 1)*
→ **Screenshot ngay:** `submission/screenshots/01-hardware-probe.png`

## Bước 0.2 — Cài đặt

```bash
make setup
```

Mất 5–15 phút. Nó làm 3 việc: tạo `.venv` + cài 4 package Python, tải **llama.cpp
prebuilt binary** (10–35 MB, **không compile**), tải **Gemma 4 E2B** (2 quantization, ~5.2 GB).

Windows dùng lệnh này thay thế:

```powershell
pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1
```

→ Sinh ra: **`models/active.json`** *(rubric 2)*, `runtime/`, `models/*.gguf`

**Nếu tải model fail** (mạng trường chặn Hugging Face): xem
[`labs/00-setup/MANUAL-DOWNLOAD.md`](labs/00-setup/MANUAL-DOWNLOAD.md).

---

# PHASE 1 — Base track (100 điểm)

## Bước 1.1 — Đo baseline: TTFT / TPOT / percentiles

```bash
make bench
```

Script tự bật `llama-server`, chạy 10 prompt qua HTTP streaming, tắt server, rồi lặp lại
với quantization thứ hai. Mất vài phút.

Bạn sẽ thấy một bảng như:

```
| Quantization | Size (GB) | TTFT P50/P95 | TPOT P50/P95 | Decode (tok/s) |
| UD-Q4_K_XL   | 2.97      | 194 / 203    | 37.0 / 40.7  | 27.0           |
| UD-Q2_K_XL   | 2.24      | 202 / 479    | 33.9 / 34.9  | 29.5           |
```

→ Sinh ra: **`benchmarks/01-quickstart-results.md`** *(rubric 3, 4, 5)*
→ **Screenshot:** `02-bench.png`

**Việc bạn phải làm:** mở file đó, thay section *"Your observation"* bằng câu trả lời:
2-bit nhanh hơn bao nhiêu, nhỏ hơn bao nhiêu, **và có đáng không?**

Muốn trả lời phần "có đáng không" cho tử tế thì phải thử chất lượng:

```bash
make serve                                      # terminal 1: bản 4-bit
python labs/02-serve/serve.py --compare         # hoặc bản 2-bit
```

Hỏi cùng một câu ở cả hai, tự đọc câu trả lời rồi kết luận.

## Bước 1.2 — Tune: tìm thread count tốt nhất cho máy bạn

```bash
make tune
```

Đây là **nguồn cho section 5 của REFLECTION** — before/after thật, không cần compiler,
không cần GPU. Mất vài phút.

```
| threads (-t) | tg128 (tok/s) | vs best |
| 1            | 27.7          | 96%     |
| 4            | 28.9          | 100%    |   ← best
| 8            | 27.4          | 95%     |
| 16           | 24.2          | 84%     |   ← oversubscribe, chậm hơn
```

→ Sinh ra: **`benchmarks/01-tuning-tg128.md`** *(nguồn cho rubric 11)*
→ Screenshot (optional): `06-tune.png`

**Việc bạn phải làm:** giải thích **knee ở đâu và vì sao**. Nếu curve của bạn khác kỳ
vọng (peak không ở physical core count) → nói rõ, đó là phần ăn điểm.

## Bước 1.3 — Dựng server + chứng minh nó chạy

Cần **2 terminal**.

**Terminal 1** (để chạy suốt, đừng tắt):

```bash
make serve
```

**Terminal 2:**

```bash
make smoke
```

`make smoke` chứng minh 2 thứ trong 1 lần chạy: một completion thật, **và** `/metrics` có
`llamacpp:tokens_predicted_total` khác 0.

→ *(rubric 6, 7)*
→ **Screenshot:** `03-serve-and-smoke.png` — phải thấy **cả** server đang listen **và**
output của `make smoke`. Chia đôi terminal, hoặc chụp 2 file `03a-` / `03b-`.

## Bước 1.4 — Load test

Server vẫn chạy ở terminal 1. Ở terminal 2:

```bash
make load-10       # 10 users, 60s
```

→ **Screenshot:** `04-locust-10.png` (phải thấy dòng có `# reqs · Median · 95%ile · 99%ile`)

Rồi tới lượt 50 users — **cần 3 terminal cho bước này**:

```bash
# terminal 2:
make load-50

# terminal 3, CHẠY NGAY KHI load-50 đang chạy:
make metrics
```

> ⚠️ **Lỗi phổ biến nhất của lab này:** chạy `make metrics` khi server đang rảnh.
> Lúc đó `n_busy_slots_per_decode` sẽ ≈ 1 và bạn không có bằng chứng gì về continuous
> batching. `make metrics` **phải** chồng thời gian với `make load-50`.

→ **Screenshot:** `05-locust-50.png`
→ Sinh ra: **`benchmarks/02-server-batching-u50.md`** + `.csv` *(rubric 9)*

Bạn sẽ thấy dòng như: `Peak n_busy_slots_per_decode = 3.79 of 4 slots` — đó chính là
continuous batching đang hoạt động.

## Bước 1.5 — Tổng hợp: server bão hoà ở đâu?

```bash
make load-report
```

Đọc 2 lần load ở trên và tính **effective concurrency** theo Little's Law
(`RPS × average latency`), so với số `--parallel` slot.

→ Sinh ra: **`benchmarks/02-server-results.md`** *(rubric 10)*

**Việc bạn phải làm:** trả lời *server bão hoà ở đâu, bằng chứng nào?* Nếu throughput
tăng ít mà P95 tăng nhiều → phần latency thêm đó là **queue time**, không phải compute.
Đó chính là lập luận goodput@SLO của deck §8.

## Bước 1.6 — RAG pipeline

Server vẫn chạy. Terminal 2:

```bash
make pipeline
```

Bạn sẽ thấy 3 query, context được retrieve, và latency chia theo stage:

```
timings : {'embed': 0.0, 'retrieve': 0.3, 'llm': 1875.2, 'total': 1875.5}
Dominant stage: llm (100% of total)
```

→ *(rubric 12, 13)* · Screenshot (optional): `08-pipeline.png`

**Việc bạn phải làm:** trong REFLECTION §4, khai báo **cái nào real, cái nào stub**.
Stub **không mất điểm** — nói dối mới mất. Thay 2 chỗ `STUB` trong
`labs/03-integrate/pipeline.py` bằng code N19 của bạn nếu có.

## Bước 1.7 — Viết REFLECTION.md

Mở [`submission/REFLECTION.md`](submission/REFLECTION.md) và điền hết. Đây là file
grader đọc kỹ nhất.

Nặng nhất là **§5 "The single change that mattered most"** (10 điểm): lấy kết quả từ
`make tune` ở bước 1.2, và giải thích **cơ chế** — memory bandwidth? cache? scheduling?
Đừng "vibes-based".

## Bước 1.8 — Kiểm tra

```bash
make verify
```

Phải **exit 0**. Nếu chưa, nó in ra đúng danh sách còn thiếu và lệnh cần chạy.

**Base track xong ở đây. Bạn đã có 100 điểm khả dụng.**

---

# PHASE 2 — Bonus track (20 điểm, optional)

> **Chỉ bắt đầu khi PHASE 1 đã xong và `make verify` đã exit 0.** Bonus không bù được
> base track thiếu.

Chi tiết: [`bonus/README.md`](bonus/README.md) · [`bonus/CHALLENGES.md`](bonus/CHALLENGES.md)

Chọn **1–2 cái**, đừng làm hết. 5 tiêu chí × 4 điểm:

| | Lệnh | Ghi chú |
|---|---|---|
| **B1** | `make build-llama && make compare-builds` | Compile cho CPU của bạn rồi so với prebuilt binary. **Máy yếu thắng đậm nhất ở đây.** Cần `cmake`. |
| **B2** | `make sweep-quant` / `sweep-ctx` / `sweep-batch` / `sweep-gpu` | Chọn 1 cái khớp bottleneck của bạn |
| **B3** | — | Ghi before/after của B1 hoặc B2 vào REFLECTION §6 |
| **B4** | — | Chọn 1 challenge C1–C7 trong `bonus/CHALLENGES.md` |
| **B5** | `make mlx-compare` (Mac) **hoặc** `make semantic-cache` (C8) **hoặc** `make serve-embed && make embed-demo` (C9) **hoặc** C6 | 4 lựa chọn — **mọi nền tảng đều đạt được** |

Nên chọn cái nào theo máy:

- **CPU-only** → B1 (`compare-builds`). Đây là speedup lớn nhất cả lab.
- **RAM chật** → `make sweep-quant`
- **Có GPU** → `make sweep-gpu`
- **Quan tâm RAG long-context** → `make sweep-ctx`
- **Không muốn tải thêm gì** → C8 hoặc C9 (chạy được cả với `--offline`)

Mỗi bonus script cũng sinh `benchmarks/bonus-*.md` với section *"required — replace this
line"* — vẫn phải điền.

---

# PHASE 3 — Nhờ Codex review trước khi submit

Trước khi push, dùng một coding agent (**Codex CLI**, Claude Code, Cursor — cái nào cũng
được) để soát lại repo. `make verify` chỉ kiểm tra **file có tồn tại**; agent kiểm tra
được **nội dung có hợp lý**.

Mở agent ở thư mục repo và paste nguyên đoạn này:

```text
Bạn là trợ lý review submission. Repo này là bài lab Day 20 (Model Serving).

Đọc rubric.md, rồi kiểm tra repo của tôi so với TỪNG tiêu chí trong đó.

Với mỗi tiêu chí, báo cáo: PASS / FAIL / KHÔNG CHẮC + file nào là bằng chứng.
Cụ thể kiểm tra:
1. hardware.json và models/active.json có tồn tại và hợp lệ không?
2. Mọi file benchmarks/*.md còn sót section "required -- replace this line" không?
3. submission/REFLECTION.md còn placeholder nào chưa điền không?
   Có section nào tôi để trống hoặc trả lời quá sơ sài không?
4. Số liệu trong REFLECTION có KHỚP với số trong benchmarks/*.md không?
   (Đây là lỗi hay gặp: copy sai, hoặc chỉnh tay rồi quên cập nhật.)
5. submission/screenshots/ có đủ 5 ảnh theo submission/screenshots/README.md không?
6. REFLECTION §5 có giải thích được CƠ CHẾ (bandwidth/cache/scheduling) không,
   hay chỉ là "vibes-based" và bullet số liệu?
7. Có file nào tôi vô tình commit mà đáng lẽ không nên (models/*.gguf, runtime/) không?

QUAN TRỌNG — giới hạn của bạn:
- KHÔNG viết hộ tôi phần nhận xét, giải thích hay reflection. Đó là phần bị chấm
  và phải là của tôi.
- KHÔNG bịa hay đoán số liệu. Nếu thiếu số, báo là thiếu.
- Chỉ chỉ ra chỗ nào yếu/thiếu và hỏi tôi câu hỏi để tôi tự viết cho tốt hơn.

Cuối cùng: liệt kê những việc tôi phải làm trước khi submit, xếp theo mức quan trọng.
```

Sửa những gì agent chỉ ra, chạy lại `make verify`, rồi sang PHASE 4.

> **Lưu ý học thuật:** dùng agent để **soát lỗi và đặt câu hỏi** là hợp lệ và được
> khuyến khích. Để agent **viết hộ phần phân tích** thì không — §5 và §3 là chỗ grader
> đánh giá tư duy của bạn, và một đoạn văn do AI viết thì đọc ra ngay.

---

# PHASE 4 — Submit

1. `make verify` → **exit 0** (chạy lần cuối)
2. Fork/copy repo lên GitHub account của bạn, set **public**
3. Commit + push:
   ```bash
   git add -A && git commit -m "Day 20 lab submission" && git push
   ```
4. Paste public URL vào ô submission Day 20 trên VinUni LMS

**Repo phải public đến khi điểm được công bố.** Private → grader không xem được → **0 điểm**.

Đừng commit `models/*.gguf` hay `runtime/` — đã có trong `.gitignore`, và `make verify`
không đòi chúng.

---

# Troubleshooting

| Triệu chứng | Cách xử lý |
|---|---|
| `unknown model architecture: 'gemma4'` | llama.cpp quá cũ. `make runtime` để tải lại bản pin. |
| `make serve` báo không tìm thấy venv | Chưa chạy `make setup` |
| `make bench` fail, câu trả lời rỗng | Gemma 4 là reasoning model; lab đã set `--reasoning off`. Nếu bạn tự bật `LAB_REASONING=on` thì `content` sẽ rỗng cho tới khi model "nghĩ" xong. |
| `make metrics` báo scrape failed | Server chưa chạy, hoặc bạn không chạy `make serve` |
| `busy_slots ≈ 1` dù đã chạy metrics | Bạn chạy `make metrics` khi không có load. Phải chồng với `make load-50`. |
| locust chỉ hoàn thành vài request | Bình thường trên máy yếu. Muốn nhiều mẫu hơn: `-t 3m`, hoặc giảm `LAB_LOAD_SHORT_TOKENS`. |
| Hugging Face bị chặn | [`labs/00-setup/MANUAL-DOWNLOAD.md`](labs/00-setup/MANUAL-DOWNLOAD.md) |
| Máy < 8 GB RAM | [`cloud/README.md`](cloud/README.md) |
| `make verify` fail mà không hiểu vì sao | Nó in đúng file thiếu + lệnh cần chạy. Đọc kỹ dòng đó. |

## Các knob có thể đổi

Không cần file `.env` — set inline là được:

```bash
LAB_N_THREADS=4 make bench       # dùng thread count tốt nhất từ make tune
LAB_N_CTX=4096 make serve        # context lớn hơn (tốn RAM hơn)
LAB_PARALLEL=8 make serve        # nhiều slot hơn
LAB_REASONING=on make bench      # bật thinking để xem nó tốn bao nhiêu
```

Danh sách đầy đủ: [`.env.example`](.env.example)
