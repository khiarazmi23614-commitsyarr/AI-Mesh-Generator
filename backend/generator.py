"""AI 3D generation integration point.

Connect this module to a compatible text-to-3D/image-to-3D model runtime.
The UI intentionally does not fake generation when no model is installed.
"""

class MeshGenerator:
    def __init__(self, model=None):
        self.model = model

    def generate(self, prompt: str, output_path: str):
        if self.model is None:
            raise RuntimeError(
                "No 3D generation model is configured. Install/configure a compatible "
                "text-to-3D model and connect it here."
            )
        return self.model.generate(prompt, output_path)
