# src/utils/text_processing.py
import re
from typing import Optional

class TextProcessor:
    """Utility class for text processing and formatting operations."""
    
    @staticmethod
    def parse_graphviz(notes_text: str) -> Optional[str]:
        """Parses Graphviz content from notes and applies styling."""
        match = re.search(r"```dot\s*([\s\S]+?)\s*```", notes_text)
        if not match:
            return None
            
        content = match.group(1).strip()
        # Ensure it is a valid digraph
        if not content.startswith('digraph'):
            content = f'digraph G {{ {content} }}'
            
        # Inject styling
        styling = 'bgcolor="transparent"; node [style="filled", shape="box", fillcolor="#AEC6CF", fontcolor="#121212", color="#FFFFFF", penwidth=2, fontname="Inter"]; edge [color="#FFFFFF", fontname="Inter"];'
        return content.replace('{', f'{{ {styling}', 1)

    @staticmethod
    def highlight_keywords(text: str) -> str:
        """Highlights keywords enclosed in @@...@@ with colored spans."""
        colors = ["#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A9DEF9", "#FFC0CB"]
        
        def color_replacer(match):
            keyword = match.group(1)
            # Use a simple hash to pick a color consistently
            color = colors[hash(keyword) % len(colors)]
            return (f'<span style="background-color: {color}; color: #121212; '
                    f'padding: 3px 6px; border-radius: 5px; font-weight: 600;">'
                    f'{keyword}</span>')
        
        return re.sub(r"@@(.*?)@@", color_replacer, text)