# app.py
import streamlit as st
import sys
from pathlib import Path

# Add the src directory to the Python path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from config.settings import Settings
from services.audio_service import AudioService
from services.ai_service import AIService
from services.youtube_service import YouTubeService
from utils.session_manager import SessionManager
from components.ui import UI
from components.quiz_component import QuizComponent

# --- Initialization ---

# Load settings (this will also check for the API key)
try:
    settings = Settings()
except Exception as e:
    st.error(f"Fatal error during initialization: {e}")
    st.stop()


# Initialize services with Streamlit's caching
@st.cache_resource
def init_services():
    """Initialize all services with caching to prevent re-creation on each rerun."""
    try:
        audio_service = AudioService()
        ai_service = AIService(api_key=settings.GOOGLE_API_KEY)
        youtube_service = YouTubeService(api_key=settings.GOOGLE_API_KEY)
        return audio_service, ai_service, youtube_service
    except Exception as e:
        st.error(f"Failed to initialize critical services: {e}", icon="🚨")
        st.stop()

class EduEaseApp:
    """The main class for the EduEase Streamlit application."""
    def __init__(self):
        self.settings = settings
        self.audio_service, self.ai_service, self.youtube_service = init_services()
        self.ui = UI()
        self.quiz_component = QuizComponent()
        self.session_manager = SessionManager()

    def run(self):
        """Main application execution logic."""
        st.set_page_config(page_title="EduEase", page_icon="🧠", layout="wide")
        self.ui.apply_custom_css()
        self.session_manager.initialize_session()

        self.ui.render_header()

        # Conditional rendering based on the application's state
        if st.session_state.processing:
            self._handle_processing()
        elif st.session_state.notes:
            self._render_results()
        else:
            self._render_home_page()

    def _render_home_page(self):
        """Renders the initial page with the input form and feature descriptions."""
        self.ui.render_hero_section()
        self._render_input_section()
        self.ui.render_features_section()

    def _render_input_section(self):
        """Renders the YouTube URL input container."""
        with self.ui.render_input_container():
            video_url = st.text_input(
                label="YouTube Video URL",
                placeholder="https://youtube.com/watch?v=...",
                key="video_input",
                label_visibility="collapsed"
            )
            if st.button("📝 Generate Notes", use_container_width=True):
                if "youtube.com" in video_url or "youtu.be" in video_url:
                    if video_url != st.session_state.video_url:
                        self.session_manager.reset_session()
                    st.session_state.video_url = video_url
                    st.session_state.processing = True
                    st.rerun()
                else:
                    st.warning("Please enter a valid YouTube URL.", icon="⚠️")

    def _handle_processing(self):
        """Handles the multi-step process of generating notes from a video."""
        st.markdown('<div class="content-section" style="text-align: center;">', unsafe_allow_html=True)
        with st.spinner('🧙‍♂️ Our AI is working its magic... This might take a moment.'):
            try:
                # 1. Extract audio
                audio_path = self.audio_service.extract_audio_from_video(st.session_state.video_url)
                if not audio_path:
                    raise Exception("Failed to extract audio from the video.")

                # 2. Transcribe audio
                transcript = self.audio_service.transcribe_audio(audio_path)
                if not transcript:
                    raise Exception("Audio transcription failed or produced no text.")

                # 3. Generate notes from transcript
                notes_text = self.ai_service.generate_notes(transcript)
                if not notes_text:
                    raise Exception("The AI model failed to generate notes.")
                
                # 4. Process and store the generated content
                self._process_and_store_notes(notes_text)

            except Exception as e:
                st.error(f"An error occurred: {e}", icon="🚨")
                self.session_manager.reset_session() # Reset state on failure

        st.session_state.processing = False
        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    def _process_and_store_notes(self, notes_text):
        """Updates the session state with all generated content."""
        st.session_state.notes = notes_text
        st.session_state.mcq_questions = self.ai_service.parse_json_from_notes(notes_text, "MCQ Quiz")
        st.session_state.flashcard_questions = self.ai_service.parse_json_from_notes(notes_text, "Flashcard Review")
        st.session_state.topic_title = self.ai_service.extract_topic_from_summary(notes_text)
        st.session_state.summary_audio_data = self.ai_service.generate_audio_summary(notes_text)


    def _render_results(self):
        """Renders the complete output: notes, roadmap, and quizzes."""
        self.ui.render_success_message()
        self.ui.render_video_summary()
        self.ui.render_study_guide()
        self._render_learning_roadmap()
        self._render_knowledge_check()

    def _render_learning_roadmap(self):
        """Renders the personalized learning roadmap section."""
        with self.ui.render_roadmap_container():
            st.session_state.learning_level = st.selectbox(
                "What is your current level on this topic?",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.learning_level)
            )

            if st.button("🚀 Generate My Roadmap", use_container_width=True):
                if st.session_state.topic_title:
                    with st.spinner("Finding the best videos for your level..."):
                        st.session_state.roadmap_recommendations = self.youtube_service.get_recommendations(
                            st.session_state.topic_title,
                            st.session_state.learning_level
                        )
                else:
                    st.warning("Could not determine the topic to generate a roadmap.", icon="⚠️")
        
        if st.session_state.roadmap_recommendations:
            self.ui.render_recommendations_list(
                st.session_state.learning_level,
                st.session_state.topic_title,
                st.session_state.roadmap_recommendations
            )
            
    def _render_knowledge_check(self):
        """Renders the tabs for the MCQ quiz and flashcards."""
        mcq = st.session_state.mcq_questions
        flashcards = st.session_state.flashcard_questions

        if not mcq and not flashcards:
            return

        with self.ui.render_knowledge_check_container():
            tabs_to_show = []
            if mcq: tabs_to_show.append("🎯 Interactive Quiz")
            if flashcards: tabs_to_show.append("📚 Flashcards")
            
            if not tabs_to_show: return
            
            tabs = st.tabs(tabs_to_show)
            
            if "🎯 Interactive Quiz" in tabs_to_show:
                with tabs[tabs_to_show.index("🎯 Interactive Quiz")]:
                    self.quiz_component.render_mcq_quiz(mcq)

            if "📚 Flashcards" in tabs_to_show:
                with tabs[tabs_to_show.index("📚 Flashcards")]:
                    self.quiz_component.render_flashcards(flashcards)


if __name__ == '__main__':
    app = EduEaseApp()
    app.run()