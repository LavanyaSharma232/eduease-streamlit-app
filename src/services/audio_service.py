# src/services/audio_service.py
import os
import yt_dlp
from faster_whisper import WhisperModel
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioService:
    """Service for video audio extraction and speech-to-text transcription."""
    
    def __init__(self, model_name: str = "base"):
        try:
            logger.info("Initializing WhisperModel...")
            self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
            logger.info("WhisperModel initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            raise RuntimeError(f"Could not load Whisper model '{model_name}'.")

    def extract_audio_from_video(self, video_url: str) -> Optional[str]:
        """
        Downloads a YouTube video and extracts the audio into a temporary MP3 file.
        Returns the path to the audio file.
        """
        logger.info(f"Starting audio extraction for URL: {video_url}")
        audio_path = "Target_audio.mp3"
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': 'Target_audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                raise FileNotFoundError("Audio file was not created or is empty after download.")
            
            logger.info(f"Audio extracted successfully to {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error during video download or audio extraction: {e}")
            self._cleanup_temp_file(audio_path)
            return None

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribes an audio file to text using the Whisper model.
        Cleans up the audio file after transcription.
        """
        if not os.path.exists(audio_path):
            logger.error(f"Transcription failed: Audio file not found at {audio_path}")
            return None
        
        logger.info(f"Starting transcription for {audio_path}")
        try:
            segments, _ = self.model.transcribe(audio_path, beam_size=5)
            transcript = "".join(segment.text for segment in segments)
            logger.info("Transcription completed.")
            return transcript
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            return None
        finally:
            self._cleanup_temp_file(audio_path)
            
    def _cleanup_temp_file(self, file_path: str):
        """Removes a file if it exists."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except OSError as e:
            logger.warning(f"Could not clean up file {file_path}: {e}")