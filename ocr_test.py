import fitz  # PyMuPDF
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from pdfminer.high_level import extract_text
from PIL import Image
import io
import easyocr

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF. Uses OCR only if necessary."""
    # Try to extract text using pdfminer (for non-scanned PDFs)
    text = extract_text(pdf_path).strip()

    if text:
        return text  # If text is found, return it (no OCR needed)

    # If text is empty, assume it's a scanned PDF and use OCR
    print("No text found. Using OCR...")
    text = []
    doc = fitz.open(pdf_path)

    for page in doc:
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            base_image = doc.extract_image(img[0])
            image_data = base_image["image"]
            image = Image.open(io.BytesIO(image_data))

            text.append(pytesseract.image_to_string(image))

    return "\n".join(text)


# Example usage
pdf_path = "Raw Material.pdf"
extracted_text = extract_text_from_pdf(pdf_path)

print("Extracted Text:\n", extracted_text)
# Save extracted text to a text file
output_path = "Raw Material Test.txt"
with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write(extracted_text)

