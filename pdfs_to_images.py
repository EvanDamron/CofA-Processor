import fitz  # PyMuPDF
import os
import io
from PIL import Image as PILImage

# Paths
pdf_folder_path = "cofa pdfs"
png_folder_path = "cofa pngs"

# Ensure output folder exists
os.makedirs(png_folder_path, exist_ok=True)

# Loop through all PDFs in the folder
for pdf in os.listdir(pdf_folder_path):
    if not pdf.endswith(".pdf"):
        continue  # Skip non-PDF files

    pdf_path = os.path.join(pdf_folder_path, pdf)
    doc = fitz.open(pdf_path)

    # Loop through all pages in the PDF
    for page_num in range(len(doc)):
        page = doc[page_num]  # Get the page
        images = page.get_images(full=True)  # Extract images from the page

        # Loop through all images on the page
        for img_index, img in enumerate(images):
            xref = img[0]  # Image reference number
            base_image = doc.extract_image(xref)  # Extract image data
            image_data = base_image["image"]

            # Convert image data to PIL Image
            image = PILImage.open(io.BytesIO(image_data))

            # Save image
            image_filename = f"{pdf.replace('.pdf', '.png')}"
            image_path = os.path.join(png_folder_path, image_filename)
            image.save(image_path)

            print(f"Saved image: {image_filename}")

print("Extraction complete.")
