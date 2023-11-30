from pathlib import Path
from openai import OpenAI

client = OpenAI()

# Define the path to the text file
text_file_path = Path(__file__).parent / "input.txt"

# Open the text file and read its contents
with open(text_file_path, "r") as file:
    text_input = file.read()

speech_file_path = Path(__file__).parent / "speech.mp3"

# Use the contents of the text file as the input
response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=text_input,
)

response.stream_to_file(speech_file_path)
