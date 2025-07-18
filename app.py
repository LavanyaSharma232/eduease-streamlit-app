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

def initialize_session_state():
    """Initialize all session state variables with default values."""
    # User authentication - FIXED: Only initialize if key doesn't exist
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    
    # Notes and history
    if 'notes_history' not in st.session_state:
        st.session_state.notes_history = []
    
    if 'notes' not in st.session_state:
        st.session_state.notes = None
    
    # Video processing
    if 'video_url' not in st.session_state:
        st.session_state.video_url = ""
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Audio and summary
    if 'summary_audio_data' not in st.session_state:
        st.session_state.summary_audio_data = None
    
    # Quiz and learning content
    if 'mcq_questions' not in st.session_state:
        st.session_state.mcq_questions = []
    
    if 'flashcard_questions' not in st.session_state:
        st.session_state.flashcard_questions = []
    
    # Topic and roadmap
    if 'topic_title' not in st.session_state:
        st.session_state.topic_title = ""
    
    if 'roadmap_recommendations' not in st.session_state:
        st.session_state.roadmap_recommendations = None
    
    if 'learning_level' not in st.session_state:
        st.session_state.learning_level = "Beginner"
    
    # Quiz state management
    if 'mcq_current_index' not in st.session_state:
        st.session_state.mcq_current_index = 0
    
    if 'flashcard_current_index' not in st.session_state:
        st.session_state.flashcard_current_index = 0
    
    if 'mcq_answer_submitted' not in st.session_state:
        st.session_state.mcq_answer_submitted = False
    
    if 'mcq_user_answer' not in st.session_state:
        st.session_state.mcq_user_answer = None

