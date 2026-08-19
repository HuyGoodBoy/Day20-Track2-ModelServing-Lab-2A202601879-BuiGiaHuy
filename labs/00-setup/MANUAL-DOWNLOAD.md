# Tải model thủ công

Dùng trang này khi `make setup` không tải được model (mạng trường chặn Hugging Face,
captive portal, mạng quá chậm).

## Model của lab

**[unsloth/gemma-4-E2B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF)**
— Apache-2.0, **không gated**: không cần login, không cần token, không cần accept license.

Xem toàn bộ file: **[tree/main](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/tree/main)**

| Vai trò | File | Size |
|---|---|--:|
| primary (bắt buộc) | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | 2.97 GB |
| compare (bắt buộc) | `gemma-4-E2B-it-UD-Q2_K_XL.gguf` | 2.24 GB |
| bonus C1 (optional) | `mtp-gemma-4-E2B-it.gguf` | 0.09 GB |

Bạn cần **hai file đầu**. Thiếu file `compare` thì mất hàng thứ hai của rubric 3–5.

## Cách 1 — curl / wget

Chạy ở **repo root**:

```bash
mkdir -p models

curl -L -o models/gemma-4-E2B-it-UD-Q4_K_XL.gguf \
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf

curl -L -o models/gemma-4-E2B-it-UD-Q2_K_XL.gguf \
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q2_K_XL.gguf
```

`-L` là bắt buộc — Hugging Face redirect sang CDN. Nếu bị ngắt giữa đường, thêm `-C -`
để tiếp tục thay vì tải lại từ đầu:

```bash
curl -L -C - -o models/gemma-4-E2B-it-UD-Q4_K_XL.gguf \
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf
```

Windows PowerShell:

```powershell
mkdir models -Force
curl.exe -L -o models\gemma-4-E2B-it-UD-Q4_K_XL.gguf `
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf
curl.exe -L -o models\gemma-4-E2B-it-UD-Q2_K_XL.gguf `
  https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q2_K_XL.gguf
```

## Cách 2 — mirror (khi Hugging Face bị chặn hẳn)

`hf-mirror.com` dùng **đúng đường dẫn**, chỉ đổi hostname:

```bash
curl -L -o models/gemma-4-E2B-it-UD-Q4_K_XL.gguf \
  https://hf-mirror.com/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf
```

Hoặc set biến môi trường rồi để script tự tải như bình thường:

```bash
HF_ENDPOINT=https://hf-mirror.com make setup
```

## Cách 3 — browser

Mở [tree/main](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/tree/main), bấm icon ⬇
cạnh hai file, rồi copy chúng vào `models/` trong repo. Thư mục con thoải mái — script
tìm đệ quy.

## Sau khi có file: ghi manifest

```bash
python labs/00-setup/download-model.py --skip-download
```

Lệnh này không tải gì, chỉ tìm file và ghi `models/active.json` (rubric item 2). Thêm
`--with-mtp` nếu bạn cũng tải MTP head.

Kiểm tra:

```bash
make verify      # mục "Model manifest" phải PASS
```

## Kiểm tra file có nguyên vẹn không

Nếu server báo lỗi lạ khi load model, khả năng cao file bị tải thiếu. So size:

```bash
ls -l models/*.gguf
```

Phải khớp bảng ở trên (2.97 GB và 2.24 GB). File nhỏ hơn đáng kể = tải dở, xoá và tải lại.

## Nếu tên file không khớp

`--skip-download` tìm đúng tên trong bảng trên. Unsloth đôi khi re-upload với nhãn quant
khác. Khi đó: đổi tên file cho khớp, **hoặc** sửa `MODEL_PRIMARY` / `MODEL_COMPARE` ở đầu
[`lib/labkit.py`](../../lib/labkit.py) và ghi lại việc đó trong REFLECTION §1.

## Runtime binary cũng bị chặn?

`fetch-runtime.py` tải từ GitHub Releases, thường thông khi Hugging Face bị chặn. Nếu cả
GitHub cũng bị chặn:

```bash
python labs/00-setup/fetch-runtime.py --list      # in ra tên các asset
```

Tải asset đúng platform của bạn từ
<https://github.com/ggml-org/llama.cpp/releases/tag/b10488> rồi giải nén vào
`runtime/b10488/`. Layout bên trong không quan trọng — lab tìm binary bằng glob.

## Vẫn không được?

Máy dưới 8 GB RAM hoặc mạng không thông: dùng [`cloud/`](../../cloud/README.md)
(Colab / Kaggle). Điểm không bị ảnh hưởng, chỉ cần khai báo ở REFLECTION §1.
