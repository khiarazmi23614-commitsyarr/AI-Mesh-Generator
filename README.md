# AI Mesh Generator

Windows desktop application for AI-assisted 3D mesh generation.

## Current version

The GUI is now connected to a real local Hunyuan3D inference adapter.

### Features

- Text prompt -> reference image -> 3D mesh
- Reference image -> 3D mesh
- GLB / OBJ export
- Background generation thread so the UI stays responsive
- Hunyuan3D model selection through environment variables
- Windows EXE build through GitHub Actions

## Architecture

```text
Prompt / Image
      |
      v
AI Mesh Generator GUI
      |
      v
backend/generator.py
      |
      v
Tencent Hunyuan3D-2mini
      |
      v
   GLB / OBJ
```

## AI engine

The connector targets Tencent Hunyuan3D-2mini by default. The model weights are intentionally not stored in this repository; they are downloaded by the local ML runtime when configured.

See `backend/HUNYUAN_ENGINE.md` for engine requirements and setup notes.

The official Hunyuan3D project supports text-to-3D by creating an image from the text prompt and then running image-to-3D shape generation.

## Hardware note

Local 3D generation is GPU-intensive. The Hunyuan3D project documents dedicated VRAM requirements for shape generation, and its smaller 2mini models are intended to reduce resource use. A compatible NVIDIA GPU is recommended for practical local inference.

## Windows EXE

GitHub Actions builds `AI-Mesh-Generator.exe` automatically on pushes to `main` and can also be started manually from the Actions page.

PyInstaller packages the application and its Python runtime so the GUI itself does not require a separate Python installation.

## License notice

If distributing an application that uses Hunyuan3D, review and comply with the model's applicable license and notices. Do not commit model weights into this repository.
