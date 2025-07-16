# src/components/ui.py
import streamlit as st
import re
from contextlib import contextmanager
from typing import List, Dict
from utils.text_processing import TextProcessor  # Corrected import

class UI:
    """A class to manage all UI components and styling for the EduEase app."""

    def apply_custom_css(self):
        """Applies the main CSS to the Streamlit application."""
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            * { font-family: 'Inter', sans-serif; }
            .stApp { background-color: #000000; }
            .main .block-container { padding: 1rem 1rem; }
            .logo-container { text-align: center; padding: 2rem 0; }
            .logo-title {
                font-size: 5rem; font-weight: 800;
                background: -webkit-linear-gradient(45deg, #FF0088, #89f7fe);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            .logo-underline {
                width: 150px; height: 4px;
                background: linear-gradient(90deg, #FF0088, #89f7fe);
                margin: 0 auto; border-radius: 2px;
                box-shadow: 0 0 12px 2px #FF0088, 0 0 12px 2px #89f7fe;
            }
            .hero-title { font-size: 3.5rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; }
            .hero-subtitle { font-size: 1.3rem; color: #E0E0E0; font-weight: 400; margin-bottom: 2rem; }
            .section-header {
                font-size: 1.8rem; font-weight: 600; color: #FFFFFF;
                margin-bottom: 1.5rem; padding-bottom: 0.5rem;
                border-bottom: 3px solid #AEC6CF;
            }
            .hero-section, .input-container, .content-section, .quiz-container {
                background-color: #121212; border: 1px solid #333333;
                border-radius: 20px; padding: 2rem; margin: 1rem auto;
            }
            .input-container { max-width: 600px; background-color: #1E1E1E; }
            .content-section { background-color: #000000; border: none; padding: 2rem 0; }
            .badge {
                display: inline-flex; align-items: center; gap: 0.5rem;
                background: rgba(174, 198, 207, 0.2); color: #AEC6CF;
                padding: 0.5rem 1rem; border-radius: 25px; font-weight: 500;
                margin-bottom: 2rem; border: 1px solid #AEC6CF;
            }
            .stTextInput > div > div > input {
                background-color: #F0F0F0; border-radius: 10px; color: #121212;
                padding: 1rem; font-size: 1rem;
            }
            .stButton > button {
                background-color: #B9FBC0; color: #121212; border: none;
                padding: 1rem 2rem; border-radius: 12px; font-weight: 700;
                font-size: 1.1rem; width: 100%; transition: all 0.3s ease;
            }
            .stButton > button:hover { background-color: #98F9A9; }
            .stTabs [data-baseweb="tab-list"] { gap: 1rem; }
            .stTabs [data-baseweb="tab"] {
                background-color: #1E1E1E; border-radius: 10px; padding: 1rem;
                border: 1px solid #333333; color: #FFFFFF;
            }
            .stTabs [aria-selected="true"] { background-color: #AEC6CF; color: #121212; }
            .quiz-question { font-size: 1.2rem; font-weight: 600; color: #FFFFFF; margin-bottom: 1.5rem; }
            .quiz-option {
                background: #333333; border: 2px solid #555555; color: #FFFFFF;
                border-radius: 10px; padding: 1rem; margin: 0.5rem 0;
                transition: all 0.3s ease;
            }
            .quiz-option:hover { border-color: #AEC6CF; }
            .quiz-option.correct { background: #28a745; border-color: #28a745; }
            .quiz-option.incorrect { background: #dc3545; border-color: #dc3545; }
            .flashcard {
                background-color: #1E1E1E; color: white; border-radius: 15px;
                padding: 2rem; margin: 1rem 0; border: 1px solid #333333;
            }
            .feature-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem; margin: 3rem 0;
            }
            .feature-card {
                background: #1E1E1E; border-radius: 15px; padding: 2rem;
                text-align: center; border: 1px solid #333333;
                transition: all 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-5px); border-color: #AEC6CF; }
            .feature-icon { font-size: 3rem; margin-bottom: 1rem; display: block; color: white; }
            .feature-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: white; }
            .feature-description { color: #E0E0E0; line-height: 1.6; }
            #MainMenu, footer, header { visibility: hidden; }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    def render_header(self):
        st.markdown("""
        <div class="logo-container">
            <div class="logo-title">EduEase</div>
            <div class="logo-underline"></div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_hero_section(self):
        st.markdown("""
        <div class="hero-section">
            <div class="badge">⚡ Designed for cognitive accessibility</div>
            <h1 class="hero-title">Transform YouTube videos into<br>easy-to-understand notes</h1>
            <p class="hero-subtitle">EduEase helps people with ADHD and other cognitive differences learn better by converting video content into clear, structured notes.</p>
        </div>
        """, unsafe_allow_html=True)

    @contextmanager
    def render_input_container(self):
        st.markdown("""
        <div class="input-container">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📹</div>
                <h2 style="color: white; margin-bottom: 0.5rem;">Generate Your Notes</h2>
                <p style="color: #E0E0E0;">Paste any YouTube educational video link below.</p>
            </div>
        """, unsafe_allow_html=True)
        yield
        st.markdown("</div>", unsafe_allow_html=True)

    def render_features_section(self):
        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon">🔮</div><h3 class="feature-title">Simplified Content</h3><p class="feature-description">Complex concepts broken down into easy-to-understand bullet points.</p></div>
            <div class="feature-card"><div class="feature-icon">📋</div><h3 class="feature-title">Structured Notes</h3><p class="feature-description">Organized information with clear headings and key takeaways.</p></div>
            <div class="feature-card"><div class="feature-icon">🎯</div><h3 class="feature-title">ADHD-Friendly</h3><p class="feature-description">Designed with cognitive accessibility and focus in mind.</p></div>
        </div>
        """, unsafe_allow_html=True)

    def render_success_message(self):
        st.markdown("""
        <div style="background: rgba(40, 167, 69, 0.2); border: 1px solid #28a745; 
                     border-radius: 10px; padding: 1rem; margin: 1rem 0; 
                     color: white; text-align: center;">
            ✅ Notes generated successfully!
        </div>
        """, unsafe_allow_html=True)

    def render_video_summary(self):
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📹 Video & Audio Summary</h2>', unsafe_allow_html=True)
        st.video(st.session_state.video_url)
        if st.session_state.summary_audio_data:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**🎧 Listen to Summary**")
            st.audio(st.session_state.summary_audio_data)
        st.markdown('</div>', unsafe_allow_html=True)

    def render_study_guide(self):
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📚 Your Study Guide</h2>', unsafe_allow_html=True)
        
        notes = st.session_state.notes
        # Split notes by headings but keep the headings
        sections = re.split(r'(?=##\s)', notes)
        
        for section in sections:
            if not section.strip(): continue
            if any(keyword in section for keyword in ["MCQ Quiz", "Flashcard Review"]): continue
            
            if "Key Concepts (for Flowchart)" in section:
                graphviz_data = TextProcessor.parse_graphviz(section)
                if graphviz_data: 
                    st.markdown("### 🔗 Key Concepts Flowchart")
                    st.graphviz_chart(graphviz_data)
            elif "Key Takeaways" in section:
                st.markdown(TextProcessor.highlight_keywords(section), unsafe_allow_html=True)
            else:
                st.markdown(section, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    @contextmanager
    def render_roadmap_container(self):
        st.markdown("""
        <div class="input-container" style="max-width: 800px;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🗺️</div>
                <h2 style="color: white; margin-bottom: 0.5rem;">Personalized Learning Roadmap</h2>
                <p style="color: #E0E0E0;">Select your learning level to get recommended videos to watch next.</p>
            </div>
        """, unsafe_allow_html=True)
        yield
        st.markdown("</div>", unsafe_allow_html=True)

    def render_recommendations_list(self, level: str, topic: str, recommendations: List[Dict]):
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown(f'<h2 class="section-header">Your {level} Roadmap for "{topic}"</h2>', unsafe_allow_html=True)
        for video in recommendations:
            st.markdown(f"""
            <a href="{video['url']}" target="_blank" style="text-decoration: none; color: white;">
                <div style="display: flex; align-items: center; background-color: #1E1E1E; border-radius: 15px; padding: 1rem; margin: 1rem 0; border: 1px solid #333333; transition: all 0.3s ease;">
                    <img src="{video['thumbnail']}" style="width: 160px; border-radius: 8px; margin-right: 1.5rem;">
                    <div style="font-weight: 600;">{video['title']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    @contextmanager
    def render_knowledge_check_container(self):
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">🧠 Test Your Knowledge</h2>', unsafe_allow_html=True)
        yield
        st.markdown('</div>', unsafe_allow_html=True)