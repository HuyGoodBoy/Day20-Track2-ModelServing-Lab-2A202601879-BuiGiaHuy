# Hardware Guide

> **Laptop của bạn *là* lab.** Không có shared sandbox. Rubric thưởng độ rõ ràng
> của *your own before/after*, không phải absolute throughput. Đừng so số với bạn
> cùng lớp — so với `make bench` lần đầu của chính bạn.

## 1. Điều kiện tối thiểu

| | Yêu cầu |
|---|---|
| RAM | **8 GB** (bắt buộc) |
| Đĩa trống | ~10 GB (5.6 GB model + 0.5 GB runtime/deps + chỗ thở) |
| Python | ≥ 3.10 |
| GPU | **không cần** |
| Compiler | **không cần** (chỉ bonus B1 mới cần cmake) |
| Docker | **không cần bao giờ** |

**RAM < 8 GB?** Dùng [`cloud/`](cloud/README.md) (Colab hoặc Kaggle) và khai báo ở
REFLECTION §1. Điểm không bị ảnh hưởng — rubric chấm lập luận, không chấm phần cứng.

## 2. Model — một model duy nhất cho cả lab

[`unsloth/gemma-4-E2B-it-GGUF`](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF)
· Apache-2.0 · **không gated** (không cần token, không cần bấm accept license).

| Vai trò | File | Kích thước |
|---|---|--:|
| primary | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | ~3.2 GB |
| compare | `gemma-4-E2B-it-UD-Q2_K_XL.gguf` | ~2.4 GB |
| bonus C1 | `mtp-gemma-4-E2B-it.gguf` (MTP head) | ~98 MB |
| bonus B5 | `unsloth/gemma-4-E2B-it-UD-MLX-4bit` (MLX format) | tải riêng |

**"E2B"** = *effective* 2B tham số. Gemma 4 E2B dùng per-layer embeddings, nên tổng
số tham số lớn hơn 2B nhưng chi phí tính toán mỗi token tương đương một model 2B.
Đó là lý do file 4-bit ~3.2 GB chứ không phải ~1.2 GB. Unsloth ghi nhận E2B 4-bit
cần **~4 GB** RAM khi inference — vừa đủ thoải mái trên 8 GB.

**"UD"** = Unsloth Dynamic: các layer nhạy cảm được giữ ở precision cao hơn. Nhờ vậy
`UD-Q2_K_XL` dùng được thật, khác với `Q2_K` phẳng thường hỏng hẳn — làm cho phần so
sánh quantization ở §1 trở thành câu hỏi mở, không phải kết luận biết trước.

Cả lab chỉ cần 2 file trên. Bonus `make sweep-quant` mới tải thêm.

## 3. Runtime — prebuilt, không compile

`labs/00-setup/fetch-runtime.py` đọc `hardware.json`, hỏi GitHub release API của
llama.cpp (pin ở build **`b10488`**), rồi chọn asset đúng cho máy bạn:

| Máy | Asset được chọn | Tải về |
|---|---|--:|
| macOS Apple Silicon | `bin-macos-arm64` (Metal có sẵn) | 11 MB |
| macOS Intel | `bin-macos-x64` | ~12 MB |
| Linux x64, CPU | `bin-ubuntu-x64` | 16 MB |
| Linux x64 + GPU bất kỳ | `bin-ubuntu-vulkan-x64` | 32 MB |
| Linux ARM64 | `bin-ubuntu-arm64` | ~15 MB |
| Windows x64, CPU | `bin-win-cpu-x64` | 18 MB |
| Windows + NVIDIA | `bin-win-cuda-<ver>-x64` + CUDA runtime DLLs | ~140–240 MB |
| Windows + AMD | `bin-win-rocm-7.14-x64` | 188 MB |
| Windows ARM64 | `bin-win-cpu-arm64` | ~17 MB |

Với NVIDIA trên Windows, script đọc CUDA version mà driver hỗ trợ (`nvidia-smi`) và
chọn build cao nhất mà driver chạy được, kèm `cudart` DLLs.

> **Linux + NVIDIA:** llama.cpp **không** publish prebuilt CUDA cho Linux. Script sẽ
> chọn **Vulkan** — chạy tốt trên NVIDIA, chỉ chậm hơn CUDA một chút. Muốn CUDA thật
> thì compile: `LLAMA_CMAKE_FLAGS=-DGGML_CUDA=ON make build-llama`. Đây chính là
> bonus **C6** (Vulkan vs CUDA head-to-head) — bạn có sẵn cả hai để so.

Ghi đè lựa chọn tự động:

```bash
python labs/00-setup/fetch-runtime.py --list                       # xem hết asset
python labs/00-setup/fetch-runtime.py --asset <tên> --force        # chọn tay
```

## 4. Backend nào cho phần cứng nào

| Accelerator | Prebuilt có? | cmake flag (bonus B1) |
|---|---|---|
| CPU (mọi OS) | ✅ luôn có | *(default)* + `-DGGML_NATIVE=ON` |
| Apple Metal | ✅ trong build macOS-arm64 | `-DGGML_METAL=ON` |
| NVIDIA CUDA | ✅ Windows · ❌ Linux (dùng Vulkan) | `-DGGML_CUDA=ON` |
| AMD ROCm | ✅ Windows · ❌ Linux (dùng Vulkan) | `-DGGML_HIPBLAS=ON` |
| Vulkan (Intel Arc, AMD, NVIDIA) | ✅ Linux + Windows | `-DGGML_VULKAN=ON` |

`make probe` đã chọn giúp bạn — cột cmake chỉ dùng khi làm bonus B1.

## 5. Nếu laptop bạn là máy yếu nhất lớp

Đó là **lợi thế** ở bonus track, không phải bất lợi:

- `make tune` (core) — thread count là knob lớn nhất trên CPU. Curve rõ nhất trên
  máy nhiều core nhưng bandwidth hẹp.
- `make build-llama && make compare-builds` (B1) — prebuilt binary được compile cho
  CPU baseline chung. Build riêng cho CPU của bạn với `-DGGML_NATIVE=ON` thường là
  speedup lớn nhất cả lab, và **càng rõ trên máy yếu**.
- `make sweep-quant` (B2) — RAM chật thì đây là quyết định thật, không phải bài tập.

## 6. Network

- Hugging Face có thể bị chặn ở mạng trường. Nếu `make setup` fail ở bước model,
  xem [`labs/00-setup/MANUAL-DOWNLOAD.md`](labs/00-setup/MANUAL-DOWNLOAD.md).
- GitHub release API giới hạn 60 request/giờ/IP. Cả lớp cùng NAT có thể chạm giới
  hạn — script tự fallback sang bảng tên asset có sẵn, nên vẫn tải được.
- Không có Docker pull nào trong toàn bộ lab.

## 7. MLX, MLC, ExecuTorch?

**MLX** là bonus B5 cho Apple Silicon — Unsloth publish Gemma 4 E2B ở cả GGUF và
MLX, nên đó là so sánh *runtime* thật (cùng model, cùng 4-bit), không phải so hai
model khác nhau. MLC LLM / ExecuTorch / Core ML được deck nhắc nhưng không build vào
lab; chọn làm stretch project nếu bạn xong sớm.
