import base64
import requests
import os
from pathlib import Path
import json
import time

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_text_from_image(image_path, api_key, output_file):
    try:
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",  # Using the mini model as discussed
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract and return all text visible in this image.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        # Write results to file immediately
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n--- Text from {image_path} ---\n")
            if 'choices' in result and len(result['choices']) > 0:
                f.write(result['choices'][0]['message']['content'])
            else:
                f.write(f"Error processing image. Full response: {json.dumps(result, indent=2)}")

        # Basic rate limiting
        time.sleep(1)

        return True

    except Exception as e:
        # Log errors but don't stop processing
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\nERROR processing {image_path}: {str(e)}\n")
        return False

def main():
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    # Get directory path from user
    dir_path = input("Enter the path to your images directory: ")
    dir_path = Path(dir_path)

    if not dir_path.is_dir():
        print(f"Error: {dir_path} is not a valid directory")
        return

    # Setup output file
    output_file = dir_path / "extracted_text.txt"

    # Process each image
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    total_images = 0
    successful_images = 0

    print(f"Starting text extraction. Results will be saved to {output_file}")

    for image_path in dir_path.glob('*'):
        if image_path.suffix.lower() in image_extensions:
            total_images += 1
            print(f"Processing {image_path.name}...")

            if extract_text_from_image(str(image_path), api_key, output_file):
                successful_images += 1

    print(f"\nProcessing complete!")
    print(f"Successfully processed {successful_images} out of {total_images} images")
    print(f"Results have been saved to {output_file}")

if __name__ == "__main__":
    main()
