# Hunyuan3D engine

The application now has a real local inference connector for Tencent Hunyuan3D-2mini.

## What it supports

- Text prompt -> generated reference image -> 3D mesh
- Reference image -> 3D mesh
- GLB and OBJ output
- Model weights are downloaded by the Hunyuan/Hugging Face runtime on first use

## Hardware

The Hunyuan3D project is GPU-oriented. Its 2mini shape model is 0.6B parameters; the official project documents a 6 GB VRAM requirement for its newer shape-generation configuration. CPU execution is technically selectable but is not practical for normal interactive use.

A compatible NVIDIA CUDA GPU is recommended for local generation.

## Local engine setup

Install the Hunyuan3D project and its inference dependencies using the official instructions, then install this application's Python dependencies. The application itself does not put model weights into GitHub.

Official project: https://github.com/Tencent-Hunyuan/Hunyuan3D-2

The desktop GUI can then use:

- `HUNYUAN_MODEL=tencent/Hunyuan3D-2mini`
- `HUNYUAN_SUBFOLDER=hunyuan3d-dit-v2-mini-turbo`
- `HUNYUAN_DEVICE=auto`

The model files should remain in the local Hugging Face cache rather than being committed to this repository.

## Why the EXE does not contain the model

The neural-network weights are large and hardware-specific. Bundling them into a normal Git repository or a small Windows EXE is not practical. PyInstaller can package the Python application itself, while the model runtime/weights are kept separately.
