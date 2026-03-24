import json
class ClaudeService:
    def get_recommendation(self, history, dosha, season, symptoms):
        return {
            "herbs": ["Ashwagandha", "Tulsi"],
            "diet": {"eat": ["Warm foods"], "avoid": ["Cold drinks"]},
            "yoga": ["Surya Namaskar"],
            "dinacharya": ["Early to bed"],
            "prevention30": "Risk of Vata imbalance"
        }
