"""Local AI mesh generation backend."""

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
            import torch
            import hy3dgen  # noqa: F401
        except Exception:
            return False, (
                "Hunyuan3D engine is not installed.\n\n"
                "The desktop UI is ready, but the local AI runtime requires the Hunyuan3D "
                "Python package, PyTorch, and a compatible GPU/runtime."
            )
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

    def _load(self, progress_callback=None):
        if self._shape_pipeline is not None:
            return
        if progress_callback:
            progress_callback(15, "Loading Hunyuan3D model...")
        from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
        device = self._get_device()
        self._shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            self.model_path,
            subfolder=self.subfolder,
            use_safetensors=True,
            device=device,
        )

    def _make_image_from_text(self, prompt, progress_callback=None):
        if not prompt:
            return None
        if self._text_pipeline is None:
            if progress_callback:
                progress_callback(30, "Creating reference image from prompt...")
            from hy3dgen.text2image import HunyuanDiTPipeline
            self._text_pipeline = HunyuanDiTPipeline(
                "Tencent-Hunyuan/HunyuanDiT-v1.1-Diffusers-Distilled",
                device=self._get_device(),
            )
        return self._text_pipeline(prompt)

    def generate(self, prompt="", image_path=None, output_format="glb", progress_callback=None):
        if not prompt and not image_path:
            raise ValueError("Provide a prompt or a reference image.")

        def progress(value, text):
            if progress_callback:
                progress_callback(value, text)

        progress(5, "Preparing generation...")
        self._load(progress)

        image = None
        if image_path:
            progress(35, "Loading reference image...")
            from PIL import Image
            image = Image.open(image_path).convert("RGBA")
        else:
            image = self._make_image_from_text(prompt, progress)

        if image is None:
            raise RuntimeError("Could not create an input image for the 3D model.")

        progress(55, "Generating 3D mesh... this can take a while.")
        mesh = self._shape_pipeline(image=image, output_type="mesh")[0]

        progress(90, "Exporting mesh...")
        out_dir = Path("outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_ext = output_format.lower()
        if safe_ext not in {"glb", "obj"}:
            safe_ext = "glb"
        output = out_dir / "generated_mesh.%s" % safe_ext
        mesh.export(str(output))
        progress(98, "Loading generated mesh into viewer...")
        return str(output.resolve())
