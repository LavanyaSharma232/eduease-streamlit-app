# src/services/youtube_service.py
from googleapiclient.discovery import build
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for interacting with the YouTube Data API."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key for YouTube service cannot be empty.")
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {e}")
            raise RuntimeError("Could not build YouTube service client.")

    def get_recommendations(self, topic: str, level: str, max_results: int = 3) -> List[Dict]:
        """
        Fetches YouTube video recommendations based on a topic and learning level.
        """
        logger.info(f"Fetching YouTube recommendations for topic: '{topic}', level: {level}")
        query = f"{topic} for {level.lower()}s tutorial"
        
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='video',
                relevanceLanguage='en',
                order='relevance'
            ).execute()

            recommendations = []
            for item in search_response.get('items', []):
                video_id = item.get('id', {}).get('videoId')
                snippet = item.get('snippet', {})
                if video_id and snippet:
                    recommendations.append({
                        "title": snippet.get('title', 'No Title'),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url')
                    })
            logger.info(f"Found {len(recommendations)} recommendations.")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching YouTube recommendations: {e}")
            return []