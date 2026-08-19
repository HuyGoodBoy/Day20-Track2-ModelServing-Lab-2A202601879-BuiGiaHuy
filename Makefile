## Day 20 - Model Serving & Inference Optimization
## One model (Gemma 4 E2B), one runtime (prebuilt llama.cpp). No compiler, no Docker.

VENV     := .venv
PY       := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
LOCUST   := $(VENV)/bin/locust
SYSPY    := python3

OS := $(shell uname -s 2>/dev/null || echo Windows)

.DEFAULT_GOAL := help

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; \
	      printf "\nDay 20 lab - Model Serving & Inference Optimization\n\nUsage:  make \033[36m<target>\033[0m\n"} \
	      /^## ---/ { printf "\n%s\n", substr($$0, 8); next } \
	      /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\nWindows:  pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1\n"
	@printf "Under 8 GB RAM?  Use cloud/Day20-lab.ipynb on Colab or Kaggle.\n\n"

# Fail early and clearly if setup has not run.
venv-check:
	@test -x $(PY) || { \
	  echo "ERROR: no virtualenv at $(VENV)/. Run: make setup" >&2; exit 1; }

# ─────────────────────────────────────────────────────────────
## --- Setup (00)
# ─────────────────────────────────────────────────────────────

probe: ## Probe hardware -> hardware.json (stdlib only, no install needed)
	@$(SYSPY) labs/00-setup/detect-hardware.py

setup: ## Install deps + fetch llama.cpp runtime + download Gemma 4 E2B (~5.6 GB)
ifeq ($(OS),Windows)
	@echo "On Windows run: pwsh -ExecutionPolicy Bypass -File labs/00-setup/bootstrap.ps1"
	@exit 1
else
	@test -d $(VENV) || $(SYSPY) -m venv $(VENV)
	@$(PY) -m pip install --upgrade pip wheel >/dev/null
	@$(PIP) install -r requirements.txt
	@$(PY) labs/00-setup/setup.py
endif

runtime: venv-check ## Re-fetch just the prebuilt llama.cpp binaries
	@$(PY) labs/00-setup/fetch-runtime.py --force

# ─────────────────────────────────────────────────────────────
## --- Measure (01)
# ─────────────────────────────────────────────────────────────

bench: venv-check ## TTFT / TPOT / P50-P95-P99 for both quantizations
	@$(PY) labs/01-measure/benchmark.py

tune: venv-check ## Thread sweep -> your before/after speedup (REFLECTION section 5)
	@$(PY) labs/01-measure/tune.py

# ─────────────────────────────────────────────────────────────
## --- Serve (02)
# ─────────────────────────────────────────────────────────────

serve: venv-check ## Start llama-server on :8080 (OpenAI-compat + /metrics)
	@$(PY) labs/02-serve/serve.py

serve-embed: venv-check ## Start an embedding server on :8081 (bonus C9)
	@$(PY) labs/02-serve/serve.py --embedding

smoke: venv-check ## Prove /v1/chat/completions + non-zero /metrics (rubric 6 + 7)
	@$(PY) labs/02-serve/smoke-test.py

load-10: venv-check ## Load test: 10 users, 60s
	@$(LOCUST) -f labs/02-serve/load-test.py --headless -u 10 -r 1 -t 1m \
	    --host http://localhost:8080 --csv benchmarks/locust-10 --csv-full-history

load-50: venv-check ## Load test: 50 users, 60s
	@$(LOCUST) -f labs/02-serve/load-test.py --headless -u 50 -r 1 -t 1m \
	    --host http://localhost:8080 --csv benchmarks/locust-50 --csv-full-history

load-report: venv-check ## Turn both load runs into the saturation reading
	@$(PY) labs/02-serve/load-report.py

metrics: venv-check ## Sample /metrics for 60s (run while load-50 is running)
	@$(PY) labs/02-serve/record-metrics.py --duration 60 --label u50

# ─────────────────────────────────────────────────────────────
## --- Integrate (03)
# ─────────────────────────────────────────────────────────────

