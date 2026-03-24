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
        return self._rule_based_fallback(dosha, season, symptoms, history)

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

    def _rule_based_fallback(self, dosha: str, season: str, symptoms: list[str], history: list[dict]) -> dict[str, Any]:
        dosha_key = dosha.lower()
        symptoms_l = [s.lower().strip() for s in symptoms]

        rules = {
            'vata': {
                'match': ['anxiety', 'dryness', 'constipation'],
                'herbs': [
                    {'name': 'ashwagandha', 'dosage': '500 mg', 'timing': 'night'},
                    {'name': 'ginger', 'dosage': '2 g tea', 'timing': 'morning'},
                ],
                'diet_eat': ['warm foods', 'soups'],
                'diet_avoid': ['cold raw foods', 'irregular meals'],
                'yoga': ['slow yoga', 'breathing'],
            },
            'pitta': {
                'match': ['acidity', 'anger', 'heat'],
                'herbs': [
                    {'name': 'amla', 'dosage': '1 tsp powder', 'timing': 'morning'},
                    {'name': 'neem', 'dosage': '250 mg', 'timing': 'after lunch'},
                ],
                'diet_eat': ['cooling foods'],
                'diet_avoid': ['spicy fried foods', 'excess caffeine'],
                'yoga': ['cooling pranayama'],
            },
            'kapha': {
                'match': ['lethargy', 'weight gain'],
                'herbs': [
                    {'name': 'trikatu', 'dosage': '250 mg', 'timing': 'before meals'},
                ],
                'diet_eat': ['light foods'],
                'diet_avoid': ['heavy sweet foods', 'cold dairy'],
                'yoga': ['active yoga'],
            },
        }

        selected = rules.get(dosha_key, rules['vata'])
        if any(any(marker in symptom for marker in selected['match']) for symptom in symptoms_l):
            herbs = selected['herbs']
            diet_eat = selected['diet_eat']
            diet_avoid = selected['diet_avoid']
            yoga = selected['yoga']
        else:
            herbs = selected['herbs']
            diet_eat = selected['diet_eat'] + ['seasonal vegetables']
            diet_avoid = selected['diet_avoid']
            yoga = selected['yoga']

        recent_symptoms = []
        for item in history[:3]:
            values = item.get('symptoms', [])
            if isinstance(values, list):
                recent_symptoms.extend([str(v).lower() for v in values])

        recurrence_note = 'No recent recurrence pattern detected.'
        if recent_symptoms:
            overlap = sorted(set(symptoms_l).intersection(set(recent_symptoms)))
            if overlap:
                recurrence_note = f'Recent recurrence observed for: {", ".join(overlap[:3])}.'

        return {
            'herbs': herbs,
            'diet': {'eat': diet_eat, 'avoid': diet_avoid},
            'yoga': yoga,
            'dinacharya': [
                {'time': '06:00', 'activity': 'Warm water and breathwork'},
                {'time': '12:30', 'activity': 'Main meal with seasonal foods'},
                {'time': '22:00', 'activity': 'Sleep hygiene routine'},
            ],
            'prevention_30day': f'Follow a {dosha} balancing routine in {season}, monitor symptoms: {", ".join(symptoms[:4])}. {recurrence_note}',
        }

    def generate_prevention_plan(self, location: str, risk_score: int, dosha: str, season: str) -> str:
        return (
            f'30-day plan for {location}: keep a {dosha}-balancing routine in {season}, '\
            f'monitor weekly risk score ({risk_score}/100), maintain early sleep, daily pranayama, '\
            'and fresh seasonal AYUSH diet.'
        )
