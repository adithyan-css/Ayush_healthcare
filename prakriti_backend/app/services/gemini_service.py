import json
from typing import Any
import httpx
from app.config import settings


class GeminiService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'

    def _extract_text(self, response_json: dict) -> str:
        return response_json['candidates'][0]['content']['parts'][0]['text']

    async def _generate_json(self, prompt: str, max_tokens: int, temperature: float) -> Any:
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
                'responseMimeType': 'application/json',
            },
        }
        async with httpx.AsyncClient(timeout=9.5) as client:
            response = await client.post(f'{self.base_url}?key={self.api_key}', json=payload)
            response.raise_for_status()
            text = self._extract_text(response.json()).strip()
            if text.startswith('```json'):
                text = text[7:-3].strip()
            elif text.startswith('```'):
                text = text[3:-3].strip()
            return json.loads(text)

    async def generate_recommendation(
        self,
        dosha: str,
        vata_pct: float,
        pitta_pct: float,
        kapha_pct: float,
        season: str,
        symptoms: list[str],
        history: list[dict],
        free_text: str | None,
        lang: str = 'en',
    ) -> dict:
        if not self.api_key:
            if dosha.lower() == 'pitta':
                return {
                    'herbs': [
                        {'name': 'Guduchi', 'benefit': 'Supports cooling and immunity', 'dosage': '500 mg twice daily', 'timing': 'after meals'},
                        {'name': 'Amalaki', 'benefit': 'Helps reduce heat and acidity', 'dosage': '1 tsp powder daily', 'timing': 'morning'},
                        {'name': 'Brahmi', 'benefit': 'Calms mind and improves focus', 'dosage': '250 mg once daily', 'timing': 'evening'},
                    ],
                    'diet': {
                        'eat': [
                            {'food': 'Cucumber and coriander', 'reason': 'Cooling support for pitta'},
                            {'food': 'Moong dal khichdi', 'reason': 'Light and easy to digest'},
                        ],
                        'avoid': [
                            {'food': 'Very spicy fried food', 'reason': 'May aggravate pitta heat'},
                            {'food': 'Excess coffee', 'reason': 'Can increase irritability and acidity'},
                        ],
                    },
                    'yoga': [
                        {'name': 'Sheetali Pranayama', 'duration': '8 min', 'benefit': 'Cooling breath practice'},
                        {'name': 'Ardha Matsyendrasana', 'duration': '6 min', 'benefit': 'Supports digestion'},
                    ],
                    'dinacharya': [
                        {'time': '06:00', 'activity': 'Wake up and hydrate with room-temperature water'},
                        {'time': '07:00', 'activity': '20-minute light yoga and breathing'},
                        {'time': '12:30', 'activity': 'Main lunch with cooling foods'},
                        {'time': '18:30', 'activity': 'Early light dinner'},
                        {'time': '22:00', 'activity': 'Sleep routine and digital detox'},
                    ],
                    'prevention_30day': 'For 30 days, prioritize cooling meals, avoid late-night spicy food, practice Sheetali and Anulom Vilom daily, and maintain sleep before 10:30 PM.',
                }
            if dosha.lower() == 'kapha':
                return {
                    'herbs': [
                        {'name': 'Trikatu', 'benefit': 'Supports metabolism and kapha balance', 'dosage': '250 mg twice daily', 'timing': 'before meals'},
                        {'name': 'Guggulu', 'benefit': 'Helps with sluggishness and heaviness', 'dosage': '500 mg once daily', 'timing': 'morning'},
                        {'name': 'Tulsi', 'benefit': 'Supports respiratory resilience', 'dosage': '2 leaves or tea daily', 'timing': 'morning'},
                    ],
                    'diet': {
                        'eat': [
                            {'food': 'Warm spiced soups', 'reason': 'Light and warming for kapha'},
                            {'food': 'Millets and steamed vegetables', 'reason': 'Supports weight and digestion'},
                        ],
                        'avoid': [
                            {'food': 'Cold dairy desserts', 'reason': 'May increase heaviness'},
                            {'food': 'Deep-fried snacks', 'reason': 'Can worsen sluggishness'},
                        ],
                    },
                    'yoga': [
                        {'name': 'Surya Namaskar', 'duration': '15 min', 'benefit': 'Stimulates circulation'},
                        {'name': 'Kapalabhati', 'duration': '5 min', 'benefit': 'Activates metabolism'},
                    ],
                    'dinacharya': [
                        {'time': '05:45', 'activity': 'Wake early and brisk walk'},
                        {'time': '07:00', 'activity': 'Active yoga practice'},
                        {'time': '13:00', 'activity': 'Balanced warm lunch'},
                        {'time': '17:30', 'activity': 'Herbal tea and short walk'},
                        {'time': '21:45', 'activity': 'Wind-down and sleep'},
                    ],
                    'prevention_30day': 'For 30 days, maintain daily movement, warm light meals, avoid day sleep, and include Surya Namaskar with Kapalabhati at least five days per week.',
                }
            return {
                'herbs': [
                    {'name': 'Ashwagandha', 'benefit': 'Supports stress adaptation and sleep', 'dosage': '500 mg at bedtime', 'timing': 'night'},
                    {'name': 'Bala', 'benefit': 'Supports strength and nervous system', 'dosage': '250 mg once daily', 'timing': 'morning'},
                    {'name': 'Triphala', 'benefit': 'Supports digestion and regularity', 'dosage': '1 tsp warm water', 'timing': 'night'},
                ],
                'diet': {
                    'eat': [
                        {'food': 'Warm cooked grains and ghee', 'reason': 'Grounding for vata'},
                        {'food': 'Stewed fruits', 'reason': 'Easy digestion and hydration'},
                    ],
                    'avoid': [
                        {'food': 'Cold raw salads at night', 'reason': 'May aggravate dryness and gas'},
                        {'food': 'Irregular meal timings', 'reason': 'Increases vata imbalance'},
                    ],
                },
                'yoga': [
                    {'name': 'Vrikshasana', 'duration': '6 min', 'benefit': 'Improves grounding and balance'},
                    {'name': 'Anulom Vilom', 'duration': '10 min', 'benefit': 'Calms nervous system'},
                ],
                'dinacharya': [
                    {'time': '06:00', 'activity': 'Wake and drink warm water'},
                    {'time': '07:00', 'activity': 'Gentle yoga and pranayama'},
                    {'time': '12:30', 'activity': 'Warm freshly cooked lunch'},
                    {'time': '19:00', 'activity': 'Light warm dinner'},
                    {'time': '22:00', 'activity': 'Sleep with fixed routine'},
                ],
                'prevention_30day': 'For 30 days, keep strict routine, eat warm freshly cooked foods, oil massage 3 times weekly, and practice Anulom Vilom daily.',
            }

        history_text = '\n'.join(
            [f"- {item.get('date', 'NA')}: {', '.join(item.get('symptoms', []))}" for item in history[:3]]
        ) or 'None'
        prompt = f"""You are an expert AYUSH health advisor.
User Prakriti: {dosha} ({vata_pct}% Vata, {pitta_pct}% Pitta, {kapha_pct}% Kapha)
Current Season: {season}
Past consultations (last 3):
{history_text}
Current symptoms: {', '.join(symptoms)}
Additional notes: {free_text or 'None'}
Return ONLY valid JSON with this exact schema:
{{"herbs":[{{"name":"","benefit":"","dosage":"","timing":""}}],"diet":{{"eat":[{{"food":"","reason":""}}],"avoid":[{{"food":"","reason":""}}]}},"yoga":[{{"name":"","duration":"","benefit":""}}],"dinacharya":[{{"time":"","activity":""}}],"prevention_30day":""}}
Respond in language: {lang}"""
        try:
            result = await self._generate_json(prompt, max_tokens=1800, temperature=0.2)
            return dict(result)
        except Exception:
            if dosha.lower() == 'pitta':
                return {
                    'herbs': [
                        {'name': 'Guduchi', 'benefit': 'Supports cooling and immunity', 'dosage': '500 mg twice daily', 'timing': 'after meals'},
                        {'name': 'Amalaki', 'benefit': 'Helps reduce heat and acidity', 'dosage': '1 tsp powder daily', 'timing': 'morning'},
                        {'name': 'Brahmi', 'benefit': 'Calms mind and improves focus', 'dosage': '250 mg once daily', 'timing': 'evening'},
                    ],
                    'diet': {
                        'eat': [
                            {'food': 'Cucumber and coriander', 'reason': 'Cooling support for pitta'},
                            {'food': 'Moong dal khichdi', 'reason': 'Light and easy to digest'},
                        ],
                        'avoid': [
                            {'food': 'Very spicy fried food', 'reason': 'May aggravate pitta heat'},
                            {'food': 'Excess coffee', 'reason': 'Can increase irritability and acidity'},
                        ],
                    },
                    'yoga': [
                        {'name': 'Sheetali Pranayama', 'duration': '8 min', 'benefit': 'Cooling breath practice'},
                        {'name': 'Ardha Matsyendrasana', 'duration': '6 min', 'benefit': 'Supports digestion'},
                    ],
                    'dinacharya': [
                        {'time': '06:00', 'activity': 'Wake up and hydrate with room-temperature water'},
                        {'time': '07:00', 'activity': '20-minute light yoga and breathing'},
                        {'time': '12:30', 'activity': 'Main lunch with cooling foods'},
                        {'time': '18:30', 'activity': 'Early light dinner'},
                        {'time': '22:00', 'activity': 'Sleep routine and digital detox'},
                    ],
                    'prevention_30day': 'For 30 days, prioritize cooling meals, avoid late-night spicy food, practice Sheetali and Anulom Vilom daily, and maintain sleep before 10:30 PM.',
                }
            if dosha.lower() == 'kapha':
                return {
                    'herbs': [
                        {'name': 'Trikatu', 'benefit': 'Supports metabolism and kapha balance', 'dosage': '250 mg twice daily', 'timing': 'before meals'},
                        {'name': 'Guggulu', 'benefit': 'Helps with sluggishness and heaviness', 'dosage': '500 mg once daily', 'timing': 'morning'},
                        {'name': 'Tulsi', 'benefit': 'Supports respiratory resilience', 'dosage': '2 leaves or tea daily', 'timing': 'morning'},
                    ],
                    'diet': {
                        'eat': [
                            {'food': 'Warm spiced soups', 'reason': 'Light and warming for kapha'},
                            {'food': 'Millets and steamed vegetables', 'reason': 'Supports weight and digestion'},
                        ],
                        'avoid': [
                            {'food': 'Cold dairy desserts', 'reason': 'May increase heaviness'},
                            {'food': 'Deep-fried snacks', 'reason': 'Can worsen sluggishness'},
                        ],
                    },
                    'yoga': [
                        {'name': 'Surya Namaskar', 'duration': '15 min', 'benefit': 'Stimulates circulation'},
                        {'name': 'Kapalabhati', 'duration': '5 min', 'benefit': 'Activates metabolism'},
                    ],
                    'dinacharya': [
                        {'time': '05:45', 'activity': 'Wake early and brisk walk'},
                        {'time': '07:00', 'activity': 'Active yoga practice'},
                        {'time': '13:00', 'activity': 'Balanced warm lunch'},
                        {'time': '17:30', 'activity': 'Herbal tea and short walk'},
                        {'time': '21:45', 'activity': 'Wind-down and sleep'},
                    ],
                    'prevention_30day': 'For 30 days, maintain daily movement, warm light meals, avoid day sleep, and include Surya Namaskar with Kapalabhati at least five days per week.',
                }
            return {
                'herbs': [
                    {'name': 'Ashwagandha', 'benefit': 'Supports stress adaptation and sleep', 'dosage': '500 mg at bedtime', 'timing': 'night'},
                    {'name': 'Bala', 'benefit': 'Supports strength and nervous system', 'dosage': '250 mg once daily', 'timing': 'morning'},
                    {'name': 'Triphala', 'benefit': 'Supports digestion and regularity', 'dosage': '1 tsp warm water', 'timing': 'night'},
                ],
                'diet': {
                    'eat': [
                        {'food': 'Warm cooked grains and ghee', 'reason': 'Grounding for vata'},
                        {'food': 'Stewed fruits', 'reason': 'Easy digestion and hydration'},
                    ],
                    'avoid': [
                        {'food': 'Cold raw salads at night', 'reason': 'May aggravate dryness and gas'},
                        {'food': 'Irregular meal timings', 'reason': 'Increases vata imbalance'},
                    ],
                },
                'yoga': [
                    {'name': 'Vrikshasana', 'duration': '6 min', 'benefit': 'Improves grounding and balance'},
                    {'name': 'Anulom Vilom', 'duration': '10 min', 'benefit': 'Calms nervous system'},
                ],
                'dinacharya': [
                    {'time': '06:00', 'activity': 'Wake and drink warm water'},
                    {'time': '07:00', 'activity': 'Gentle yoga and pranayama'},
                    {'time': '12:30', 'activity': 'Warm freshly cooked lunch'},
                    {'time': '19:00', 'activity': 'Light warm dinner'},
                    {'time': '22:00', 'activity': 'Sleep with fixed routine'},
                ],
                'prevention_30day': 'For 30 days, keep strict routine, eat warm freshly cooked foods, oil massage 3 times weekly, and practice Anulom Vilom daily.',
            }

    async def generate_xai_explanation(
        self,
        district: str,
        risk_level: str,
        risk_score: float,
        top_condition: str,
        trend: str,
        weather_summary: str,
        social_summary: str,
    ) -> list[str]:
        if not self.api_key:
            return [
                f'Risk score {risk_score}/100 in {district} is tied to {top_condition} trend: {trend}.',
                f'Weather signal: {weather_summary}.',
                f'Social signal intensity: {social_summary}.',
                f'Combined climate and symptom pressure supports {risk_level} classification.',
            ]

        prompt = f"""You are a public health AI.
District: {district}
Risk level: {risk_level}
Risk score: {risk_score}
Top condition: {top_condition}
Trend: {trend}
Weather summary: {weather_summary}
Social summary: {social_summary}
Return ONLY valid JSON array of 4 to 5 specific reasons with numbers."""
        try:
            result = await self._generate_json(prompt, max_tokens=700, temperature=0.1)
            return [str(x) for x in result][:5]
        except Exception:
            return [
                f'{district} risk remains {risk_level} at {risk_score}/100 due to sustained {top_condition} burden.',
                f'Weather trend suggests persistence: {weather_summary}.',
                f'Social signal volume indicates active concern: {social_summary}.',
                f'Current trajectory classified as {trend}.',
            ]

    async def generate_vaidya_suggestion(self, symptoms: list[str], dosha: str, history: list[dict]) -> dict:
        if not self.api_key:
            if dosha.lower() == 'kapha':
                return {
                    'formulations': ['Trikatu Churna', 'Kanchanar Guggulu', 'Tulsi Ginger Decoction'],
                    'rationale': 'These classical formulations support kapha reduction, metabolism and respiratory resilience.',
                    'cautions': ['Avoid in active gastritis without supervision', 'Monitor if on anticoagulants'],
                }
            if dosha.lower() == 'pitta':
                return {
                    'formulations': ['Guduchi Satva', 'Amalaki Rasayana', 'Praval Pishti (supervised)'],
                    'rationale': 'Cooling and pitta-pacifying support with digestive and inflammatory balance.',
                    'cautions': ['Use mineral preparations only under licensed supervision'],
                }
            return {
                'formulations': ['Ashwagandha Churna', 'Dashamoola Kwatha', 'Triphala at bedtime'],
                'rationale': 'Supports vata balancing, stress adaptation and bowel regulation.',
                'cautions': ['Adjust dose in pregnancy and chronic conditions with physician advice'],
            }

        prompt = f"""You are an AYUSH clinical support assistant.
Dosha: {dosha}
Symptoms: {symptoms}
History summary: {history[:3]}
Return ONLY JSON object: {{"formulations": [""], "rationale": "", "cautions": [""]}}"""
        try:
            result = await self._generate_json(prompt, max_tokens=900, temperature=0.2)
            return dict(result)
        except Exception:
            if dosha.lower() == 'kapha':
                return {
                    'formulations': ['Trikatu Churna', 'Kanchanar Guggulu', 'Tulsi Ginger Decoction'],
                    'rationale': 'These classical formulations support kapha reduction, metabolism and respiratory resilience.',
                    'cautions': ['Avoid in active gastritis without supervision', 'Monitor if on anticoagulants'],
                }
            if dosha.lower() == 'pitta':
                return {
                    'formulations': ['Guduchi Satva', 'Amalaki Rasayana', 'Praval Pishti (supervised)'],
                    'rationale': 'Cooling and pitta-pacifying support with digestive and inflammatory balance.',
                    'cautions': ['Use mineral preparations only under licensed supervision'],
                }
            return {
                'formulations': ['Ashwagandha Churna', 'Dashamoola Kwatha', 'Triphala at bedtime'],
                'rationale': 'Supports vata balancing, stress adaptation and bowel regulation.',
                'cautions': ['Adjust dose in pregnancy and chronic conditions with physician advice'],
            }

    async def generate_bulletin_text(
        self,
        district_name: str,
        risk_level: str,
        top_conditions: list[str],
        forecast_summary: str,
        weather_summary: str,
        social_summary: str,
    ) -> str:
        if not self.api_key:
            return (
                f'{district_name} currently shows {risk_level} public-health pressure, led by {", ".join(top_conditions)}. '
                f'Forecast indicates {forecast_summary}. Weather context: {weather_summary}. Social signals: {social_summary}. '
                'Immediate preventive AYUSH messaging is advised with hydration, seasonal diet and community surveillance.'
            )

        prompt = f"""Draft a professional public health bulletin paragraph.
District: {district_name}
Risk level: {risk_level}
Top conditions: {top_conditions}
Forecast summary: {forecast_summary}
Weather summary: {weather_summary}
Social summary: {social_summary}
Return ONLY JSON: {{"bulletin_text": "..."}}"""
        try:
            result = await self._generate_json(prompt, max_tokens=500, temperature=0.2)
            return str(result.get('bulletin_text', '')).strip()
        except Exception:
            return (
                f'{district_name} currently shows {risk_level} public-health pressure, led by {", ".join(top_conditions)}. '
                f'Forecast indicates {forecast_summary}. Weather context: {weather_summary}. Social signals: {social_summary}. '
                'Immediate preventive AYUSH messaging is advised with hydration, seasonal diet and community surveillance.'
            )

    async def generate_prevention_plan(self, location: str, risk_score: int, dosha: str, age_group: str = 'adult') -> str:
        if not self.api_key:
            return (
                f'30-day prevention plan for {location}: Follow a {dosha}-balancing diet, include Tulsi-Guduchi decoction 5 days/week, '
                f'practice Surya Namaskar and Anulom Vilom daily, maintain fixed sleep, and monitor symptoms weekly for {age_group} group '
                f'under current risk score {risk_score}/100.'
            )

        prompt = f"""Create a concise 30-day AYUSH prevention plan.
Location: {location}
Risk score: {risk_score}
Dominant dosha: {dosha}
Age group: {age_group}
Return ONLY JSON: {{"plan": "..."}}"""
        try:
            result = await self._generate_json(prompt, max_tokens=700, temperature=0.2)
            return str(result.get('plan', '')).strip()
        except Exception:
            return (
                f'30-day prevention plan for {location}: Follow a {dosha}-balancing diet, include Tulsi-Guduchi decoction 5 days/week, '
                f'practice Surya Namaskar and Anulom Vilom daily, maintain fixed sleep, and monitor symptoms weekly for {age_group} group '
                f'under current risk score {risk_score}/100.'
            )
