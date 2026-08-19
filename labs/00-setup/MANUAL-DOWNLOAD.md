# Manual model download

If `make setup` cannot reach Hugging Face (university firewall, captive portal, slow
link), download the two GGUF files in a browser and drop them into `models/`.

## What you need

Repo: **[unsloth/gemma-4-E2B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/tree/main)**
— Apache-2.0, **not gated**, no login required.

| Role | File | Size |
|---|---|--:|
| primary | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | ~3.0 GB |
| compare | `gemma-4-E2B-it-UD-Q2_K_XL.gguf` | ~2.2 GB |
| optional (bonus C1) | `mtp-gemma-4-E2B-it.gguf` | ~98 MB |

## Steps

1. Open the repo link above, click **Files and versions**.
2. Download both files (the ⬇ icon next to each).
3. Put them anywhere under `models/` in the repo root — subfolders are fine, the
   script searches recursively.
4. Write the manifest:

   ```bash
   python labs/00-setup/download-model.py --skip-download
   ```

   That produces `models/active.json` pointing at the files it found. Add
   `--with-mtp` if you also grabbed the MTP head.

5. Confirm:

   ```bash
   make verify        # should now pass the "Model manifest" check
   ```

## If the filenames do not match

`--skip-download` looks for the exact names in the table above. Unsloth occasionally
re-uploads with different quant labels. If yours differ, either rename your files to
match, or edit `MODEL_PRIMARY` / `MODEL_COMPARE` at the top of
[`lib/labkit.py`](../../lib/labkit.py) and say so in REFLECTION §1.

## Mirrors

- `hf-mirror.com` — same paths, e.g.
  `https://hf-mirror.com/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf`
- ModelScope mirrors many GGUF repos
- Ask your instructor — a USB copy is the fastest option in a room with one uplink

## The runtime binaries too?

`fetch-runtime.py` pulls from GitHub releases, which is usually reachable when HF is
not. If it is also blocked:

```bash
python labs/00-setup/fetch-runtime.py --list      # print the asset names
```

Download the asset for your platform from
<https://github.com/ggml-org/llama.cpp/releases/tag/b10488> and extract it into
`runtime/b10488/`. Any internal folder layout works — the lab globs for the binary.
