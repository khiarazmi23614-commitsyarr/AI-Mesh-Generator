import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Make the repository root importable both from source and from the PyInstaller build.
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.generator import MeshGenerator

APP_NAME = "AI Mesh Generator"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x700")
        self.minsize(820, 600)
        self.generator = MeshGenerator()
        self.output_path = None
        self.reference_image = None
        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text=APP_NAME, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(root, text="AI text/image → 3D mesh", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 14))

        prompt_box = ttk.LabelFrame(root, text="Prompt")
        prompt_box.pack(fill="x", pady=(0, 10))
        self.prompt = tk.Text(prompt_box, height=4, font=("Segoe UI", 11))
        self.prompt.pack(fill="x", padx=10, pady=10)
        self.prompt.insert("1.0", "a cute low-poly robot toy, clean shape, studio lighting")

        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(0, 10))

        ttk.Label(controls, text="Reference image:").pack(side="left")
        self.image_var = tk.StringVar(value="None")
        ttk.Label(controls, textvariable=self.image_var, width=28).pack(side="left", padx=6)
        ttk.Button(controls, text="Choose", command=self.choose_image).pack(side="left")

        ttk.Label(controls, text="Format:").pack(side="left", padx=(18, 4))
        self.format = ttk.Combobox(controls, values=["GLB", "OBJ"], state="readonly", width=7)
        self.format.set("GLB")
        self.format.pack(side="left")

        self.generate_button = ttk.Button(controls, text="Generate Mesh", command=self.generate)
        self.generate_button.pack(side="left", padx=12)

        self.status = ttk.Label(root, text="Ready — Hunyuan3D backend connector available")
        self.status.pack(anchor="w", pady=(0, 10))

        preview = ttk.LabelFrame(root, text="3D Preview")
        preview.pack(fill="both", expand=True)
        self.preview_text = ttk.Label(
            preview,
            text="Generated mesh information will appear here.\n\nThe full Hunyuan3D viewer is enabled when the AI engine is installed.",
            anchor="center",
            justify="center",
        )
        self.preview_text.pack(expand=True)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="Open Output Folder", command=self.open_output).pack(side="left")
        ttk.Button(bottom, text="Engine Status", command=self.engine_status).pack(side="right")

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choose reference image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if path:
            self.image_var.set(os.path.basename(path))
            self.reference_image = path
        else:
            self.reference_image = None

    def generate(self):
        prompt = self.prompt.get("1.0", "end").strip()
        image = self.reference_image
        if not prompt and not image:
            messagebox.showwarning(APP_NAME, "Enter a prompt or choose a reference image.")
            return

        self.generate_button.config(state="disabled")
        self.status.config(text="Generating with the AI engine...")
        threading.Thread(target=self._generate_worker, args=(prompt, image), daemon=True).start()

    def _generate_worker(self, prompt, image):
        try:
            ext = self.format.get().lower()
            path = self.generator.generate(prompt=prompt, image_path=image, output_format=ext)
            self.output_path = path
            self.after(0, lambda: self._generation_done(path))
        except Exception as exc:
            self.after(0, lambda: self._generation_error(str(exc)))

    def _generation_done(self, path):
        self.generate_button.config(state="normal")
        self.status.config(text=f"Generated: {path}")
        self.preview_text.config(text=f"Mesh generated successfully.\n\n{path}\n\nOpen the output folder to inspect the model.")

    def _generation_error(self, error):
        self.generate_button.config(state="normal")
        self.status.config(text="Generation failed")
        messagebox.showerror(APP_NAME, error)

    def open_output(self):
        if self.output_path and os.path.exists(self.output_path):
            os.startfile(os.path.dirname(self.output_path))
        else:
            messagebox.showinfo(APP_NAME, "No generated mesh yet.")

    def engine_status(self):
        _, message = self.generator.status()
        messagebox.showinfo("AI Engine Status", message)


if __name__ == "__main__":
    App().mainloop()
