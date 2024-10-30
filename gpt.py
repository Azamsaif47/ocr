import openai
import os
from PIL import Image

openai.api_key = 'sk-proj-zgXqKiXJ3flv7xFoBvdjT3BlbkFJ1hezS1kRuOsw0jTkBEjE'


def get_chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']


def process_image(image_path):
    # Load the image using Pillow
    image = Image.open(image_path)
    # Here you can add any image processing you need
    return image


def main():
    # Prompt user for the image path
    image_path = input("Enter the path to the image file: ")

    if not os.path.isfile(image_path):
        print("File does not exist. Please enter a valid path.")
        return

    # Process the image
    image = process_image(image_path)

    # Display or process the image as needed (optional)
    image.show()

    # Ask user for a question regarding the image
    question = input("What would you like to ask about the image? ")

    # Combine image information and question for context
    prompt = f"Here is an image: {image_path}. {question}"

    # Get the response from ChatGPT
    answer = get_chatgpt_response(prompt)
    print(f"ChatGPT's response: {answer}")


if __name__ == "__main__":
    main()
