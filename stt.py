import subprocess
import sys
import os
from openai import OpenAI


# Function to convert AAC to MP3
def convert_aac_to_mp3(aac_file_path, mp3_file_path):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                aac_file_path,
                "-acodec",
                "libmp3lame",
                "-ab",
                "192k",
                mp3_file_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")
        sys.exit(1)


# Function to transcribe audio file
def transcribe_audio_file(audio_file_path):
    client = OpenAI()
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return transcript.text


# Main script logic
if __name__ == "__main__":
    audio_file_path = sys.argv[1]
    file_extension = os.path.splitext(audio_file_path)[1][1:].lower()

    # Check if conversion is needed
    if file_extension != "mp3":
        print(f"Converting {audio_file_path} to MP3 format...")
        mp3_file_path = os.path.splitext(audio_file_path)[0] + ".mp3"
        convert_aac_to_mp3(audio_file_path, mp3_file_path)
        audio_file_path = mp3_file_path  # Update the path to use the converted file

    # Perform transcription
    print(f"Transcribing audio file {audio_file_path}...")
    transcription_text = transcribe_audio_file(audio_file_path)
    print(transcription_text)
