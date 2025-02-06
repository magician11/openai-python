import subprocess
import sys
import os
from openai import OpenAI
from pydub import AudioSegment

def verify_audio_file(audio_file_path):
    """Verify that the audio file exists and is readable"""
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    try:
        AudioSegment.from_file(audio_file_path)
    except Exception as e:
        raise ValueError(f"Invalid or corrupted audio file: {e}")

def check_size_and_split(audio_file_path):
    """Check file size and split if necessary, with enhanced error handling"""
    try:
        verify_audio_file(audio_file_path)
        file_size = os.path.getsize(audio_file_path)

        if file_size > 25 * 1024 * 1024:  # 25MB limit
            print(f"File size ({file_size/1024/1024:.2f}MB) exceeds 25MB, splitting...")
            song = AudioSegment.from_file(audio_file_path)
            chunk_length_ms = int(25 * 1024 * 1024 * 8 / (192 * 1024) * 1000)
            chunks = make_chunks(song, chunk_length_ms)

            chunk_names = []
            for i, chunk in enumerate(chunks):
                chunk_name = f"{os.path.splitext(audio_file_path)[0]}_part{i}.mp3"
                print(f"Creating chunk {i+1}/{len(chunks)}: {chunk_name}")
                chunk.export(chunk_name, format="mp3", parameters=["-q:a", "0"])
                chunk_names.append(chunk_name)
            return chunk_names
        return [audio_file_path]
    except Exception as e:
        print(f"Error processing audio file: {e}")
        sys.exit(1)

def convert_to_mp3(audio_file_path, mp3_file_path):
    """Convert audio to MP3 with robust error handling"""
    try:
        print(f"Converting {audio_file_path} to MP3...")
        command = [
            "ffmpeg",
            "-i", audio_file_path,
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-ar", "44100",  # Set standard sample rate
            "-y",  # Overwrite output file if it exists
            mp3_file_path
        ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                output=process.stdout,
                stderr=process.stderr
            )

        return mp3_file_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Conversion error: {e}")
        sys.exit(1)

def make_chunks(audio_segment, chunk_length_ms):
    """Create chunks of audio with specified length"""
    return [
        audio_segment[i:i + chunk_length_ms]
        for i in range(0, len(audio_segment), chunk_length_ms)
    ]

def transcribe_audio_file(audio_file_paths):
    """Transcribe audio files with progress reporting"""
    client = OpenAI()
    transcript_texts = []

    if isinstance(audio_file_paths, list):
        total_files = len(audio_file_paths)
        for i, path in enumerate(audio_file_paths, 1):
            print(f"Transcribing file {i}/{total_files}: {path}")
            try:
                with open(path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                    transcript_texts.append(transcript.text)
            except Exception as e:
                print(f"Error transcribing {path}: {e}")
                continue
    else:
        with open(audio_file_paths, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
            transcript_texts.append(transcript.text)

    return " ".join(transcript_texts)

def cleanup_temp_files(file_paths):
    """Clean up temporary chunk files"""
    for path in file_paths:
        if "_part" in path and os.path.exists(path):
            try:
                os.remove(path)
                print(f"Cleaned up temporary file: {path}")
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <audio_file_path>")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    file_extension = os.path.splitext(audio_file_path)[1][1:].lower()
    supported_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]

    try:
        if file_extension not in supported_formats:
            print(f"Converting {audio_file_path} to MP3...")
            mp3_file_path = os.path.splitext(audio_file_path)[0] + ".mp3"
            converted_path = convert_to_mp3(audio_file_path, mp3_file_path)
            audio_file_paths = check_size_and_split(converted_path)
        else:
            print(f"Processing {audio_file_path}...")
            audio_file_paths = check_size_and_split(audio_file_path)

        print("Starting transcription...")
        transcription_text = transcribe_audio_file(audio_file_paths)
        print("\nTranscription result:")
        print("-" * 80)
        print(transcription_text)
        print("-" * 80)

        # Clean up temporary files
        if isinstance(audio_file_paths, list) and len(audio_file_paths) > 1:
            cleanup_temp_files(audio_file_paths)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
