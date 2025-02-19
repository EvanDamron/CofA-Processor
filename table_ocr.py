import pytesseract
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_table(image_path):
    """Detect and draw a bounding box around the table based on text box positions."""
    # Load image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Run pytesseract to get text box data
    data = pytesseract.image_to_data(image, config='--oem 1 --psm 3', output_type=pytesseract.Output.DICT)
    width, height = image.size

    # Step 1: Find the upper boundary based on "Test Method"
    upper_bound = None
    boxes = []

    for i, text in enumerate(data['text']):
        if text.strip():
            boxes.append({
                "text": text.strip(),
                "top": data['top'][i],
                "bottom": data['top'][i] + data['height'][i]
            })

            if "test method" in text.strip().lower():  # Case-insensitive match
                upper_bound = data['top'][i]
                print(f"Found 'Test Method' at y = {upper_bound}")

    if upper_bound is None:
        print("Error: 'Test Method' not found.")
        return image

    # Step 2: Sort boxes by their top Y-coordinate
    boxes_sorted = sorted(boxes, key=lambda x: x['top'])

    # Step 3: Find the lower boundary (first gap ≥ 100 pixels below "Test Method")
    lower_bound = None
    for i in range(len(boxes_sorted) - 1):
        current_bottom = boxes_sorted[i]['bottom']
        next_top = boxes_sorted[i + 1]['top']

        # Only check gaps below "Test Method"
        if current_bottom > upper_bound and next_top - current_bottom >= 100:
            lower_bound = current_bottom
            print(f"Found lower boundary at y = {lower_bound} (gap ≥ 100 pixels)")
            break

    if lower_bound is None:
        # Default to bottom of the image if no suitable gap is found
        lower_bound = height
        print("No large gap found. Using bottom of the image as lower boundary.")

    # Step 4: Draw the table bounding box (full width)
    draw.rectangle([(0, upper_bound), (width, lower_bound)], outline="green", width=3)
    print(f"Drew bounding box from y = {upper_bound} to y = {lower_bound}")

    # Display the result
    plt.figure(figsize=(12, 10))
    plt.imshow(image)
    plt.title("Detected Table Bounding Box")
    plt.axis("off")
    plt.show()

    return image

# ---- Run the function ---- #
image_path = "Raw Material.png"  # Replace with your image path
detected_image = detect_table(image_path)
# detected_image.save("output_with_table_box.png")  # Uncomment to save the result
