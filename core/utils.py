import os
import whisper
from moviepy import VideoFileClip

# Load Whisper model once globally (optional optimization)
model = whisper.load_model("medium")  # You can also try "small.en" or "large" if needed

def process_video(video_path):
    try:
        # Extract audio from video and save as WAV or MP3
        audio_path = video_path.replace(".mp4", ".mp3")  # safer for Whisper

        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)

        # Transcribe using Whisper
        result = model.transcribe(audio_path)

        return result['text']

    except Exception as e:
        return f"Error during processing: {str(e)}"
