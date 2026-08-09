import math
import os
import shutil
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.generator import MeshGenerator

APP_NAME = "AI Mesh Generator"


class MeshViewer(tk.Canvas):
    """Built-in lightweight 3D viewer. Drag to orbit and use the wheel to zoom."""

    def __init__(self, master, **kwargs):
        super().__init__(master, background="#17191d", highlightthickness=0, **kwargs)
        self.vertices = []
        self.faces = []
        self.rot_x = -0.25
        self.rot_y = 0.65
        self.zoom = 1.0
        self.last_x = self.last_y = None
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-4>", lambda e: self._zoom(1.12))
        self.bind("<Button-5>", lambda e: self._zoom(0.89))
        self.bind("<Configure>", lambda e: self.draw())

    def clear(self):
        self.vertices, self.faces = [], []
        self.draw()

    def load(self, path):
        import trimesh
        loaded = trimesh.load(path, force="scene")
        if isinstance(loaded, trimesh.Scene):
            meshes = [g for g in loaded.geometry.values() if hasattr(g, "vertices") and len(g.vertices)]
            if not meshes:
                raise ValueError("The generated file contains no mesh geometry.")
            mesh = trimesh.util.concatenate(meshes)
        else:
            mesh = loaded
        if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
            raise ValueError("The generated file contains no renderable triangles.")

        self.vertices = mesh.vertices.astype(float).tolist()
        self.faces = mesh.faces.astype(int).tolist()
        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        cz = sum(v[2] for v in self.vertices) / len(self.vertices)
        self.vertices = [[v[0] - cx, v[1] - cy, v[2] - cz] for v in self.vertices]
        extent = max(max(abs(c) for c in v) for v in self.vertices) or 1.0
        self.vertices = [[c / extent for c in v] for v in self.vertices]
        self.zoom = 1.0
        self.draw()

    def _press(self, event):
        self.last_x, self.last_y = event.x, event.y

    def _drag(self, event):
        if self.last_x is None:
            return
        self.rot_y += (event.x - self.last_x) * 0.01
        self.rot_x += (event.y - self.last_y) * 0.01
        self.last_x, self.last_y = event.x, event.y
        self.draw()

    def _wheel(self, event):
        self._zoom(1.12 if event.delta > 0 else 0.89)

    def _zoom(self, amount):
        self.zoom = max(0.2, min(5.0, self.zoom * amount))
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = max(self.winfo_width(), 1), max(self.winfo_height(), 1)
        if not self.vertices:
            self.create_text(w // 2, h // 2, text="No mesh loaded", fill="#c7cad0", font=("Segoe UI", 12))
            return

        sx, cx = math.sin(self.rot_x), math.cos(self.rot_x)
        sy, cy = math.sin(self.rot_y), math.cos(self.rot_y)
        projected = []
        for x, y, z in self.vertices:
            x1 = x * cy + z * sy
            z1 = -x * sy + z * cy
            y1 = y * cx - z1 * sx
            z2 = y * sx + z1 * cx
            perspective = 1.0 / max(0.35, 2.8 - z2 * 0.45)
            scale = min(w, h) * 0.34 * self.zoom * perspective
            projected.append((w / 2 + x1 * scale, h / 2 - y1 * scale, z2))

        ordered = sorted(self.faces, key=lambda f: (projected[f[0]][2] + projected[f[1]][2] + projected[f[2]][2]) / 3)
        for f in ordered:
            p = [projected[i] for i in f]
            depth = sum(q[2] for q in p) / 3
            shade = int(max(75, min(220, 150 + depth * 45)))
            fill = f"#{shade:02x}{shade:02x}{min(255, shade + 20):02x}"
            self.create_polygon([(q[0], q[1]) for q in p], fill=fill, outline="#555b64")
        self.create_text(12, 12, anchor="nw", text="Drag = rotate   •   Wheel = zoom", fill="#d9dce1", font=("Segoe UI", 9))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x760")
        self.minsize(900, 650)
        self.generator = MeshGenerator()
        self.output_path = None
        self.reference_image = None
        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=APP_NAME, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(root, text="AI text/image → 3D mesh", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 12))

        prompt_box = ttk.LabelFrame(root, text="Prompt")
        prompt_box.pack(fill="x", pady=(0, 8))
        self.prompt = tk.Text(prompt_box, height=3, font=("Segoe UI", 11))
        self.prompt.pack(fill="x", padx=10, pady=8)
        self.prompt.insert("1.0", "a cute low-poly robot toy, clean shape, studio lighting")

        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(0, 7))
        ttk.Label(controls, text="Reference:").pack(side="left")
        self.image_var = tk.StringVar(value="None")
        ttk.Label(controls, textvariable=self.image_var, width=24).pack(side="left", padx=5)
        ttk.Button(controls, text="Choose", command=self.choose_image).pack(side="left")
        ttk.Label(controls, text="Format:").pack(side="left", padx=(15, 4))
        self.format = ttk.Combobox(controls, values=["GLB", "OBJ"], state="readonly", width=7)
        self.format.set("GLB")
        self.format.pack(side="left")
        self.generate_button = ttk.Button(controls, text="Generate Mesh", command=self.generate)
        self.generate_button.pack(side="left", padx=10)
        self.download_button = ttk.Button(controls, text="Download Mesh", command=self.download_mesh, state="disabled")
        self.download_button.pack(side="left")

        progress_row = ttk.Frame(root)
        progress_row.pack(fill="x", pady=(0, 8))
        self.progress = ttk.Progressbar(progress_row, mode="determinate", maximum=100)
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress_label = ttk.Label(progress_row, text="  0%")
        self.progress_label.pack(side="left")
        self.status = ttk.Label(root, text="Ready")
        self.status.pack(anchor="w", pady=(0, 8))

        preview = ttk.LabelFrame(root, text="3D Preview — drag to rotate, wheel to zoom")
        preview.pack(fill="both", expand=True)
        self.viewer = MeshViewer(preview)
        self.viewer.pack(fill="both", expand=True, padx=3, pady=3)
        self.viewer.clear()

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Open Output Folder", command=self.open_output).pack(side="left")
        ttk.Button(bottom, text="Engine Status", command=self.engine_status).pack(side="right")

    def choose_image(self):
        path = filedialog.askopenfilename(title="Choose reference image", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")])
        if path:
            self.image_var.set(os.path.basename(path))
            self.reference_image = path

    def _set_progress(self, value, text):
        self.progress["value"] = value
        self.progress_label.config(text=f"  {int(value)}%")
        self.status.config(text=text)

    def generate(self):
        prompt = self.prompt.get("1.0", "end").strip()
        image = self.reference_image
        if not prompt and not image:
            messagebox.showwarning(APP_NAME, "Enter a prompt or choose a reference image.")
            return
        self.generate_button.config(state="disabled")
        self.download_button.config(state="disabled")
        self._set_progress(2, "Preparing AI generation...")
        threading.Thread(target=self._generate_worker, args=(prompt, image), daemon=True).start()

    def _generate_worker(self, prompt, image):
        try:
            ext = self.format.get().lower()
            def progress(value, text):
                self.after(0, lambda v=value, t=text: self._set_progress(v, t))
            path = self.generator.generate(prompt=prompt, image_path=image, output_format=ext, progress_callback=progress)
            self.output_path = path
            self.after(0, lambda: self._generation_done(path))
        except Exception as exc:
            self.after(0, lambda: self._generation_error(str(exc)))

    def _generation_done(self, path):
        self.generate_button.config(state="normal")
        self._set_progress(100, "Generation complete — loading mesh...")
        try:
            self.viewer.load(path)
            self.download_button.config(state="normal")
            self.status.config(text="Mesh ready — drag the preview to rotate it.")
        except Exception as exc:
            self.status.config(text=f"Mesh generated, but viewer could not load it: {exc}")
            messagebox.showwarning(APP_NAME, f"Mesh was generated, but the 3D viewer could not load it.\n\n{exc}")

    def _generation_error(self, error):
        self.generate_button.config(state="normal")
        self.download_button.config(state="disabled")
        self.progress["value"] = 0
        self.progress_label.config(text="  0%")
        self.status.config(text="Generation failed")
        messagebox.showerror(APP_NAME, error)

    def download_mesh(self):
        if not self.output_path or not os.path.exists(self.output_path):
            messagebox.showinfo(APP_NAME, "No generated mesh yet.")
            return
        source = Path(self.output_path)
        destination = filedialog.asksaveasfilename(
            title="Save generated mesh",
            initialfile=source.name,
            defaultextension=source.suffix,
            filetypes=[(source.suffix.upper().replace(".", "") + " file", "*" + source.suffix), ("All files", "*.*")],
        )
        if destination:
            shutil.copy2(source, destination)
            self.status.config(text=f"Saved: {destination}")

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
