# AI Mesh Generator

Windows desktop app for generating 3D meshes with an AI backend.

## Status

Initial project scaffold. The application is designed for text/image-to-3D generation, local preview, and GLB/OBJ export.

## Architecture

- `app/` - desktop UI and 3D preview
- `backend/` - AI generation service integration
- `scripts/` - build helpers
- `.github/workflows/` - Windows build pipeline

## Important

The repository contains the application shell and integration points. A production-quality text-to-3D model requires a compatible 3D generation model and GPU/runtime; the app does not pretend to generate AI meshes without such a model.
