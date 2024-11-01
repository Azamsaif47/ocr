from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import cv2
import numpy as np
import shutil
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Answer key image path
ANSWER_KEY_PATH = 'answer_key.jpg'  # Assume answer key is in this file

# Function to determine if a circle is filled
def is_filled_circle(circle_center, thresh_image):
    x, y, r = circle_center
    mask = np.zeros(thresh_image.shape, dtype=np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1)
    filled_area = cv2.countNonZero(cv2.bitwise_and(mask, thresh_image))
    return filled_area > (np.pi * r * r) / 2

# Function to extract answer key or responses from image
def extract_answer_key_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

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

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
    else:
        circles = []

    height, width = image.shape[:2]
    left_circles = [circle for circle in circles if circle[0] < width // 2]
    right_circles = [circle for circle in circles if circle[0] >= width // 2]

    def extract_answer_key(circles, thresh_image, row_offset=0):
        answer_key = {}
        circles.sort(key=lambda c: (c[1], c[0]))
        rows = []
        current_row = []
        last_y = circles[0][1] if circles else None

        for circle in circles:
            if last_y is not None and abs(circle[1] - last_y) < 20:
                current_row.append(circle)
            else:
                if current_row:
                    rows.append(current_row)
                current_row = [circle]
            last_y = circle[1]

        if current_row:
            rows.append(current_row)

        for row_index, row in enumerate(rows, start=1 + row_offset):
            row.sort(key=lambda c: c[0])
            filled_count = 0
            for idx, circle in enumerate(row[:5]):
                x, y, r = circle
                label = chr(65 + idx)

                if is_filled_circle(circle, thresh_image):
                    filled_count += 1
                    answer_key[row_index] = label
                else:
                    if row_index not in answer_key:
                        answer_key[row_index] = 'U'

            if filled_count > 1:
                answer_key[row_index] = 'I'

        return answer_key

    left_answer_key = extract_answer_key(left_circles, thresh)
    right_answer_key = extract_answer_key(right_circles, thresh, row_offset=len(left_answer_key))
    answer_key = {**left_answer_key, **right_answer_key}
    return answer_key

# Load the answer key
answer_key = extract_answer_key_from_image(ANSWER_KEY_PATH)

# Function to evaluate student responses
def evaluate_student_responses(answer_key, student_response):
    total_questions = len(answer_key)
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    double_answered_count = 0

    for question in range(1, total_questions + 1):
        answer = answer_key.get(question)
        student_answer = student_response.get(question)

        if student_answer == "U" or student_answer is None or student_answer == "":
            unanswered_count += 1
        elif student_answer == "I":
            double_answered_count += 1
        elif student_answer == answer:
            correct_count += 1
        else:
            incorrect_count += 1

    answered_questions = total_questions - unanswered_count
    percentage = (correct_count / answered_questions * 100) if answered_questions > 0 else 0

    result_summary = {
        "Total Questions": total_questions,
        "Correct Answers": correct_count,
        "Incorrect Answers": incorrect_count + double_answered_count,
        "Unanswered Questions": unanswered_count,
        "Percentage": percentage
    }

    return result_summary

# API endpoint to process multiple answer sheets
@app.post("/process-answer-sheets/")
async def process_answer_sheets(files: List[UploadFile] = File(...)):
    results = []

    print(f"Received {len(files)} files")

    if not files:
        return JSONResponse(content={"error": "No files received"}, status_code=400)

    for file in files:
        print(f"Processing file: {file.filename}")  # Log the file name
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_file_path = tmp_file.name

            student_response = extract_answer_key_from_image(tmp_file_path)
            result = evaluate_student_responses(answer_key, student_response)
            result["filename"] = file.filename
            results.append(result)

            os.remove(tmp_file_path)
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
            return JSONResponse(content={"error": f"Error processing {file.filename}"}, status_code=400)

    return JSONResponse(content={"results": results})
