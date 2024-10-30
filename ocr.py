import cv2
import numpy as np

# Load the image
image = cv2.imread('new_ocr.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to the image
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Thresholding the image to binary
_, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

# Save the thresholded image for review
cv2.imwrite('thresholded_image.jpg', thresh)

# Detect circles using HoughCircles
circles = cv2.HoughCircles(
    thresh,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=10,
    param1=50,
    param2=13,
    minRadius=12,
    maxRadius=15
)

# Print detected circles
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    print("Detected circles:", circles)
else:
    print("No circles detected.")
    circles = []

# Draw detected circles
for (x, y, r) in circles:
    cv2.circle(image, (x, y), r, (0, 255, 0), 2)  # Draw circle in green
    cv2.rectangle(image, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)  # Draw center in orange

# Function to check if a circle is filled
def is_filled_circle(circle_center):
    x, y, r = circle_center
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)  # Create a filled circle mask
    filled_area = cv2.countNonZero(cv2.bitwise_and(mask, thresh))  # Count non-zero pixels in the masked area
    return filled_area > (np.pi * r * r) / 2  # Check if more than half of the circle is filled

# Identify filled circles
filled_circles = [circle for circle in circles if is_filled_circle(circle)]

# Split the image into left and right halves
height, width = image.shape[:2]
left_circles = []
right_circles = []

# Divide circles into left and right based on their x-coordinates
for circle in circles:
    x, y, r = circle
    if x < width // 2:
        left_circles.append(circle)  # Circles in the left half
    else:
        right_circles.append(circle)  # Circles in the right half

# Function to label circles with a specified number of labels
def label_circles(circles):
    # Sort circles first by their y coordinate, then by x coordinate
    circles.sort(key=lambda c: (c[1], c[0]))

    # Draw bounding boxes around rows of circles
    if circles:
        # Group circles by their y-coordinates to find rows
        rows = []
        current_row = []
        last_y = circles[0][1]

        for circle in circles:
            # Group circles into rows based on their vertical position
            if abs(circle[1] - last_y) < 20:  # Threshold for y-coordinate grouping
                current_row.append(circle)
            else:
                if current_row:  # Only append if there's something in current_row
                    rows.append(current_row)
                current_row = [circle]  # Start a new row
            last_y = circle[1]

        # Add the last row
        if current_row:
            rows.append(current_row)

        # Label each row of circles
        for row_index, row in enumerate(rows, start=1):  # Start numbering from 1
            # Sort the circles in the row from left to right
            row.sort(key=lambda c: c[0])  # Sort by x coordinate

            # Draw row number
            y_position = row[0][1] - 10  # Position the row number above the row
            cv2.putText(image, str(row_index), (row[0][0] - 10, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            for idx, circle in enumerate(row):
                x, y, r = circle

                # Check if the current circle is filled
                if tuple(circle) in [tuple(filled_circle) for filled_circle in filled_circles]:
                    cv2.circle(image, (x, y), r, (255, 0, 0), 2)  # Blue for filled circles
                else:
                    cv2.circle(image, (x, y), r, (0, 255, 0), 2)  # Green for non-filled circles

                # Label the circles with letters A-E
                if idx < 5:  # Ensure we only label the first five circles
                    label = chr(65 + idx)  # 65 is the ASCII code for 'A'
                    cv2.putText(image, label, (x - 10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Draw bounding boxes for each row of circles
            min_x = min(circle[0] - circle[2] for circle in row)  # Minimum x-coordinate - radius
            max_x = max(circle[0] + circle[2] for circle in row)  # Maximum x-coordinate + radius
            min_y = min(circle[1] - circle[2] for circle in row)  # Minimum y-coordinate - radius
            max_y = max(circle[1] + circle[2] for circle in row)  # Maximum y-coordinate + radius
            cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (255, 0, 255), 2)  # Draw rectangle in purple

# Process left and right circles separately
label_circles(left_circles)
label_circles(right_circles)

# Save the final image with filled circles labeled
cv2.imwrite("labeled_filled_circles.jpg", image)

print("Filled circles identified and labeled successfully.")
