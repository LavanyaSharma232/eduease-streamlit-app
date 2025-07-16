# src/utils/session_manager.py
import streamlit as st

class SessionManager:
    """A helper class to manage Streamlit's session state."""

    # Define the default state for the application
    DEFAULT_STATE = {
        "notes": "",
        "video_url": "",
        "summary_audio_data": None,
        "mcq_questions": [],
        "flashcard_questions": [],
        "mcq_current_index": 0,
        "flashcard_current_index": 0,
        "mcq_answer_submitted": False,
        "mcq_user_answer": None,
        "processing": False,
        "learning_level": "Beginner",
        "roadmap_recommendations": None,
        "topic_title": None,
    }
    
    @classmethod
    def initialize_session(cls):
        """Initializes the session state with default values if they don't exist."""
        for key, default_value in cls.DEFAULT_STATE.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @classmethod
    def reset_session(cls):
        """Resets the entire session state to its default values."""
        for key, default_value in cls.DEFAULT_STATE.items():
            st.session_state[key] = default_value