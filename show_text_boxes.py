# import cv2
# import pytesseract
# from PIL import Image, ImageDraw, ImageFont
# import matplotlib.pyplot as plt
# import numpy as np
#
# # Configure pytesseract to use the installed Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#
#
# def rotate_image(image, angle):
#     """Rotate the image around its center by the given angle."""
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#     return rotated
#
#
# def deskew_image(image_path):
#     """Deskew the image by detecting horizontal lines and rotating it accordingly."""
#
#     # Load the image in grayscale (for line detection) and color (for output)
#     gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     original = cv2.imread(image_path)
#
#     # Detect edges using Canny to find lines
#     edges = cv2.Canny(gray, 50, 150, apertureSize=3)
#
#     # Detect lines using Hough Line Transform
#     lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)  # Adjust threshold if needed
#
#     if lines is not None:
#         angles = []
#         for rho, theta in lines[:, 0]:
#             angle = (theta * 180) / np.pi  # Convert radians to degrees
#
#             # Focus on near-horizontal lines (angles close to 0 or 180 degrees)
#             if angle < 10 or angle > 170:
#                 skew_angle = angle if angle < 90 else angle - 180
#                 angles.append(skew_angle)
#
#         if angles:
#             avg_angle = np.mean(angles)
#             print(f"Detected skew angle: {avg_angle:.2f}°")
#
#             # Rotate the original image to correct skew
#             deskewed = rotate_image(original, avg_angle)
#         else:
#             print("No significant horizontal lines detected. Skipping rotation.")
#             deskewed = original
#     else:
#         print("No lines detected. Skipping rotation.")
#         deskewed = original
#
#     # Convert to PIL image for compatibility with other libraries
#     pil_image = Image.fromarray(cv2.cvtColor(deskewed, cv2.COLOR_BGR2RGB))
#     return pil_image
#
#
# def draw_text_boxes(image):
#     """Detect text using pytesseract, draw bounding boxes, and print word count."""
#
#     draw = ImageDraw.Draw(image)
#
#     custom_config = r'--oem 1 --psm 11'
#     data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
#
#     # Optional: Load font for labels
#     try:
#         font = ImageFont.truetype("arial.ttf", 15)
#     except:
#         font = ImageFont.load_default()
#
#     word_count = 0  # Initialize word count
#
#     # Draw bounding boxes and count detected words
#     for i in range(len(data['text'])):
#         if data['text'][i].strip():  # Skip empty detections
#             word_count += 1  # Increment word count
#             x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
#             draw.rectangle([(x, y), (x + w, y + h)], outline="red", width=2)
#             draw.text((x, y - 15), data['text'][i], fill="blue", font=font)  # Label with text
#
#     # Print the total number of detected words
#     print(f"Total words/boxes detected: {word_count}")
#
#     # Display the image with bounding boxes
#     plt.figure(figsize=(12, 10))
#     plt.imshow(image)
#     plt.title("Detected Text with Bounding Boxes")
#     plt.axis("off")
#     plt.show()
#
#     return image
#
# # ---- Run the function ---- #
# image_path = "Raw Material.png"  # Replace with your image path
# # deskewed_image = deskew_image(image_path)
# # output_image = draw_text_boxes(deskewed_image)
#
# unprocessed_image = Image.open(image_path)
# output_image = draw_text_boxes(unprocessed_image)
import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import random
import numpy as np


# Configure pytesseract to use the installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def boxes_within_threshold(box1, box2, horizontal_threshold, vertical_threshold):
    """Check if two boxes are within horizontal and vertical thresholds."""
    horizontal_distance = min(abs(box2['left'] - box1['right']), abs(box1['left'] - box2['right']))
    vertical_distance = min(abs(box2['top'] - box1['top']), abs(box1['bottom'] - box2['bottom']))
    return horizontal_distance <= horizontal_threshold and vertical_distance <= vertical_threshold


def merge_two_boxes(box1, box2):
    """Merge two boxes into one encompassing box with concatenated text."""
    return {
        "text": f"{box1['text']} {box2['text']}",
        "left": min(box1['left'], box2['left']),
        "top": min(box1['top'], box2['top']),
        "right": max(box1['right'], box2['right']),
        "bottom": max(box1['bottom'], box2['bottom'])
    }


import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import random


def random_color():
    """Generate a random RGB color."""
    return tuple(random.randint(50, 200) for _ in range(3))


def draw_text_boxes(image, data, clusters):
    """
    Draw original OCR text boxes and clustered merged boxes with different colors.

    Parameters:
    - image: PIL.Image object.
    - data: Original Tesseract output data dictionary (with 'text', 'left', 'top', 'width', 'height').
    - clusters: List of clusters, where each cluster is a list of merged box dictionaries.
    """
    before_image = image.copy()
    after_image = image.copy()

    before_draw = ImageDraw.Draw(before_image)
    after_draw = ImageDraw.Draw(after_image)

    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()

    # Draw original boxes (red)
    for i in range(len(data['text'])):
        if data['text'][i].strip():
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            before_draw.rectangle([(x, y), (x + w, y + h)], outline="red", width=2)
            before_draw.text((x, y - 10), data['text'][i], fill="red", font=font)

    # Draw merged clusters with different colors
    for cluster in clusters:
        cluster_color = random_color()  # Different color for each cluster
        for box in cluster:
            after_draw.rectangle(
                [(box['left'], box['top']), (box['right'], box['bottom'])],
                outline=cluster_color,
                width=3
            )
            after_draw.text(
                (box['left'], box['top'] - 10),
                box['text'],
                fill=cluster_color,
                font=font
            )

    # Display side-by-side comparison
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))

    axes[0].imshow(before_image)
    axes[0].set_title("Before Merging (Original Text Boxes)")
    axes[0].axis("off")

    axes[1].imshow(after_image)
    axes[1].set_title("After Merging (Clustered Merged Text Boxes)")
    axes[1].axis("off")

    plt.show()


