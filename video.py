import cv2
import base64
import os
import sys
from openai import OpenAI


def extract_frames(video_path):
    video = cv2.VideoCapture(video_path)
    base64_frames = []

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64_frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    return base64_frames


def get_video_description(frames, client):
    prompt_messages = [
        {
            "role": "user",
            "content": [
                "These are frames from a video. Generate a description of what happens.",
                *map(
                    lambda x: {"image": x, "resize": 768}, frames[0::50]
                ),  # Adjust frame selection as needed
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 333,
    }

    result = client.chat.completions.create(**params)
    return result.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print(
            "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    frames = extract_frames(video_path)
    description = get_video_description(frames, client)
    print("Video Description:", description)
