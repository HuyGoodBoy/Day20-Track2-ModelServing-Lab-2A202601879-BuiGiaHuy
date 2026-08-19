#!/usr/bin/env python3
"""Pre-submission check. Run `make verify` before you push.

Checks what is *committed*, because that is all the grader can see. Large local
artifacts (the GGUF weights, the runtime binaries) are gitignored by design, so
their absence is reported as information, never as a failure -- otherwise this
script could never pass on a fresh clone, which is exactly what the grader does.

Exit 0 means your repo is ready. Exit 1 prints the checklist of what is missing.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import labkit  # noqa: E402

MIN_SCREENSHOTS = 5

# Placeholders left behind by the REFLECTION template.
TEMPLATE_MARKERS = [
    r"<Họ Tên>",
    r"<A20-K1 / A20-K2",
    r"<YYYY-MM-DD>",
    r"<macOS 14 / Windows 11",
    r"^_Answer here\._?\s*$",
]
# Every generated report ends with a section the student must replace.
UNANSWERED = re.compile(r"required -- replace this line", re.IGNORECASE)

OK, WARN, BAD = "  ✓", "  •", "  ✗"


class Report:
    def __init__(self) -> None:
        self.problems: list[str] = []
        self.notes: list[str] = []

    def fail(self, msg: str) -> None:
        self.problems.append(msg)
        print(f"{BAD} {msg}")

    def ok(self, msg: str) -> None:
        print(f"{OK} {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)
        print(f"{WARN} {msg}")


def need_file(r: Report, path: pathlib.Path, label: str, how: str) -> pathlib.Path | None:
    rel = path.relative_to(labkit.repo_root())
    if not path.exists():
        r.fail(f"{label}: {rel} is missing — run `{how}`")
        return None
    if path.stat().st_size == 0:
        r.fail(f"{label}: {rel} is empty — run `{how}`")
        return None
    if path.suffix == ".md" and UNANSWERED.search(path.read_text()):
        r.fail(f"{label}: {rel} still has an unanswered 'replace this line' section")
        return None
    r.ok(f"{label}: {rel}")
    return path


def any_file(r: Report, patterns: list[str], label: str, how: str) -> bool:
    root = labkit.repo_root()
    hits = [p for pat in patterns for p in sorted(root.glob(pat)) if p.stat().st_size > 0]
    if not hits:
        r.fail(f"{label}: none of {patterns} found — run `{how}`")
        return False
    stale = [p for p in hits if p.suffix == ".md" and UNANSWERED.search(p.read_text())]
    if stale and len(stale) == len([p for p in hits if p.suffix == ".md"]):
        r.fail(f"{label}: {stale[0].relative_to(root)} still has an unanswered section")
        return False
    r.ok(f"{label}: {', '.join(str(p.relative_to(root)) for p in hits[:3])}")
    return True


def check_manifest(r: Report) -> None:
    path = labkit.active_json()
    if not path.exists():
        r.fail("Model manifest: models/active.json is missing — run `make setup`")
        return
    try:
        cfg = json.loads(path.read_text())
    except ValueError as exc:
        r.fail(f"Model manifest: models/active.json is not valid JSON — {exc}")
        return
    missing = [k for k in ("model", "repo_id", "primary_model", "compare_model") if not cfg.get(k)]
    if missing:
        r.fail(f"Model manifest: models/active.json lacks {missing} — re-run `make setup`")
        return
    r.ok(f"Model manifest: {cfg['model']} ({cfg.get('primary_quant')} + {cfg.get('compare_quant')})")

    # Weights are gitignored, so their absence is not a submission problem.
    for key in ("primary_model", "compare_model"):
        p = labkit.repo_root() / cfg[key]
        if not p.exists():
            r.note(f"{cfg[key]} not on this machine (fine — weights are gitignored)")


def check_reflection(r: Report) -> None:
    path = labkit.repo_root() / "submission" / "REFLECTION.md"
    if not path.exists():
        r.fail("Reflection: submission/REFLECTION.md is missing")
        return
    text = path.read_text()
    left = [
        p for p in TEMPLATE_MARKERS
        if re.search(p, text, re.MULTILINE if p.startswith("^") else 0)
    ]
    if left:
        r.fail(
            f"Reflection: submission/REFLECTION.md still has {len(left)} template "
            f"placeholder(s) — fill in your own numbers and answers"
        )
        return
    words = len(text.split())
    if words < 400:
        r.fail(f"Reflection: only {words} words — sections 3, 4 and 5 need real content")
        return
    r.ok(f"Reflection: submission/REFLECTION.md filled in ({words} words)")


def check_screenshots(r: Report) -> None:
    folder = labkit.repo_root() / "submission" / "screenshots"
    if not folder.exists():
        r.fail("Screenshots: submission/screenshots/ is missing")
        return
    imgs = [p for p in folder.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    if len(imgs) < MIN_SCREENSHOTS:
        r.fail(
            f"Screenshots: {len(imgs)} of {MIN_SCREENSHOTS} required — "
            f"see submission/screenshots/README.md"
        )
        return
    r.ok(f"Screenshots: {len(imgs)} image(s)")


def check_runtime(r: Report) -> None:
    """Informational: the grader will not have these, and does not need them."""
    server = labkit.runtime_bin("llama-server", required=False)
    if server:
        r.ok(f"Runtime: llama-server present ({labkit.LLAMA_CPP_BUILD})")
    else:
        r.note("llama-server not on this machine (fine — runtime/ is gitignored)")


def main() -> int:
    r = Report()
    root = labkit.repo_root()
    print(f"==> Verifying submission readiness in {root}\n")

    print("Setup (00)")
    need_file(r, root / "hardware.json", "Hardware probe", "make probe")
    check_manifest(r)
    check_runtime(r)

    print("\nMeasure (01)")
    need_file(r, root / "benchmarks" / "01-quickstart-results.md",
              "Latency baseline", "make bench")
    any_file(r, ["benchmarks/01-tuning-*.md"], "Tuning sweep", "make tune")

    print("\nServe (02)")
    need_file(r, root / "benchmarks" / "02-server-results.md",
              "Load test + saturation reading", "make load-10 && make load-50 && make load-report")
    any_file(r, ["benchmarks/02-server-batching*.md", "benchmarks/02-server-metrics*.csv"],
             "Continuous-batching evidence", "make metrics (while make load-50 runs)")

    print("\nSubmission")
    check_reflection(r)
    check_screenshots(r)

    print()
    if r.problems:
        print(f"✗ Not ready — {len(r.problems)} item(s) to fix:\n")
        for p in r.problems:
            print(f"  - {p}")
        print("\nSee rubric.md for what each item is worth. Re-run `make verify` when fixed.")
        return 1

    print("✓ All checks passed.")
    if r.notes:
        print(f"  ({len(r.notes)} informational note(s) above — none block submission.)")
    print("\n  Next: commit, push to a PUBLIC GitHub repo, paste the URL into the LMS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
