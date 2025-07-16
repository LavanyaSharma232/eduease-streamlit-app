# src/components/quiz_component.py
import streamlit as st
from typing import List, Dict
from utils.quiz_helpers import QuizHelpers
from utils.session_manager import SessionManager

class QuizComponent:
    """A component to render interactive quizzes and flashcards."""

    def render_mcq_quiz(self, mcq_questions: List[Dict]):
        """Renders the entire MCQ quiz interface."""
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        
        idx = st.session_state.mcq_current_index
        if idx >= len(mcq_questions):
            st.info("You have completed the quiz!")
            if st.button("Restart Quiz"):
                SessionManager.reset_session()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return

        q_data = mcq_questions[idx]
        st.markdown(f'<div style="font-size: 1rem; color: #AAAAAA; margin-bottom: 1rem;">Question {idx + 1} of {len(mcq_questions)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="quiz-question">{q_data["question"]}</div>', unsafe_allow_html=True)
        
        options = q_data.get('options', [])
        correct_answer = q_data.get('correct_answer', '')
        
        if not options or not correct_answer:
            st.error("Quiz question is malformed. Cannot display.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        correct_idx = QuizHelpers.find_correct_option_index(options, correct_answer)
        if correct_idx is None:
            st.error(f"Could not determine the correct answer for the question.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        if st.session_state.mcq_answer_submitted:
            self._render_mcq_results(options, correct_idx, q_data.get('hint'))
        else:
            self._render_mcq_selection(options)
            
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_mcq_selection(self, options: List[str]):
        """Renders the radio buttons for answer selection."""
        user_choice = st.radio("Select your answer:", options, index=None, label_visibility="collapsed", key=f"mcq_radio_{st.session_state.mcq_current_index}")
        
        if st.button("Submit Answer", use_container_width=True):
            if user_choice:
                st.session_state.mcq_user_answer = user_choice
                st.session_state.mcq_answer_submitted = True
                st.rerun()
            else:
                st.warning("Please select an answer.", icon="⚠️")

    def _render_mcq_results(self, options: List[str], correct_idx: int, hint: str):
        """Displays the results after a user has submitted an answer."""
        user_answer = st.session_state.mcq_user_answer
        user_idx = options.index(user_answer) if user_answer in options else -1

        for i, option in enumerate(options):
            style_class = "quiz-option"
            if i == correct_idx:
                style_class += " correct"
                label = "✅ "
            elif i == user_idx:
                style_class += " incorrect"
                label = "❌ "
            else:
                label = ""
            st.markdown(f'<div class="{style_class}">{label}{option}</div>', unsafe_allow_html=True)

        if user_idx == correct_idx:
            st.success("🎉 Correct! Well done!", icon="✅")
        else:
            st.error(f"❌ Not quite. The correct answer was option {chr(65+correct_idx)}.", icon="🚫")
            if hint:
                st.info(f"💡 Hint: {hint}", icon="💡")

        st.markdown("---")
        if st.button("Next Question ➡️", use_container_width=True):
            st.session_state.mcq_current_index += 1
            st.session_state.mcq_answer_submitted = False
            st.session_state.mcq_user_answer = None
            st.rerun()

    def render_flashcards(self, flashcard_questions: List[Dict]):
        """Renders the flashcard review interface."""
        idx = st.session_state.flashcard_current_index
        if idx >= len(flashcard_questions):
            st.info("No more flashcards!")
            return

        q_data = flashcard_questions[idx]
        st.markdown(f'<div style="font-size: 1rem; color: #AAAAAA; margin-bottom: 1rem;">Flashcard {idx + 1} of {len(flashcard_questions)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="flashcard"><div style="font-size: 1.2rem; font-weight: 600;">{q_data["question"]}</div></div>', unsafe_allow_html=True)

        with st.expander("🤔 Reveal Answer"):
            st.success(f"**Answer:** {q_data['answer']}")
        
        st.write("")
        col1, col2, _ = st.columns([1, 1, 4])
        if col1.button("⬅️ Previous", use_container_width=True, disabled=(idx <= 0), key="prev_flash"):
            st.session_state.flashcard_current_index -= 1
            st.rerun()
        if col2.button("Next ➡️", use_container_width=True, disabled=(idx >= len(flashcard_questions) - 1), key="next_flash"):
            st.session_state.flashcard_current_index += 1
            st.rerun()