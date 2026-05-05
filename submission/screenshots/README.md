# Required screenshots

Drop the following PNG/JPG files into this folder before submitting. Filenames are suggested, not required — grader reads `REFLECTION.md` to map screenshots to evidence.

## Minimum (6 shots)

1. **`01-hardware-probe.png`** — terminal output of `python 00-setup/detect-hardware.py`. Must show CPU, RAM, accelerator, recommended model tier.
2. **`02-quickstart-bench.png`** — terminal output of `python 01-llama-cpp-quickstart/benchmark.py` showing the per-prompt TTFT/TPOT/E2E table.
3. **`03-server-running.png`** — `llama-server` running (terminal showing `listening on http://0.0.0.0:8080`) **plus** a `curl http://localhost:8080/metrics | head -30` excerpt.
4. **`04-locust-10.png`** — locust headless summary table after `-u 10 -t 1m`. Must show RPS + P50/P95/P99.
5. **`05-locust-50.png`** — same but `-u 50 -t 1m`.
6. **`06-bonus-sweep.png`** — at least one chart or terminal table from `BONUS-llama-cpp-optimization/benchmarks/*.py` (thread / quant / ctx-len / gpu-offload / batch-size). Pick the one with the most interesting result on your hardware.

## Optional (extra credit, mentioned in `rubric.md`)

7. **`07-grafana-or-prom.png`** — if you ran the optional Prometheus container, show a Grafana panel or the Prometheus query UI with `llamacpp:kv_cache_usage_ratio` plotted.
8. **`08-mlx-vs-llamacpp.png`** — Apple Silicon students who ran the MLX bonus.
9. **`09-pipeline-output.png`** — `python 03-milestone-integration/pipeline.py` end-to-end output.

## Tips

- Crop tight — full-screen browser shots get rejected. The grader wants to see the data, not your wallpaper.
- Dark or light terminal both fine; just make sure text is readable.
- For load-test screenshots, include the locust *Type · Name · # reqs · Median · Avg · 95%ile · 99%ile* row — that's the rubric evidence.
