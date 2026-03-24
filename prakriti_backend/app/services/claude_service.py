from app.config import settings
import json

class ClaudeService:
    async def generate_recommendation(self, dosha: str, symptoms: list, season: str, history: list):
        # AI prompt logic with Inject last 3 sessions + dosha + symptoms + season
        # Expected Strict JSON
        response = {
            "herbs": ["Ashwagandha"],
            "diet": {"eat": ["Warm foods"], "avoid": ["Cold foods"]},
            "yoga": ["Surya Namaskar"],
            "dinacharya": ["Wake up early"],
            "prevention30": "Increase hydration to avoid Vata imbalance."
        }
        return response\n