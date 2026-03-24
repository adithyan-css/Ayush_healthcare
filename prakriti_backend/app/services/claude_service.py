import json
import httpx
from fastapi import HTTPException
from app.config import settings


class ClaudeService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = 'gemini-1.5-pro'
        self.base_url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent'

    def _extract_text(self, response_json: dict) -> str:
        candidates = response_json.get('candidates', [])
        if not candidates:
            return ''
        parts = candidates[0].get('content', {}).get('parts', [])
        if not parts:
            return ''
        return (parts[0].get('text') or '').strip()

    def _clean_json_text(self, text: str) -> str:
        if text.startswith('```json'):
            return text[7:-3].strip()
        if text.startswith('```'):
            return text[3:-3].strip()
        return text

    async def _generate_json(self, prompt: str, max_tokens: int, temperature: float):
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
                'responseMimeType': 'application/json',
            },
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f'{self.base_url}?key={self.api_key}',
                json=payload,
                headers={'Content-Type': 'application/json'},
            )
            response.raise_for_status()
            raw = self._extract_text(response.json())
            return json.loads(self._clean_json_text(raw))

    async def generate_recommendation(self, dosha: str, vata: float, pitta: float, kapha: float, season: str, symptoms: list, history: list, free_text: str = None, lang: str = 'en'):
        if not self.api_key:
            return {
                'herbs': [{'name': 'Ashwagandha', 'benefit': 'Stress relief', 'dosage': '1 tsp', 'timing': 'night'}],
                'diet': {'eat': [{'food': 'Warm grains', 'reason': 'Balances Vata'}], 'avoid': [{'food': 'Cold salads', 'reason': 'Increases Vata'}]},
                'yoga': [{'name': 'Surya Namaskar', 'duration': '10 min', 'benefit': 'Full body warm up'}],
                'dinacharya': [{'time': '06:00', 'activity': 'Wake up and drink warm water'}],
                'prevention_30day': f'GOOGLE_API_KEY missing. Default response for {dosha} dosha.'
            }

        hist_str = '\n'.join([f"- {h.get('date', '')}: {', '.join(h.get('symptoms', []))}" for h in history]) if history else 'None'
        prompt = f"""You are an expert AYUSH health advisor.
User Prakriti: {dosha} dosha ({vata}% Vata, {pitta}% Pitta, {kapha}% Kapha)
Current Season: {season}
Past consultations (last 3):
{hist_str}
Current symptoms: {', '.join(symptoms)}
{free_text or ''}
Return ONLY valid JSON (no markdown fences, no explanation):
{{"herbs":[{{"name":"","benefit":"","dosage":"","timing":""}}],"diet":{{"eat":[{{"food":"","reason":""}}],"avoid":[{{"food":"","reason":""}}]}},"yoga":[{{"name":"","duration":"","benefit":""}}],"dinacharya":[{{"time":"","activity":""}}],"prevention_30day":"string paragraph"}}
Respond in language: {lang}"""
        try:
            return await self._generate_json(prompt=prompt, max_tokens=2000, temperature=0.2)
        except Exception as e:
            print(f'Gemini Error: {e}')
            raise HTTPException(status_code=500, detail='Failed to fetch AI recommendation.')

    async def generate_xai_explanation(self, district: str, level: str, score: float, condition: str, trend: str, weather_summary: str, social_summary: str):
        if not self.api_key:
            return ['High humidity detected.', 'Rising social signals.', 'Seasonal pattern matches historical outbreak.']
        prompt = f"""You are a public health AI. District: {district}, Risk: {level} ({score}/100), Top condition: {condition}, Trend: {trend}, Weather: {weather_summary}, Social signals: {social_summary}.
Return ONLY a JSON array of 4-5 strings, each a specific data-driven reason with numbers.
Example: [\"340% above-normal rainfall precedes dengue spike\", \"AQI above 150 for 5 consecutive days\"]"""
        try:
            return await self._generate_json(prompt=prompt, max_tokens=800, temperature=0.1)
        except Exception:
            return ['Weather indicators suggest elevated risk.', 'Social trend data confirms anomalies in region.']

    async def generate_vaidya_suggestion(self, symptoms: list, dosha: str, history: list):
        if not self.api_key:
            return {'formulations': ['Triphala 500mg'], 'rationale': 'Balances all three doshas', 'cautions': ['Do not exceed recommended dose']}
        prompt = f"""Patient Dosha: {dosha}. Symptoms: {symptoms}. History: {history}.
Return ONLY strict JSON: {{\"formulations\": [\"\"], \"rationale\": \"\", \"cautions\": [\"\"]}}"""
        try:
            return await self._generate_json(prompt=prompt, max_tokens=1000, temperature=0.2)
        except Exception:
            return {'formulations': ['Consult specialist'], 'rationale': 'API Error', 'cautions': []}
