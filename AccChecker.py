import tkinter as tk
from tkinter import ttk, messagebox
import json
import fitz  # PyMuPDF for handling PDFs
from PIL import Image, ImageTk


# Load JSON data
def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


# Save JSON data
def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


# Convert PDF to a high-quality image
def pdf_to_image(pdf_path, output_path="output.png", zoom=3):
    doc = fitz.open(pdf_path)
    page = doc[0]  # Get first page
    mat = fitz.Matrix(zoom, zoom)  # Higher zoom for better quality
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(output_path)
    return output_path


class JsonEditorApp:
    def __init__(self, root, json_data, pdf_image):
        self.root = root
        self.root.title("PDF & JSON Editor")
        self.root.state('zoomed')  # Open in full-screen mode
        self.json_data = json_data

        # Main Layout
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Frame for PDF display
        pdf_frame = ttk.Frame(main_frame, padding=10)
        pdf_frame.pack(side="left", fill="both", expand=True)
        ttk.Label(pdf_frame, text="PDF Preview", font=("Arial", 14, "bold")).pack()

        img = Image.open(pdf_image)
        img = img.resize((600, 800), Image.Resampling.LANCZOS)  # Increase display size
        self.tk_img = ImageTk.PhotoImage(img)
        ttk.Label(pdf_frame, image=self.tk_img).pack()

        # Frame for JSON data
        json_frame = ttk.Frame(main_frame, padding=10)
        json_frame.pack(side="right", fill="both", expand=True)
        ttk.Label(json_frame, text="Edit JSON Data", font=("Arial", 14, "bold")).pack()

        self.entries = {}
        canvas = tk.Canvas(json_frame)
        scrollbar = ttk.Scrollbar(json_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for key, value in json_data.items():
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=5, pady=2)
            ttk.Label(frame, text=key.replace("_", " ").capitalize(), width=25, anchor="w").pack(side="left")
            if isinstance(value, list):
                sub_frame = ttk.Frame(scrollable_frame)
                sub_frame.pack(fill="x", padx=20, pady=2)
                self.entries[key] = []
                for item in value:
                    sub_entry = ttk.Entry(sub_frame, width=40)
                    sub_entry.insert(0, str(item))
                    sub_entry.pack(anchor="w")
                    self.entries[key].append(sub_entry)
            else:
                entry = ttk.Entry(frame, width=40)
                entry.insert(0, str(value))
                entry.pack(side="right")
                self.entries[key] = entry

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Submit button
        ttk.Button(json_frame, text="Approve & Submit", command=self.save_json_data).pack(pady=10)

    def save_json_data(self):
        updated_data = {}
        for key, value in self.json_data.items():
            if isinstance(value, list):
                updated_data[key] = [entry.get() for entry in self.entries[key]]
            else:
                updated_data[key] = self.entries[key].get()
        save_json(updated_data, "updated_data.json")
        messagebox.showinfo("Success", "Data has been saved successfully!")
        self.root.quit()  # Close the GUI automatically


if __name__ == "__main__":
    json_path = "raw material.json"
    pdf_path = "Raw Material (1).pdf"
    img_path = pdf_to_image(pdf_path, zoom=3)  # Higher zoom for better quality
    json_data = load_json(json_path)

    root = tk.Tk()
    app = JsonEditorApp(root, json_data, img_path)
    root.mainloop()
