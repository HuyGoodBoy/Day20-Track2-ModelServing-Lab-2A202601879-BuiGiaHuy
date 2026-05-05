# Build llama.cpp from source for your hardware

Out-of-the-box `llama-cpp-python` works, but the source build lets you pick CPU instructions, link against the right BLAS, and unlock 1.5–4× speedups. This guide branches by OS and accelerator.

## 1. Clone

```bash
cd BONUS-llama-cpp-optimization
git clone --depth 1 https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

(If GitHub is slow on your network: `git clone --depth 1 https://hf-mirror.com/ggml-org/llama.cpp` works as of 2026.)

## 2. Pick a build profile

Read your `hardware.json` (or just `python ../../00-setup/detect-hardware.py` again) and pick the row whose `llama_cpp_backend` matches yours.

### A. CPU only (any OS)

```bash
# Linux / macOS
cmake -B build -DGGML_NATIVE=ON
cmake --build build -j --config Release
```

```powershell
# Windows (PowerShell, MSVC + cmake on PATH)
cmake -B build -DGGML_NATIVE=ON
cmake --build build -j --config Release
```

`-DGGML_NATIVE=ON` is the single most important flag for CPU builds — it tells cmake to use whatever instruction set extensions your CPU actually supports (AVX2, AVX-512, NEON for ARM). The default prebuilt wheel uses a conservative baseline that ignores these.

### B. NVIDIA CUDA (Linux / Windows / WSL2)

Prerequisites: CUDA Toolkit 12+ (`nvcc --version`), cmake, gcc/MSVC.

```bash
cmake -B build -DGGML_CUDA=ON -DGGML_NATIVE=ON
cmake --build build -j --config Release
```

If you have multiple GPUs, you can also pass `-DGGML_CUDA_F16=ON -DGGML_CUDA_FORCE_MMQ=ON` for slightly faster matrix kernels on Ampere+.

### C. Apple Silicon Metal (macOS arm64)

```bash
cmake -B build -DGGML_METAL=ON -DGGML_NATIVE=ON
cmake --build build -j --config Release
```

Metal is enabled by default on Apple Silicon since 2024, but `-DGGML_NATIVE=ON` still helps the CPU paths (token sampling, etc.).

### D. AMD ROCm (Linux only)

Prerequisites: ROCm 6.x installed and your user in the `render`/`video` groups. RDNA2+ supported.

```bash
cmake -B build -DGGML_HIPBLAS=ON -DAMDGPU_TARGETS=gfx1100 -DGGML_NATIVE=ON \
      -DCMAKE_C_COMPILER=hipcc -DCMAKE_CXX_COMPILER=hipcc
cmake --build build -j --config Release
```

Replace `gfx1100` with your card's target (look it up: `rocminfo | grep gfx`). Common targets: `gfx1030` (RX 6800/6900), `gfx1100` (RX 7900), `gfx900` (Vega).

### E. Vulkan (cross-vendor: Intel Arc, AMD, NVIDIA fallback)

Prerequisites: Vulkan SDK installed (`vulkaninfo --summary` works).

```bash
cmake -B build -DGGML_VULKAN=ON -DGGML_NATIVE=ON
cmake --build build -j --config Release
```

Vulkan is slower than vendor-native (CUDA / Metal / ROCm) but works on basically any modern GPU including integrated Intel/AMD iGPUs. On Intel Arc it's the only good path.

## 3. Verify the build

```bash
./build/bin/llama-cli --version
./build/bin/llama-bench -m ../../models/<your-model>.gguf -t 0 -ngl 0
```

`llama-bench` is the tool the sweep scripts in `benchmarks/` wrap — it's what you should run by hand the first time to make sure things work before kicking off automated sweeps.

## 4. CPU-only tuning checklist

Even before running the sweep scripts, these are the easy CPU wins:

| Flag | Effect | When |
|---|---|---|
| `-DGGML_NATIVE=ON` | Use AVX2/AVX-512/NEON if present | Always |
| `-DGGML_OPENMP=ON` | OpenMP parallelism (default ON Linux) | Linux/macOS multi-thread |
| `-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS` | OpenBLAS for prefill | If you have OpenBLAS or MKL |
| `-DGGML_LTO=ON` | Link-time optimization | Slightly faster binary |
| `-DCMAKE_BUILD_TYPE=Release` | -O3 -DNDEBUG | Always (cmake `--config Release` does this) |

A common newbie mistake is comparing a Debug-built binary to a Release-built one and reporting the gap as a "speedup". Don't.

## 5. After building

Update `models/active.json` is unchanged — it points at the GGUF file paths, which are independent of which binary serves them. Then:

```bash
# from repo root
./BONUS-llama-cpp-optimization/llama.cpp/build/bin/llama-bench \
    -m models/<your-model>.gguf -t 0 -ngl 99
```

Note your tokens/sec — that's the **before** number. The sweep scripts in `benchmarks/` produce **after** numbers.
