import fitz  # PyMuPDF
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from pdfminer.high_level import extract_text
from PIL import Image
import io
import os
import easyocr

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF by converting to an image and using OCR."""
    text = []
    doc = fitz.open(pdf_path)

    for page in doc:
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            base_image = doc.extract_image(img[0])
            image_data = base_image["image"]
            image = Image.open(io.BytesIO(image_data))

            # Debugging: Print Image Mode and Size
            print(f"Processing Image {img_index + 1}: Mode={image.mode}, Size={image.size}")

            # Ensure image is in RGB mode before OCR
            if image.mode != "RGB":
                image = image.convert("RGB")

            custom_config = r'--oem 1 --psm 11'
            ocr_text = pytesseract.image_to_string(image, config=custom_config)
            print(f"OCR Text Extracted from Image {img_index + 1}: {ocr_text[:200]}")
            text.append(ocr_text)


    return "\n".join(text)


# Example usage
pdf_path = "Raw Material.pdf"
extracted_text = extract_text_from_pdf(pdf_path)



print("Extracted Text:\n", extracted_text)
# Save extracted text to a text file
output_path = "Raw Material test.txt"
with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write(extracted_text)

