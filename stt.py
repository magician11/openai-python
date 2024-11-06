import subprocess
import sys
import os
from openai import OpenAI
from pydub import AudioSegment


# Function to check file size and split if necessary
def check_size_and_split(audio_file_path):
    try:
        # Check file size
        file_size = os.path.getsize(audio_file_path)
        if file_size > 25 * 1024 * 1024:  # File size greater than 25MB
            song = AudioSegment.from_file(audio_file_path)
            # Calculate chunk length in milliseconds and ensure it's an integer
            chunk_length_ms = int(25 * 1024 * 1024 * 8 / (192 * 1024) * 1000)
            chunks = make_chunks(song, chunk_length_ms)
            chunk_names = []  # List to store the names of the chunks
            for i, chunk in enumerate(chunks):
                chunk_name = f"{os.path.splitext(audio_file_path)[0]}_part{i}.mp3"
                chunk.export(chunk_name, format="mp3")
                chunk_names.append(chunk_name)  # Add the chunk name to the list
            return chunk_names
        else:
            return [audio_file_path]
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


# Function to convert to MP3 and check size
def convert_and_check_size(audio_file_path, mp3_file_path):
    try:
        # Convert to MP3
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                audio_file_path,
                "-acodec",
                "libmp3lame",
                "-ab",
                "192k",
                mp3_file_path,
            ],
            check=True,
        )
        return check_size_and_split(mp3_file_path)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")
        sys.exit(1)


# Function to make chunks of the audio file
def make_chunks(audio_segment, chunk_length_ms):
    return [
        audio_segment[i : i + chunk_length_ms]
        for i in range(0, len(audio_segment), chunk_length_ms)
    ]


# Function to transcribe audio file
def transcribe_audio_file(audio_file_path):
    client = OpenAI()
    transcript_texts = []
    if isinstance(audio_file_path, list):
        for path in audio_file_path:
            with open(path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, language="en"
                )
                transcript_texts.append(transcript.text)
    else:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language="en"
            )
            transcript_texts.append(transcript.text)
    return " ".join(transcript_texts)


# Main script logic
if __name__ == "__main__":
    audio_file_path = sys.argv[1]
    file_extension = os.path.splitext(audio_file_path)[1][1:].lower()

    if file_extension not in ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]:
        print(f"Converting {audio_file_path} to MP3 and checking size...")
        mp3_file_path = os.path.splitext(audio_file_path)[0] + ".mp3"
        audio_file_paths = convert_and_check_size(audio_file_path, mp3_file_path)
    else:
        print(f"Checking size of {audio_file_path}...")
        audio_file_paths = check_size_and_split(audio_file_path)

    # Perform transcription
    print(f"Transcribing audio file(s)...")
    transcription_text = transcribe_audio_file(audio_file_paths)
    print(transcription_text)
