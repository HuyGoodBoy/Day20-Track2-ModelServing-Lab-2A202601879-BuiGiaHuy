#!/usr/bin/env python3
"""Download the lab model: Gemma 4 E2B, two quantizations.

One model for the whole lab. Two quantizations because the quantization
comparison (deck section 1) needs a before/after on the same weights:

    primary  gemma-4-E2B-it-UD-Q4_K_XL.gguf   ~3.2 GB   the default
    compare  gemma-4-E2B-it-UD-Q2_K_XL.gguf   ~2.4 GB   the contrast

Unsloth's UD ("Unsloth Dynamic") quants keep the sensitive layers at higher
precision, so UD-Q2_K_XL is far more usable than a flat Q2_K -- which is exactly
what makes the comparison interesting rather than a foregone conclusion.

    python labs/00-setup/download-model.py                # both quants
    python labs/00-setup/download-model.py --with-mtp     # + MTP head (bonus C1)
    python labs/00-setup/download-model.py --skip-download  # manifest only
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
import labkit  # noqa: E402


def find_local(models_dir: pathlib.Path, filename: str) -> pathlib.Path | None:
    for p in models_dir.rglob(filename):
        if p.is_file():
            return p
    return None


def fetch(repo_id: str, filename: str, models_dir: pathlib.Path) -> pathlib.Path:
    from huggingface_hub import hf_hub_download

    existing = find_local(models_dir, filename)
    if existing:
        print(f"    already present: {existing.relative_to(labkit.repo_root())}")
        return existing
    print(f"==> Downloading {filename}")
    return pathlib.Path(
        hf_hub_download(repo_id=repo_id, filename=filename, local_dir=str(models_dir))
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Download the Gemma 4 E2B GGUFs for the lab.")
    ap.add_argument("--skip-download", action="store_true",
                    help="Locate already-downloaded files and write the manifest only")
    ap.add_argument("--with-mtp", action="store_true",
                    help="Also fetch the MTP head (~98 MB) for bonus C1 speculative decoding")
    args = ap.parse_args()

    models_dir = labkit.repo_root() / "models"
    models_dir.mkdir(exist_ok=True)
    repo = labkit.MODEL_REPO

    wanted = [labkit.MODEL_PRIMARY, labkit.MODEL_COMPARE]
    if args.with_mtp:
        wanted.append(labkit.MODEL_MTP)

    resolved: dict[str, pathlib.Path] = {}
    if args.skip_download:
        for f in wanted:
            found = find_local(models_dir, f)
            if not found:
                labkit.die(
                    f"--skip-download but {f} is not under models/.",
                    "Drop it in manually first -- see labs/00-setup/MANUAL-DOWNLOAD.md",
                )
            print(f"==> Found {found.relative_to(labkit.repo_root())}")
            resolved[f] = found
    else:
        try:
            for f in wanted:
                resolved[f] = fetch(repo, f, models_dir)
        except ImportError:
            labkit.die("huggingface_hub not installed.", "Run: make setup")
        except Exception as exc:  # noqa: BLE001 -- surface the real cause to the student
            labkit.die(
                f"Download failed: {exc}",
                "Network blocked? See labs/00-setup/MANUAL-DOWNLOAD.md for the browser path.",
            )

    def rel(p: pathlib.Path) -> str:
        try:
            return str(p.resolve().relative_to(labkit.repo_root()))
        except ValueError:
            return str(p.resolve())

    manifest = {
        "model": "gemma-4-E2B-it",
        "repo_id": repo,
        "primary_model": rel(resolved[labkit.MODEL_PRIMARY]),
        "primary_quant": "UD-Q4_K_XL",
        "compare_model": rel(resolved[labkit.MODEL_COMPARE]),
        "compare_quant": "UD-Q2_K_XL",
        "mtp_head": rel(resolved[labkit.MODEL_MTP]) if args.with_mtp else None,
        "mlx_repo": labkit.MLX_REPO,
    }
    labkit.active_json().parent.mkdir(exist_ok=True)
    labkit.active_json().write_text(json.dumps(manifest, indent=2))

    total_gb = sum(p.stat().st_size for p in resolved.values()) / 1024**3
    print(f"\n==> Wrote models/active.json  ({total_gb:.1f} GB on disk)")
    for f, p in resolved.items():
        print(f"    {p.stat().st_size / 1024**3:5.2f} GB  {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
