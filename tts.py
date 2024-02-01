from pathlib import Path
from openai import OpenAI
import sys

client = OpenAI()

# Define the path to the text file from the first command line argument
text_file_path = Path(sys.argv[1])

# Open the text file and read its contents
with open(text_file_path, "r") as file:
    text_input = file.read()

speech_file_path = Path(__file__).parent / "speech.mp3"

# Use the contents of the text file as the input
response = client.audio.speech.create(
    model="tts-1", voice="nova", input=text_input, speed=1
)

response.stream_to_file(speech_file_path)

# Smooth and Silent - Shimano Steps E7000 motor with max torque of 70Nm.
# Long Range Battery - Up to 150km range, chargeable in 3.5 hours.
# Smooth Shifting - Shimano Deore M6000 gears for improved stability and retention.