def iterative_merge_text_boxes(data, horizontal_threshold=30, vertical_threshold=10):
    """Iteratively merge text boxes until no new merges occur."""
    boxes = []
    for i in range(len(data['text'])):
        if data['text'][i].strip():
            boxes.append({
                "text": data['text'][i].strip(),
                "left": data['left'][i],
                "top": data['top'][i],
                "right": data['left'][i] + data['width'][i],
                "bottom": data['top'][i] + data['height'][i]
            })

    merged = True
    iteration = 0

    while merged:
        iteration += 1
        merged = False
        new_boxes = []
        used_indices = set()

        for i, box1 in enumerate(boxes):
            if i in used_indices:
                continue

            merged_box = box1
            for j, box2 in enumerate(boxes):
                if i != j and j not in used_indices and boxes_within_threshold(merged_box, box2, horizontal_threshold, vertical_threshold):
                    merged_box = merge_two_boxes(merged_box, box2)
                    used_indices.add(j)
                    merged = True

            new_boxes.append(merged_box)
            used_indices.add(i)

        boxes = new_boxes

    print(f"Merging completed in {iteration} iteration(s).")
    return boxes


# def draw_text_boxes(image, data, merged_boxes):
#     """Draw original and merged text boxes for comparison."""
#
#     before_image = image.copy()
#     after_image = image.copy()
#
#     before_draw = ImageDraw.Draw(before_image)
#     after_draw = ImageDraw.Draw(after_image)
#
#     try:
#         font = ImageFont.truetype("arial.ttf", 12)
#     except:
#         font = ImageFont.load_default()
#
#     # Draw original boxes (red)
#     for i in range(len(data['text'])):
#         if data['text'][i].strip():
#             x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
#             before_draw.rectangle([(x, y), (x + w, y + h)], outline="red", width=2)
#             before_draw.text((x, y - 10), data['text'][i], fill="red", font=font)
#
#     # Draw merged boxes (green)
#     for box in merged_boxes:
#         after_draw.rectangle([(box['left'], box['top']), (box['right'], box['bottom'])], outline="green", width=3)
#         after_draw.text((box['left'], box['top'] - 10), box['text'], fill="green", font=font)
#
#     # Display side-by-side comparison
#     fig, axes = plt.subplots(1, 2, figsize=(20, 12))
#
#     axes[0].imshow(before_image)
#     axes[0].set_title("Before Merging (Original Text Boxes)")
#     axes[0].axis("off")
#
#     axes[1].imshow(after_image)
#     axes[1].set_title("After Merging (Merged Text Boxes)")
#     axes[1].axis("off")
#
#     plt.show()


def process_image(image_path, horizontal_threshold=30, vertical_threshold=10):
    """Run OCR, iteratively merge text boxes, and display results."""
    image = Image.open(image_path)

    # Run OCR
    custom_config = r'--oem 1 --psm 11'
    # custom_config = r'--oem 1 --psm 3'
    data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)

    # Iteratively merge text boxes
    merged_boxes = iterative_merge_text_boxes(data, horizontal_threshold, vertical_threshold)

    # Print counts
    original_count = len([t for t in data['text'] if t.strip()])
    merged_count = len(merged_boxes)
    print(f"\nOriginal word boxes: {original_count}")
    print(f"Merged text boxes: {merged_count}")

    for box in merged_boxes:
        print(
            f"Text: '{box['text']}', Left: {box['left']}, Top: {box['top']}, Right: {box['right']}, Bottom: {box['bottom']}")

    clusters = cluster_boxes_by_bottom(merged_boxes)
    # display_clusters(clusters)
    # Draw before and after merging
    draw_text_boxes(image, data, clusters)


def cluster_boxes_by_bottom(merged_boxes, bottom_threshold=20):
    """
    Cluster merged OCR boxes based on their 'bottom' value.

    Parameters:
    - merged_boxes: List of dictionaries with 'text', 'left', 'top', 'right', 'bottom'.
    - bottom_threshold: Int, max difference in 'bottom' values to consider for the same cluster.

    Returns:
    - List of clusters (each cluster is a list of boxes).
    """
    # Sort boxes by 'bottom' value
    sorted_boxes = sorted(merged_boxes, key=lambda x: x['bottom'])

    clusters = []
    current_cluster = [sorted_boxes[0]]

    for box in sorted_boxes[1:]:
        # Check if box is close enough to the current cluster's 'bottom' reference
        if abs(box['bottom'] - current_cluster[-1]['bottom']) <= bottom_threshold:
            current_cluster.append(box)
        else:
            # Start a new cluster if the 'bottom' values differ beyond threshold
            clusters.append(current_cluster)
            current_cluster = [box]

    clusters.append(current_cluster)  # Add the last cluster
    return clusters


def display_clusters(clusters):
    """
    Display the clustered OCR boxes.

    Parameters:
    - clusters: List of clusters with text boxes.
    """
    for i, cluster in enumerate(clusters, 1):
        print(f"\n🔹 Cluster {i}:")
        # Sort by 'left' to maintain reading order within the line
        for box in sorted(cluster, key=lambda x: x['left']):
            print(f"  Text: {box['text'].strip()}  (bottom: {box['bottom']}, Left: {box['left']})")


     # ---- Run the function ---- #
# image_path = "viscoplex_cofa.png"  # Replace with your image path
image_path = "Raw Material.png"
# image_path = "pure_performance_cofa.png"
# image_path = "viscoplex_cofa.png"
process_image(image_path, horizontal_threshold=40, vertical_threshold=10)  # Adjust thresholds as needed

