import json
from typing import Any

import httpx

from app.config import settings


class RecommendationService:
    def __init__(self):
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL

    async def generate_recommendation(
        self,
        dosha: str,
        vata: float,
        pitta: float,
        kapha: float,
        season: str,
        symptoms: list[str],
        history: list[dict],
        free_text: str | None,
        language: str,
    ) -> dict[str, Any]:
        if self.anthropic_api_key:
            try:
                return await self._generate_with_claude(dosha, vata, pitta, kapha, season, symptoms, history, free_text, language)
            except Exception:
                pass
        return self._rule_based_fallback(dosha, season, symptoms)

    async def _generate_with_claude(
        self,
        dosha: str,
        vata: float,
        pitta: float,
        kapha: float,
        season: str,
        symptoms: list[str],
        history: list[dict],
        free_text: str | None,
        language: str,
    ) -> dict[str, Any]:
        history_text = '\n'.join([f"- {item.get('date', 'NA')}: {item.get('symptoms', [])}" for item in history[:3]]) or 'None'
        prompt = (
            'You are an AYUSH doctor assistant. Return ONLY valid JSON with keys '
            'herbs, diet, yoga, dinacharya, prevention_30day. '\
            f'Language: {language}. Dosha={dosha}, scores=({vata},{pitta},{kapha}), season={season}, symptoms={symptoms}, notes={free_text or "None"}. '\
            f'History:\n{history_text}. '\
            'Schema: {"herbs":[{"name":"","dosage":"","timing":""}],"diet":{"eat":[],"avoid":[]},"yoga":[],"dinacharya":[],"prevention_30day":""}'
        )

        payload = {
            'model': self.model,
            'max_tokens': 1200,
            'temperature': 0.2,
            'messages': [{'role': 'user', 'content': prompt}],
        }

        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.anthropic_api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json',
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        text_chunks = []
        for part in data.get('content', []):
            if part.get('type') == 'text':
                text_chunks.append(part.get('text', ''))
        text = ''.join(text_chunks).strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
        return json.loads(text)

    def _rule_based_fallback(self, dosha: str, season: str, symptoms: list[str]) -> dict[str, Any]:
        dosha_key = dosha.lower()
        if dosha_key == 'pitta':
            herbs = [
                {'name': 'Guduchi', 'dosage': '500 mg', 'timing': 'after lunch'},
                {'name': 'Amalaki', 'dosage': '1 tsp powder', 'timing': 'morning'},
            ]
            diet_eat = ['Cucumber', 'Bottle gourd', 'Warm but not spicy meals']
            diet_avoid = ['Excess chili', 'Deep fried food', 'Late-night meals']
        elif dosha_key == 'kapha':
            herbs = [
                {'name': 'Trikatu', 'dosage': '250 mg', 'timing': 'before meals'},
                {'name': 'Tulsi', 'dosage': '2 leaves tea', 'timing': 'morning'},
            ]
            diet_eat = ['Millets', 'Warm soups', 'Light spiced meals']
            diet_avoid = ['Cold dairy', 'Sugary desserts', 'Heavy dinner']
        else:
            herbs = [
                {'name': 'Ashwagandha', 'dosage': '500 mg', 'timing': 'night'},
                {'name': 'Triphala', 'dosage': '1 tsp', 'timing': 'bedtime'},
            ]
            diet_eat = ['Warm cooked meals', 'Stewed fruits', 'Ghee in moderation']
            diet_avoid = ['Cold raw salads at night', 'Irregular meals', 'Excess fasting']

        return {
            'herbs': herbs,
            'diet': {'eat': diet_eat, 'avoid': diet_avoid},
            'yoga': ['Anulom Vilom 10 min', 'Surya Namaskar 10 min'],
            'dinacharya': [
                {'time': '06:00', 'activity': 'Warm water and breathwork'},
                {'time': '12:30', 'activity': 'Main meal with seasonal foods'},
                {'time': '22:00', 'activity': 'Sleep hygiene routine'},
            ],
            'prevention_30day': f'Follow a {dosha} balancing routine in {season}, monitor symptoms: {", ".join(symptoms[:4])}.',
        }

    def generate_prevention_plan(self, location: str, risk_score: int, dosha: str, season: str) -> str:
        return (
            f'30-day plan for {location}: keep a {dosha}-balancing routine in {season}, '\
            f'monitor weekly risk score ({risk_score}/100), maintain early sleep, daily pranayama, '\
            'and fresh seasonal AYUSH diet.'
        )
