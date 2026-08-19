# Cloud fallback — Colab / Kaggle

> Các bước của lab không đổi: **[GUIDE.md](../GUIDE.md)**

Đây là **phương án fallback**, không phải cách chạy mặc định. Hãy dùng
[`Day20-lab.ipynb`](Day20-lab.ipynb) khi laptop có dưới **8 GB RAM**, hoặc khi setup
local gặp lỗi bạn không thể xử lý. Gemma 4 E2B cần khoảng 4 GB RAM riêng cho inference,
vì vậy lab đặt mức tối thiểu là 8 GB RAM.

## Dùng cloud không mất điểm

Rubric chấm độ rõ ràng của setup, phép đo và lập luận. Rubric không chấm tốc độ tuyệt
đối và không giả định hai sinh viên có phần cứng giống nhau.

Tuy nhiên, bạn **bắt buộc phải khai báo** trong **REFLECTION §1** rằng mình dùng cloud
fallback và nêu lý do. Việc khai báo **không làm mất điểm**. Notebook tự ghi
`runtime_environment: "colab"` hoặc `"kaggle"` vào `hardware.json`, nên bạn chỉ cần
thêm một dòng giải thích.

## Mở notebook

| Nền tảng | Cách mở |
|---|---|
| **Colab** | Mở [colab.research.google.com](https://colab.research.google.com) → File → Open notebook → GitHub → paste URL fork của bạn → chọn `cloud/Day20-lab.ipynb` |
| **Kaggle** | Mở [kaggle.com/code](https://www.kaggle.com/code) → New Notebook → File → Import Notebook → upload `cloud/Day20-lab.ipynb` |

**Trên Kaggle, phải bật Internet** trong settings sidebar trước khi chạy. Nếu Internet
tắt, notebook không thể tải model.

Trong cell đầu tiên, sửa `REPO_URL` để trỏ tới fork của **bạn**.

## CPU hay GPU?

Notebook mặc định dùng `RUNTIME = 'cpu'`. Đây là cấu hình chủ đích và chạy được toàn bộ
base track, nhưng chậm hơn. Với 2 vCPU, mỗi benchmark có thể mất vài phút.

Notebook không mặc định dùng GPU vì llama.cpp **không cung cấp prebuilt Linux CUDA
binary**. Image Colab/Kaggle cũng **không có Vulkan driver**. Vì vậy các prebuilt asset
tăng tốc không có backend phù hợp để sử dụng.

Muốn dùng T4, bạn phải compile với `-DGGML_CUDA=ON`. Cell 4b thực hiện việc này trong
khoảng 8 phút.

Phần compile không bị lãng phí: nó đạt bonus **B1**. Khi có cả CUDA build và Vulkan
prebuilt trên cùng một máy, bạn cũng có sẵn điều kiện cho challenge **C6**.

## Artifact và filename không đổi

Notebook chạy cùng các script với cách làm trên laptop, nên sinh đúng các file sau:

```
hardware.json
models/active.json
benchmarks/01-quickstart-results.md
benchmarks/01-tuning-tg128.md
benchmarks/02-server-results.md
benchmarks/02-server-batching-u50.md  +  02-server-metrics-u50.csv
benchmarks/locust-10_stats.csv  ·  locust-50_stats.csv
```

`scripts/verify.py` không cần nhánh xử lý riêng cho cloud.

## Hoàn tất bài trên máy local

Cell cuối cùng nén các file bằng chứng, không nén model weights. Download file zip, giải
nén vào clone local của bạn, rồi làm lần lượt:

1. Thay mọi section **"required -- replace this line"** trong `benchmarks/*.md` bằng
   nhận xét của bạn. Nếu còn bất kỳ section nào, `make verify` sẽ fail.
2. Điền `submission/REFLECTION.md`, gồm cả khai báo cloud trong §1.
3. Thêm 5 screenshots từ output của các notebook cell.
4. Chạy `make verify` và bảo đảm lệnh **exit 0**. Sau đó push lên repo **public** và
   submit URL.

## Lỗi thường gặp

| Vấn đề | Cách xử lý |
|---|---|
| Session ngắt giữa chừng | Chạy lại từ section 3. Bước clone và download sẽ bỏ qua phần đã có trên disk. |
| Kaggle báo "no internet" | Settings sidebar → Internet → On. |
| Colab free tier hết thời gian | Rút ngắn load test: set `LOAD_DURATION = '30s'` trong cell 1. |
| `unknown model architecture: 'gemma4'` | Bước tải runtime đã bị bỏ qua hoặc fail. Chạy lại section 4. |
| Hết disk | Free tier thường đủ cho 5.2 GB. Nếu buộc phải xóa, xóa `models/*Q2*`; bạn sẽ mất hàng quantization thứ hai của rubric 3–5. |

## Giới hạn cần nêu trong REFLECTION

Cloud VM không phải laptop của bạn. VM có core count và memory bandwidth khác, chạy
qua hypervisor, và có thể chia sẻ host với workload của người khác. Vì vậy, kết quả
tuning mô tả **VM được cấp**, không mô tả laptop của bạn. Thread-count curve cũng có
thể rất khác máy vật lý.

Hãy nêu giới hạn này trong **REFLECTION §5**. Đây là một phần quan trọng khi diễn giải
số liệu, đặc biệt nếu bạn dùng cloud fallback.