pipeline: venv-check ## RAG pipeline -> llama-server (server must be up)
	@$(PY) labs/03-integrate/pipeline.py

# ─────────────────────────────────────────────────────────────
## --- Submission
# ─────────────────────────────────────────────────────────────

verify: venv-check ## Check submission readiness (run before you push)
	@$(PY) scripts/verify.py

# ─────────────────────────────────────────────────────────────
## --- Bonus (optional, +20 pts)
# ─────────────────────────────────────────────────────────────

build-llama: venv-check ## B1 - build llama.cpp from source and beat the prebuilt binary
	@bash -c 'set -e; \
	  command -v cmake >/dev/null || { \
	    echo "cmake not found. macOS: brew install cmake · Ubuntu: apt install cmake build-essential" >&2; \
	    exit 1; }; \
	  mkdir -p bonus && cd bonus; \
	  if [ ! -d llama.cpp ]; then \
	    git clone --depth 1 --branch $(shell $(PY) -c "import sys;sys.path.insert(0,\"lib\");import labkit;print(labkit.LLAMA_CPP_BUILD)") \
	      https://github.com/ggml-org/llama.cpp; \
	  fi; \
	  cd llama.cpp; \
	  cmake -B build $(LLAMA_CMAKE_FLAGS) -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release; \
	  cmake --build build -j --config Release'
	@echo ""
	@echo "Built. Now compare it against the prebuilt binary you have been using:"
	@echo "  $(PY) bonus/compare-builds.py"

compare-builds: venv-check ## B1 - prebuilt vs your source build, same model
	@$(PY) bonus/compare-builds.py

sweep-quant: venv-check ## B2 - GGUF quantization ladder (downloads more weights)
	@$(PY) bonus/sweeps/quant-sweep.py

sweep-ctx: venv-check ## B2 - context length vs prefill cost (TTFT curve)
	@$(PY) bonus/sweeps/ctx-len-sweep.py

sweep-batch: venv-check ## B2 - --batch-size / --ubatch-size (chunked prefill)
	@$(PY) bonus/sweeps/batch-size-sweep.py

sweep-gpu: venv-check ## B2 - -ngl GPU offload (needs CUDA/Metal/Vulkan/ROCm)
	@$(PY) bonus/sweeps/gpu-offload-sweep.py

mlx-compare: venv-check ## B5 - MLX vs llama.cpp Metal (Apple Silicon only)
	@$(PY) bonus/mlx/compare-mlx-vs-llama-cpp.py

embed-demo: venv-check ## B5/C9 - embedding serving regime (--offline works serverless)
	@$(PY) bonus/serving-regimes/embedding-serving.py

semantic-cache: venv-check ## B5/C8 - semantic cache above the KV cache
	@$(PY) bonus/serving-regimes/semantic-cache-demo.py

# ─────────────────────────────────────────────────────────────
## --- Housekeeping
# ─────────────────────────────────────────────────────────────

clean: ## Remove generated reports (keeps hardware.json, models, REFLECTION, screenshots)
	@rm -f benchmarks/01-*.md benchmarks/01-*.json \
	       benchmarks/02-*.md benchmarks/02-*.json benchmarks/02-*.csv \
	       benchmarks/locust-*.csv benchmarks/bonus-*.md benchmarks/bonus-*.json
	@find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned generated reports. Kept: hardware.json, models/, runtime/, submission/."

clean-all: clean ## Also remove the venv, runtime binaries, weights and source build
	@rm -rf $(VENV) runtime models bonus/llama.cpp hardware.json
	@echo "Removed venv, runtime, models and hardware.json. Re-run: make setup"

.PHONY: help venv-check probe setup runtime bench tune serve serve-embed smoke \
        load-10 load-50 load-report metrics pipeline verify \
        build-llama compare-builds sweep-quant sweep-ctx sweep-batch sweep-gpu \
        mlx-compare embed-demo semantic-cache clean clean-all
