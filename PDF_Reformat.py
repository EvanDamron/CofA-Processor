from wand.image import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as PILImage, ImageDraw, ImageFont

# Step 1: Convert PDF to Image using Wand
pdf_file = "Raw Material (1).pdf"  # Change this to your file
with Image(filename=pdf_file, resolution=300) as img:
    img.format = "png"
    img.save(filename="converted.png")

# Step 2: Load Image into OpenCV
image = cv2.imread("converted.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Step 3: Apply Thresholding (Convert text to white, background to black)
_, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

# Step 4: Compute Vertical Projection Histogram to Detect Columns
vertical_histogram = np.sum(binary, axis=0)  # Sum pixel values along vertical axis
column_threshold = np.max(vertical_histogram) * 0.2  # Define a cutoff for gaps
column_boundaries = np.where(vertical_histogram < column_threshold)[0]

# Step 5: Identify Column Start/End Positions
column_indices = []
prev = 0
for i in range(1, len(column_boundaries)):
    if column_boundaries[i] - column_boundaries[i - 1] > 50:  # Minimum gap size
        column_indices.append((prev, column_boundaries[i - 1]))
        prev = column_boundaries[i]
column_indices.append((prev, column_boundaries[-1]))  # Last column

# Step 6: Detect Rows Using Horizontal Projection
horizontal_histogram = np.sum(binary, axis=1)  # Sum pixel values along horizontal axis
row_threshold = np.max(horizontal_histogram) * 0.2  # Define cutoff for gaps
row_boundaries = np.where(horizontal_histogram < row_threshold)[0]

# Step 7: Identify Row Start/End Positions
row_indices = []
prev = 0
for i in range(1, len(row_boundaries)):
    if row_boundaries[i] - row_boundaries[i - 1] > 20:  # Minimum gap size
        row_indices.append((prev, row_boundaries[i - 1]))
        prev = row_boundaries[i]
row_indices.append((prev, row_boundaries[-1]))  # Last row

# Step 8: Draw Bounding Boxes and Detect Empty Rows
output_image = PILImage.open("converted.png")
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

        # If row has too much whitespace, add "N/A" text
        if cell_text_density < (x2 - x1) * (y2 - y1) * 0.1:  # 10% text density threshold
            text_x, text_y = (x1 + x2) // 2, (y1 + y2) // 2
            draw.text((text_x, text_y), "N/A", fill="red", font=font, anchor="mm")

# Step 9: Save and Display Result
output_image.save("output_with_boxes.png")

plt.figure(figsize=(10, 8))
plt.imshow(output_image)
plt.title("Detected Columns and Rows with N/A")
plt.axis("off")
plt.show()

