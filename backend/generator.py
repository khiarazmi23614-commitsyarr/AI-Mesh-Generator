"""Local AI mesh generation backend.

This connector targets Tencent Hunyuan3D-2 / Hunyuan3D-2mini.
The model weights are downloaded by Hugging Face on first use and are NOT stored in Git.
"""

import os
from pathlib import Path


class MeshGenerator:
    def __init__(self):
        self.model_path = os.getenv("HUNYUAN_MODEL", "tencent/Hunyuan3D-2mini")
        self.subfolder = os.getenv("HUNYUAN_SUBFOLDER", "hunyuan3d-dit-v2-mini-turbo")
        self.device = os.getenv("HUNYUAN_DEVICE", "auto")
        self._shape_pipeline = None
        self._text_pipeline = None

    def status(self):
        try:
            import torch  # noqa: F401
            import hy3dgen  # noqa: F401
        except Exception:
            return False, (
                "Hunyuan3D engine is not installed.\n\n"
                "The desktop UI is ready, but the local AI runtime requires the Hunyuan3D "
                "Python package, PyTorch, and a compatible GPU/runtime."
            )

        import torch
        device = "CUDA/NVIDIA GPU" if torch.cuda.is_available() else "CPU"
        return True, f"Hunyuan3D engine detected. Runtime device: {device}."

    def _get_device(self):
        if self.device != "auto":
            return self.device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def _load(self):
        if self._shape_pipeline is not None:
            return

        from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

        device = self._get_device()
        self._shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            self.model_path,
            subfolder=self.subfolder,
            use_safetensors=True,
            device=device,
        )

    def _make_image_from_text(self, prompt):
        if not prompt:
            return None
        if self._text_pipeline is None:
            from hy3dgen.text2image import HunyuanDiTPipeline
            self._text_pipeline = HunyuanDiTPipeline(
                "Tencent-Hunyuan/HunyuanDiT-v1.1-Diffusers-Distilled",
                device=self._get_device(),
            )
        return self._text_pipeline(prompt)

    def generate(self, prompt="", image_path=None, output_format="glb"):
        from pathlib import Path

        if not prompt and not image_path:
            raise ValueError("Provide a prompt or a reference image.")

        self._load()

        image = None
        if image_path:
            from PIL import Image
            image = Image.open(image_path).convert("RGBA")
        else:
            image = self._make_image_from_text(prompt)

        if image is None:
            raise RuntimeError("Could not create an input image for the 3D model.")

        mesh = self._shape_pipeline(image=image, output_type="mesh")[0]

        # Hunyuan3D returns a trimesh-compatible object in normal inference builds.
        out_dir = Path("outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_ext = output_format.lower()
        if safe_ext not in {"glb", "obj"}:
            safe_ext = "glb"
        output = out_dir / "generated_mesh.%s" % safe_ext
        mesh.export(str(output))
        return str(output.resolve())
