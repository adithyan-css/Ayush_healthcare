from app.config import settings
import json

class ClaudeService:
    async def generate_recommendation(self, dosha: str, symptoms: dict, season: str, history: list):
        # In a real app we construct a huge history-aware prompt here and call Anthropic API.
        # Since I'm mocking for demo-readiness as asked:
        prompt = f"Dosha: {dosha}, Symptoms: {symptoms}, Season: {season}. History: {history}"
        
        response = {
            "herbs": ["Ashwagandha", "Brahmi"],
            "diet": {
                "eat": ["Warm cooked grains", "Ghee"],
                "avoid": ["Cold salads", "Dry crackers"]
            },
            "yoga": ["Surya Namaskar", "Vajrasana"],
            "dinacharya": ["Abhyanga (Oil Massage) before bath", "Early to bed by 10 PM"],
            "prevention30": f"Given your {dosha} dosha and {season} season, risk of joint pain is high. Stay hydrated with warm water."
        }
        return response
