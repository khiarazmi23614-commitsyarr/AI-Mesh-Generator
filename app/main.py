import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "AI Mesh Generator"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("900x600")
        self.minsize(760, 520)
        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=APP_NAME, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(root, text="Text-to-3D AI mesh generator").pack(anchor="w", pady=(2, 14))

        ttk.Label(root, text="Prompt").pack(anchor="w")
        self.prompt = tk.Text(root, height=4, font=("Segoe UI", 11))
        self.prompt.pack(fill="x", pady=(5, 10))
        self.prompt.insert("1.0", "a low-poly medieval sword")

        controls = ttk.Frame(root)
        controls.pack(fill="x")
        ttk.Label(controls, text="Output:").pack(side="left")
        self.format = ttk.Combobox(controls, values=["GLB", "OBJ"], state="readonly", width=8)
        self.format.set("GLB")
        self.format.pack(side="left", padx=6)
        ttk.Button(controls, text="Generate Mesh", command=self.generate).pack(side="left", padx=8)

        self.status = ttk.Label(root, text="Ready")
        self.status.pack(anchor="w", pady=10)

        preview = ttk.LabelFrame(root, text="3D Preview")
        preview.pack(fill="both", expand=True)
        ttk.Label(preview, text="3D viewer will be connected to the generated GLB/OBJ output.", anchor="center").pack(expand=True)

    def generate(self):
        prompt = self.prompt.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning(APP_NAME, "Enter a prompt first.")
            return
        self.status.config(text="Generation backend is not configured yet. Connect a compatible text-to-3D model in backend/generator.py.")

if __name__ == "__main__":
    App().mainloop()
