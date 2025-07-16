# src/services/ai_service.py
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
import re
import json
import logging
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Service for all AI-powered content generation and processing."""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash-latest'):
        if not api_key:
            raise ValueError("API key for AI service cannot be empty.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_notes(self, transcript: str) -> Optional[str]:
        """Generates structured study notes from a given transcript."""
        system_prompt = """You are an expert educator for students with learning disabilities. Your task is to transform a video transcript into clear, simple, and engaging study notes. You MUST be creative and avoid repetitive phrasing.
The notes must ALWAYS include these sections, formatted in Markdown with `##` for headings:
1.  ## Title: A creative and relevant title.
2.  ## Detailed Summary: A detailed, easy-to-understand summary.
3.  ## Jargon Buster: Identify 2-3 complex terms. For each, provide a simple, one-sentence "in plain English" explanation.
4.  ## Key Concepts (for Flowchart): Identify the core concepts and their relationships. Format them for a Graphviz flowchart inside a 'dot' code block.
5.  ## Key Takeaways: A bulleted list of important points. Wrap 3-5 keywords in @@keyword@@ markers. **CRUCIAL: If the transcript discusses any mathematical formulas or equations, you MUST convert them into proper LaTeX format and include them in this section. For inline math, use single dollar signs (e.g., `$E=mc^2$`).**
6.  ## Mnemonics: A unique and clever memory aid for a key fact.
7.  ## MCQ Quiz: Generate 3-5 varied multiple-choice questions (what, why, how). Format THIS SECTION ONLY as a valid JSON array. Each object must have "question", "options", "correct_answer", and "hint" keys.
8.  ## Flashcard Review: Generate 3-5 DIFFERENT open-ended questions for flashcard review (e.g., "Explain what X is."). Format THIS SECTION ONLY as a valid JSON array. Each object must have "question" and "answer" keys.
"""
        try:
            logger.info("Generating notes with Google AI.")
            full_prompt = f"{system_prompt}\n\nHere is the transcript:\n{transcript}"
            response = self.model.generate_content(full_prompt)
            if response and hasattr(response, 'text'):
                return response.text
            else:
                logger.error("Google AI response was empty or malformed.")
                return None
        except Exception as e:
            logger.critical(f"A critical error occurred with the Google AI API: {e}")
            return None

    def extract_topic_from_summary(self, notes_text: str) -> Optional[str]:
        """Distills a concise search topic from the summary section of the notes."""
        logger.info("Extracting topic from summary.")
        summary_match = re.search(r'##\s*(Detailed\s)?Summary\s*.*?\n(.*?)(?=##)', notes_text, re.DOTALL | re.IGNORECASE)
        if not summary_match or not summary_match.group(2).strip():
            logger.warning("Could not find a summary in the notes to generate a topic.")
            return "General Educational Topic" # Fallback topic

        summary_text = summary_match.group(2).strip()
        
        try:
            prompt = (f"Based on the following summary, please identify the core topic in 3-5 words. "
                      f"Your response should ONLY be the topic phrase itself, with no extra text or punctuation. "
                      f"For example: 'Quantum Physics Basics'.\n\nSummary: {summary_text}")
            response = self.model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                topic = response.text.strip().replace('"', '')
                logger.info(f"AI returned topic: '{topic}'")
                return topic
            return None
        except Exception as e:
            logger.error(f"AI error while extracting topic: {e}")
            return None

    def generate_audio_summary(self, notes_text: str) -> Optional[BytesIO]:
        """Generates a text-to-speech audio file for the summary section."""
        logger.info("Generating audio summary.")
        summary_match = re.search(r'##\s*(Detailed\s)?Summary\s*.*?\n(.*?)(?=##)', notes_text, re.DOTALL | re.IGNORECASE)
        if not summary_match:
            logger.warning("No summary found to generate audio.")
            return None
        
        summary_text = summary_match.group(2).strip()
        try:
            sound_file = BytesIO()
            tts = gTTS(text=summary_text, lang='en')
            tts.write_to_fp(sound_file)
            sound_file.seek(0) # Rewind the file to the beginning
            return sound_file
        except Exception as e:
            logger.error(f"Failed to generate gTTS audio summary: {e}")
            return None
            
    def parse_json_from_notes(self, notes_text: str, key: str) -> List[Dict]:
        """Parses a JSON block from the generated notes for a specific section key."""
        logger.info(f"Parsing JSON for section: {key}")
        pattern = re.compile(f'##\\s*{key}[\\s\\S]*?```json\\s*([\\s\\S]+?)\\s*```', re.IGNORECASE)
        match = pattern.search(notes_text)
        if not match:
            logger.warning(f"No JSON block found for key: {key}")
            return []
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for key {key}: {e}")
            return []