class EduEaseApp:
    """The main class for the EduEase Streamlit application."""
    
    def __init__(self):
        """
        Initializes the application and its core components.
        Crucially, it also ensures the Streamlit session state is initialized.
        """
        # --- KEY CHANGE: Initialize session state first ---
        initialize_session_state()
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Now, initialize all other services and components
        self.settings = settings
        self.audio_service, self.ai_service, self.youtube_service = init_services()
        self.ui = UI()
        self.quiz_component = QuizComponent()

    def _render_signin_form(self):
        """Renders a simple form to ask for the user's name."""
        self.ui.render_header()  # Render header without a name
        with self.ui.render_input_container():
            st.markdown("<h3 style='text-align: center; color: white;'>What should we call you?</h3>", unsafe_allow_html=True)
            name = st.text_input(
                "Enter your name",
                label_visibility="collapsed",
                placeholder="e.g., Alex",
                key="user_name_input"  # Added unique key
            )
            if st.button("Continue", use_container_width=True, key="continue_button"):
                if name:
                    st.session_state.user_name = name
                    st.rerun()  # Rerun the app to pass the sign-in gate
                else:
                    st.warning("Please enter your name to continue.", icon="⚠️")

    def _run_main_app(self):
        """Runs the main logic of the app after the user has signed in."""
        # This method contains the logic that was previously in run()
        
        self._render_history_sidebar()
        
        # Render the header, now with the user's name
        self.ui.render_header(user_name=st.session_state.user_name)

        # Conditional rendering based on the application's state
        if st.session_state.processing:
            self._handle_processing()
        elif st.session_state.notes:
            self._render_results()
        else:
            self._render_home_page()
        
    def run(self):
        """
        Main application execution logic. Assumes session is already initialized.
        """
        # Apply CSS and render the UI components
        self.ui.apply_custom_css()
        
        # Check if user is signed in - FIXED: Check for None or empty string
        if not st.session_state.user_name:
            # If not, render the sign-in form and stop further execution.
            self._render_signin_form()
        else:
            # If we have the name, run the full application.
            self._run_main_app()

    def _render_home_page(self):
        """Renders the initial page with the input form and feature descriptions."""
        self.ui.render_hero_section()
        self._render_input_section()
        self.ui.render_features_section()

    def _render_history_sidebar(self):
        """Renders the sidebar for displaying and managing notes history."""
        with st.sidebar:
            st.title("📜 Notes History")
            st.markdown("---")

            if st.button("Clear History", use_container_width=True):
                self.session_manager.clear_history()
                st.rerun()

            if not st.session_state.notes_history:
                st.info("Your generated notes will appear here.")
            else:
                for i, entry in enumerate(st.session_state.notes_history):
                    # Use the topic title for the button label
                    button_label = entry.get('topic_title', f"Note #{i+1}")
                    if st.button(button_label, key=f"history_{i}", use_container_width=True):
                        self._load_from_history(i)

    def _load_from_history(self, index: int):
        """Loads a selected note from the history into the main session state."""
        # 1. Get the selected entry
        history_entry = st.session_state.notes_history[index]
        
        # 2. Update the session state with the loaded data
        st.session_state.notes = history_entry['notes']
        st.session_state.video_url = history_entry['video_url']
        st.session_state.summary_audio_data = history_entry['summary_audio_data']
        st.session_state.mcq_questions = history_entry['mcq_questions']
        st.session_state.flashcard_questions = history_entry['flashcard_questions']
        st.session_state.topic_title = history_entry['topic_title']
        st.session_state.roadmap_recommendations = history_entry['roadmap_recommendations']
        st.session_state.learning_level = history_entry['learning_level']
        st.session_state.flowchart_description = history_entry.get('flowchart_description')

        # 3. Reset quiz progress and other temporary states
        st.session_state.mcq_current_index = 0
        st.session_state.flashcard_current_index = 0
        st.session_state.mcq_answer_submitted = False
        st.session_state.mcq_user_answer = None
        st.session_state.processing = False
        
        # 4. Rerun the app to display the loaded notes
        st.rerun()

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
                self.session_manager.reset_session()  # Reset state on failure

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
        st.session_state.flowchart_description = self.ai_service.parse_flowchart_description(notes_text) 

        # Check if this video already exists in history
        video_exists = any(
            entry['video_url'] == st.session_state.video_url for entry in st.session_state.notes_history
        )

        # If it's a new video, add it to the history
        if not video_exists:
            history_entry = {
                "video_url": st.session_state.video_url,
                "topic_title": st.session_state.topic_title,
                "notes": st.session_state.notes,
                "mcq_questions": st.session_state.mcq_questions,
                "flashcard_questions": st.session_state.flashcard_questions,
                "summary_audio_data": st.session_state.summary_audio_data,
                "roadmap_recommendations": None,  # Reset roadmap for history items
                "learning_level": "Beginner"
            }
            # Insert at the beginning to show the most recent first
            st.session_state.notes_history.insert(0, history_entry)

    def _render_results(self):
        """Renders the complete output: notes, roadmap, and quizzes."""
        if st.button("⬅️ Back to Home"):
            self.session_manager.reset_session()
            st.rerun()

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
            if mcq: 
                tabs_to_show.append("🎯 Interactive Quiz")
            if flashcards: 
                tabs_to_show.append("📚 Flashcards")
            
            if not tabs_to_show: 
                return
            
            tabs = st.tabs(tabs_to_show)
            
            if "🎯 Interactive Quiz" in tabs_to_show:
                with tabs[tabs_to_show.index("🎯 Interactive Quiz")]:
                    self.quiz_component.render_mcq_quiz(mcq)

            if "📚 Flashcards" in tabs_to_show:
                with tabs[tabs_to_show.index("📚 Flashcards")]:
                    self.quiz_component.render_flashcards(flashcards)


if __name__ == '__main__':
    # Per Streamlit best practices, set page config as the very first command
    st.set_page_config(page_title="EduEase", page_icon="🧠", layout="wide")

    # Create an instance of the app. This will automatically call __init__
    # and initialize the session state before doing anything else.
    app = EduEaseApp()

    # Now, run the application's main logic
    app.run()