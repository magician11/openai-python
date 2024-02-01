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
        base64_encoded_frame = base64.b64encode(buffer).decode("utf-8")
        base64_frames.append(base64_encoded_frame)

    video.release()
    return base64_frames


def get_video_description(
    frames, prompt, client, frame_interval, save_frames=False, save_dir="saved_frames"
):
    if save_frames and not os.path.exists(save_dir):
        os.makedirs(save_dir)

    selected_frames = []
    for i, frame in enumerate(frames):
        if i % frame_interval == 0:
            selected_frames.append(frame)

            if save_frames:
                frame_data = base64.b64decode(frame)
                frame_file = os.path.join(save_dir, f"frame_{i}.jpg")
                with open(frame_file, "wb") as file:
                    file.write(frame_data)

    prompt_messages = [
        {
            "role": "user",
            "content": [
                prompt,
                *map(lambda x: {"image": x}, selected_frames),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 555,
    }

    result = client.chat.completions.create(**params)
    return result.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video.py <video_path> <prompt>")
        sys.exit(1)

    video_path = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    api_key = os.environ.get("OPENAI_API_KEY")
    save_frames = True  # Set to True to save frames locally
    frame_interval = 111  # Adjust as needed

    if not api_key:
        print(
            "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    frames = extract_frames(video_path)
    response = get_video_description(
        frames, prompt, client, frame_interval, save_frames
    )
    print(response)
