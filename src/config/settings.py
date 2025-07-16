# src/config/settings.py
import os
import streamlit as st
from dataclasses import dataclass

@dataclass
class Settings:
    """Manages application settings and API keys loaded from Streamlit secrets."""
    
    # API Keys
    GOOGLE_API_KEY: str = None
    
    # AI/Audio Model Config
    WHISPER_MODEL: str = "base"
    GEMINI_MODEL: str = "gemini-1.5-flash-latest"
    
    def __post_init__(self):
        """Loads API keys after the object is created."""
        self._load_api_keys()

    def _load_api_keys(self):
        """
        Loads the Google API key from Streamlit's secrets management.
        Raises an exception if the key is not found.
        """
        try:
            self.GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
            if not self.GOOGLE_API_KEY:
                raise KeyError
        except KeyError:
            st.error("Google AI API key not found. Please add `GOOGLE_API_KEY` to your Streamlit secrets.", icon="🚨")
            raise Exception("API Key configuration error.")