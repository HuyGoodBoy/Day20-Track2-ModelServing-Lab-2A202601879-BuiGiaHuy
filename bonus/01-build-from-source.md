# Build llama.cpp from source (bonus B1)

You already have a working llama.cpp — `make setup` downloaded the prebuilt release.
So why compile?

**Because the prebuilt binary is compiled for a CPU that might not be yours.** It has
to run on every machine that downloads it, so it targets a conservative baseline
instruction set. Your CPU probably supports more than that (AVX2, AVX-512, or NEON),
and `-DGGML_NATIVE=ON` tells the compiler to use whatever it finds.

That is the experiment: **same source revision, same model, same runtime flags — only
the compiler's assumptions differ.**

```bash
make build-llama       # clone + compile (5-15 min)
make compare-builds    # benchmark both binaries, write the report
```

`compare-builds.py` writes `benchmarks/bonus-build-compare-tg128.md` with a
before/after table and a speedup ratio — that file plus your explanation satisfies
B1, and can also satisfy B3.

---

## 1. What `make build-llama` does

Clones llama.cpp at the pinned build (`b10488`, matching your prebuilt binary so the
comparison is fair) into `bonus/llama.cpp/`, then:

```bash
cmake -B build $LLAMA_CMAKE_FLAGS -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build -j --config Release
```

Prerequisite: **cmake** and a C++ toolchain.

| OS | Install |
|---|---|
| macOS | `xcode-select --install && brew install cmake` |
| Ubuntu/Debian | `sudo apt install cmake build-essential` |
| Fedora | `sudo dnf install cmake gcc-c++` |
| Windows | Visual Studio Build Tools + cmake on PATH |

## 2. Backend flags

Pass extra flags through `LLAMA_CMAKE_FLAGS`. `-DGGML_NATIVE=ON` and
`-DCMAKE_BUILD_TYPE=Release` are always added for you.

### CPU only — the most interesting case for this bonus

```bash
make build-llama          # nothing extra needed
```

`-DGGML_NATIVE=ON` is doing the work. This is where the biggest gap against the
prebuilt binary usually shows up.

### NVIDIA CUDA

```bash
LLAMA_CMAKE_FLAGS="-DGGML_CUDA=ON" make build-llama
```

Needs CUDA Toolkit 12+ (`nvcc --version`). **On Linux this is the only way to get
CUDA at all** — llama.cpp publishes no prebuilt Linux CUDA binary, so your core lab
ran on Vulkan. That makes your comparison a genuine Vulkan-vs-CUDA measurement, which
is challenge **C6** for free.

### Apple Metal

```bash
LLAMA_CMAKE_FLAGS="-DGGML_METAL=ON" make build-llama
```

Metal is already on in the prebuilt macOS-arm64 binary, so expect a *small* gap here —
the win, if any, comes from the CPU-side paths (sampling, tokenization). A near-zero
result is a legitimate finding; say so and explain why.

### AMD ROCm (Linux)

```bash
LLAMA_CMAKE_FLAGS="-DGGML_HIPBLAS=ON -DAMDGPU_TARGETS=gfx1100 \
  -DCMAKE_C_COMPILER=hipcc -DCMAKE_CXX_COMPILER=hipcc" make build-llama
```

Replace `gfx1100` with your target (`rocminfo | grep gfx`). Common: `gfx1030`
(RX 6800/6900), `gfx1100` (RX 7900), `gfx90a`/`gfx942` (Instinct).

### Vulkan

```bash
LLAMA_CMAKE_FLAGS="-DGGML_VULKAN=ON" make build-llama
```

Needs the Vulkan SDK (`vulkaninfo --summary` must work).

## 3. Extra CPU tuning flags worth trying

| Flag | Effect | When |
|---|---|---|
| `-DGGML_NATIVE=ON` | Use the CPU's actual instruction set | Always (added for you) |
| `-DGGML_NATIVE=OFF` | Force a generic baseline build | Challenge C7 — the other side of the comparison |
| `-DGGML_LTO=ON` | Link-time optimization | Cheap, sometimes a few percent |
| `-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS` | External BLAS for prefill | If OpenBLAS/MKL is installed; helps `pp`, rarely `tg` |
| `-DCMAKE_BUILD_TYPE=Release` | `-O3 -DNDEBUG` | Always (added for you) |

**The classic mistake:** comparing a Debug build against a Release build and reporting
the difference as a speedup. `make build-llama` always passes Release so you cannot
make it by accident — but if you build by hand, check.

## 4. Verify your build

```bash
./bonus/llama.cpp/build/bin/llama-cli --version
./bonus/llama.cpp/build/bin/llama-bench \
    -m models/gemma-4-E2B-it-UD-Q4_K_XL.gguf -t 4 -ngl 99
```

`labkit.runtime_bin()` finds `bonus/llama.cpp/` automatically, so once built, every
lab script can use it. `compare-builds.py` deliberately does **not** — it pins each
side explicitly so the comparison stays honest.

## 5. Serve with your own build

```bash
./bonus/llama.cpp/build/bin/llama-server \
    -m models/gemma-4-E2B-it-UD-Q4_K_XL.gguf \
    --host 127.0.0.1 --port 8080 -t <best-from-make-tune> -ngl 99 \
    --parallel 4 --cont-batching --metrics
```

Then re-run `make load-50 && make load-report` and see whether the compile-time win
survives under concurrency. It does not always — and finding out why is a better
writeup than the raw tok/s number.
