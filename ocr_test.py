import pytesseract
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
import difflib

# Path to the PDF file
pdf_path = "./Raw Material.pdf"


# Function to extract text using pdfminer (without OCR)
def extract_text_pdfminer(pdf_path):
    try:
        text = extract_text(pdf_path)
        if text.strip():
            return text
    except Exception as e:
        print(f"PDFMiner failed: {e}")
    return ""


# Function to extract text using OCR (Tesseract) from images
def extract_text_ocr(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)  # Convert PDF to images
    extracted_text = []

    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)  # Apply OCR
        extracted_text.append(text)
        print(f"Extracted text from page {i + 1}...")

    return "\n".join(extracted_text)


# Extract text using both methods
pdfminer_text = extract_text_pdfminer(pdf_path)
ocr_text = extract_text_ocr(pdf_path)

# Save extracted text to files
pdfminer_text_path = "/mnt/data/pdfminer_text.txt"
ocr_text_path = "/mnt/data/ocr_text.txt"

with open(pdfminer_text_path, "w", encoding="utf-8") as f:
    f.write(pdfminer_text)

with open(ocr_text_path, "w", encoding="utf-8") as f:
    f.write(ocr_text)

# Compare both texts using difflib
diff = difflib.unified_diff(pdfminer_text.splitlines(), ocr_text.splitlines(),
                            fromfile="PDFMiner", tofile="OCR", lineterm="")

# Save comparison results
diff_path = "/mnt/data/text_comparison.txt"
with open(diff_path, "w", encoding="utf-8") as f:
    f.write("\n".join(diff))

print(f"Extracted text saved to:\n- PDFMiner: {pdfminer_text_path}\n- OCR: {ocr_text_path}")
print(f"Comparison saved to: {diff_path}")
