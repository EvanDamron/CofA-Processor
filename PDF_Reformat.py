import fitz  # PyMuPDF
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as PILImage, ImageDraw, ImageFont
import io

# Step 1: Extract Images from PDF using PyMuPDF (fitz)
pdf_path = "viscoplex_cofa.pdf"  # Update with your PDF file path

doc = fitz.open(pdf_path)
image_list = []

for page_index, page in enumerate(doc):
    images = page.get_images(full=True)
    for img_index, img in enumerate(images):
        base_image = doc.extract_image(img[0])
        image_data = base_image["image"]
        image = PILImage.open(io.BytesIO(image_data))
        image_filename = f"converted_page{page_index + 1}_image{img_index + 1}.png"
        image.save(image_filename)
        image_list.append(image_filename)
        print(f"Saved image: {image_filename}")

# Process each extracted image
for image_path in image_list:
    print(f"\nProcessing {image_path}...")

    # Step 2: Load Image into OpenCV
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply Thresholding (Convert text to white, background to black)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Step 4: Compute Vertical Projection Histogram to Detect Columns
    vertical_histogram = np.sum(binary, axis=0)  # Sum pixel values vertically
    column_threshold = np.max(vertical_histogram) * 0.2  # Threshold to detect column gaps
    column_boundaries = np.where(vertical_histogram < column_threshold)[0]

    # Step 5: Identify Column Start/End Positions
    column_indices = []
    prev = column_boundaries[0] if len(column_boundaries) > 0 else 0

    for i in range(1, len(column_boundaries)):
        if column_boundaries[i] - column_boundaries[i - 1] > 50:  # Adjust gap size as needed
            column_indices.append((prev, column_boundaries[i - 1]))
            prev = column_boundaries[i]
    if len(column_boundaries) > 0:
        column_indices.append((prev, column_boundaries[-1]))  # Last column

    # Step 6: Detect Rows Using Horizontal Projection
    horizontal_histogram = np.sum(binary, axis=1)  # Sum pixel values horizontally
    row_threshold = np.max(horizontal_histogram) * 0.2  # Threshold to detect row gaps
    row_boundaries = np.where(horizontal_histogram < row_threshold)[0]

    # Step 7: Identify Row Start/End Positions
    row_indices = []
    prev = row_boundaries[0] if len(row_boundaries) > 0 else 0

    for i in range(1, len(row_boundaries)):
        if row_boundaries[i] - row_boundaries[i - 1] > 30:  # Adjust gap size for row detection
            row_indices.append((prev, row_boundaries[i - 1]))
            prev = row_boundaries[i]
    if len(row_boundaries) > 0:
        row_indices.append((prev, row_boundaries[-1]))  # Last row

    # Step 8: Draw Bounding Boxes and Detect Empty Cells
    output_image = PILImage.open(image_path)
    draw = ImageDraw.Draw(output_image)

    # Load font for "N/A" text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    for x1, x2 in column_indices:
        for y1, y2 in row_indices:
            # Extract cell content
            cell = binary[y1:y2, x1:x2]
            cell_text_density = np.sum(cell)

            # Draw column & row bounding boxes
            draw.rectangle([x1, y1, x2, y2], outline="green", width=2)

            # Insert "N/A" if text density is below threshold (blank cell detection)
            if cell_text_density < (x2 - x1) * (y2 - y1) * 0.1:  # Adjust threshold if needed
                text_x, text_y = (x1 + x2) // 2, (y1 + y2) // 2
                draw.text((text_x, text_y), "N/A", fill="red", font=font, anchor="mm")

    # Step 9: Save and Display Result
    output_filename = f"output_with_boxes_{image_path}"
    output_image.save(output_filename)

    plt.figure(figsize=(12, 10))
    plt.imshow(output_image)
    plt.title(f"Detected Columns and Rows with N/A - {image_path}")
    plt.axis("off")
    plt.show()

    print(f"Saved output image with boxes: {output_filename}")
