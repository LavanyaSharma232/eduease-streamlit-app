# src/utils/quiz_helpers.py
import re
from typing import List, Optional

class QuizHelpers:
    """Helper functions for quiz functionality."""
    
    @staticmethod
    def find_correct_option_index(options: List[str], correct_answer: str) -> Optional[int]:
        """
        Finds the index of the correct option from a list of choices.
        It tries multiple matching strategies for robustness.
        """
        if not options or not correct_answer:
            return None
        
        correct_answer_clean = correct_answer.strip().upper()
        
        # Strategy 1: Direct letter match (e.g., "A", "B")
        if len(correct_answer_clean) == 1 and 'A' <= correct_answer_clean <= 'Z':
            try:
                # Converts 'A' to 0, 'B' to 1, etc.
                return ord(correct_answer_clean) - ord('A')
            except (ValueError, IndexError):
                pass # Fall through to other strategies

        # Strategy 2: Content similarity
        for i, option in enumerate(options):
            if option:
                option_clean = option.strip().upper()
                # Remove prefixes like "A)", "B.", etc.
                option_content = re.sub(r'^[A-Z][\)\.\s]+', '', option_clean).strip()
                
                # Check for an exact or near-exact match
                if (correct_answer_clean == option_content or 
                    correct_answer_clean in option_content or
                    option_content in correct_answer_clean):
                    return i
        
        # Strategy 3: Best partial match as a fallback
        best_match_index, best_match_score = None, 0
        for i, option in enumerate(options):
            if option:
                option_content = re.sub(r'^[A-Z][\)\.\s]+', '', option.strip().upper())
                common_words = set(correct_answer_clean.split()) & set(option_content.split())
                score = len(common_words)
                if score > best_match_score:
                    best_match_score = score
                    best_match_index = i
        
        return best_match_index if best_match_score > 0 else None