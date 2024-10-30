import cv2

def get_question_area(section, question_index, original_image, output_filename):
    # Define regions for each section (adjust coordinates based on actual layout)
    section_coords = {
        'Section-I': (10, 10, 200, 400),  # (x, y, width, height)
        'Section-II': (220, 10, 400, 400),
        'Section-III': (10, 420, 200, 800)
    }

    # Get the coordinates for the section
    x, y, w, h = section_coords[section]

    # Define spacing for each question (adjust based on layout)
    question_height = 25  # Height of each question area in pixels

    # Calculate the y-coordinate for the question within the section
    question_y = y + (question_index * question_height)

    # Ensure we don't exceed image boundaries
    if question_y + question_height > original_image.shape[0]:
        return None

    # Define the bounding box for the question area
    question_area = original_image[question_y:question_y + question_height, x:x + w]

    # Draw a bounding box around the question area on the original image
    cv2.rectangle(original_image, (x, question_y), (x + w, question_y + question_height), (0, 255, 0), 2)

    # Save the modified image with the bounding box
    cv2.imwrite(output_filename, original_image)

    return question_area

# Example usage
section = 'Section-I'
question_index = 0
original_image = cv2.imread('detected_circles.jpg')  # Load your original image
output_filename = 'question_area_with_bounding_box.jpg'

question_area = get_question_area(section, question_index, original_image, output_filename)