from typing import Any
import json

from app.config import settings
from app.services.claude_service import ClaudeService
from app.services.hf_service import HFService


class RecommendationService:
    def __init__(self):
        self.hf = HFService()
        self.claude = ClaudeService()
        self.gemini_api_key = settings.GOOGLE_API_KEY

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
        language_map = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi', 'te': 'Telugu', 'ja': 'Japanese'}
        language_name = language_map.get((language or 'en').lower(), 'English')
        symptoms_text = ', '.join([str(item).strip() for item in symptoms if str(item).strip()])

        try:
            hf_result = self.hf.classify_symptoms(symptoms_text)
            mapped_dosha = str(hf_result.get('dosha', dosha)).lower()
            if mapped_dosha not in {'vata', 'pitta', 'kapha'}:
                mapped_dosha = str(dosha).lower() if str(dosha).lower() in {'vata', 'pitta', 'kapha'} else 'vata'
        except Exception:
            mapped_dosha = str(dosha).lower() if str(dosha).lower() in {'vata', 'pitta', 'kapha'} else 'vata'

        rule_based = self._rule_based_fallback(mapped_dosha, season, symptoms, history)
        safe_rule = self._normalize_output(rule_based)

        if self.claude.is_configured():
            try:
                claude_result = await self.claude.generate_recommendation_json(
                    dosha=mapped_dosha,
                    vata=vata,
                    pitta=pitta,
                    kapha=kapha,
                    season=season,
                    symptoms=symptoms,
                    history=history,
                    free_text=free_text,
                    language_name=language_name,
                    fallback_json=safe_rule,
                )
                merged = self._merge_recommendations(safe_rule, claude_result)
                return self._normalize_output(merged)
            except Exception:
                pass

        if not self.gemini_api_key:
            return safe_rule

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            history_text = '\n'.join(
                [f"- {item.get('date', 'NA')}: {item.get('symptoms', [])}" for item in history[:3]]
            ) or 'None'

            prompt = (
                'You are an expert Ayurvedic clinician assistant. Make recommendations personalized and context-aware. '
                'Explain reasoning briefly inside JSON field content. Do not repeat same response patterns across similar requests. '
                'Use Ayurvedic terminology where suitable. '
                'Return ONLY valid JSON with keys herbs, diet, yoga, dinacharya, prevention_plan. Do not return markdown. '
                f'Respond strictly in {language_name}. Do not translate JSON keys. '
                f'Language={language}. Profile dosha={mapped_dosha}. Season={season}. Symptoms={symptoms}. Notes={free_text or "None"}. '
                f'History:\n{history_text}. '
                f'Base recommendation JSON:\n{json.dumps(safe_rule, ensure_ascii=False)}'
            )

            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.35,
                    'response_mime_type': 'application/json',
                },
            )

            raw_text = (getattr(response, 'text', '') or '').strip()
            if raw_text.startswith('```json'):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith('```'):
                raw_text = raw_text[3:-3].strip()

            enhanced = json.loads(raw_text) if raw_text else {}
            merged = self._merge_recommendations(safe_rule, enhanced)
            return self._normalize_output(merged)
        except Exception:
            return safe_rule

    async def generate_xai_explanation(
        self,
        district: str,
        risk_level: str,
        risk_score: float,
        top_condition: str,
        trend: str,
        weather_summary: str,
        social_summary: str,
        language: str = 'en',
    ) -> list[str]:
        language_map = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi', 'te': 'Telugu', 'ja': 'Japanese'}
        language_name = language_map.get((language or 'en').lower(), 'English')
        if not self.gemini_api_key:
            return [
                f'Risk in {district} is {risk_level} ({risk_score}/100) with {top_condition} trend={trend}.',
                f'Weather context: {weather_summary}.',
                f'Social-signal context: {social_summary}.',
                'Combined epidemiological and environmental indicators support this classification.',
            ]

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                'Return ONLY valid JSON array with 4 concise reasons. '
                f'Respond strictly in {language_name}. Do not translate JSON structure. '
                f'District={district}, risk_level={risk_level}, risk_score={risk_score}, top_condition={top_condition}, trend={trend}, '
                f'weather={weather_summary}, social={social_summary}.'
            )
            response = model.generate_content(
                prompt,
                generation_config={'temperature': 0.1, 'response_mime_type': 'application/json'},
            )
            raw_text = (getattr(response, 'text', '') or '').strip()
            if raw_text.startswith('```json'):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith('```'):
                raw_text = raw_text[3:-3].strip()
            parsed = json.loads(raw_text) if raw_text else []
            return [str(item) for item in parsed][:5]
        except Exception:
            return [
                f'Risk in {district} is {risk_level} ({risk_score}/100) with {top_condition} trend={trend}.',
                f'Weather context: {weather_summary}.',
                f'Social-signal context: {social_summary}.',
                'Combined epidemiological and environmental indicators support this classification.',
            ]

    async def generate_bulletin_text(
        self,
        district_name: str,
        risk_level: str,
        top_conditions: list[str],
        forecast_summary: str,
        weather_summary: str,
        social_summary: str,
        language: str = 'en',
    ) -> str:
        language_map = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi', 'te': 'Telugu', 'ja': 'Japanese'}
        language_name = language_map.get((language or 'en').lower(), 'English')
        if not self.gemini_api_key:
            return (
                f'{district_name} shows {risk_level} health pressure led by {", ".join(top_conditions)}. '
                f'Forecast: {forecast_summary}. Weather: {weather_summary}. Social signals: {social_summary}.'
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                'Return ONLY valid JSON object {"bulletin_text":"..."}. '
                f'Respond strictly in {language_name}. Do not translate JSON keys. '
                f'District={district_name}, risk={risk_level}, conditions={top_conditions}, '
                f'forecast={forecast_summary}, weather={weather_summary}, social={social_summary}.'
            )
            response = model.generate_content(
                prompt,
                generation_config={'temperature': 0.2, 'response_mime_type': 'application/json'},
            )
            raw_text = (getattr(response, 'text', '') or '').strip()
            if raw_text.startswith('```json'):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith('```'):
                raw_text = raw_text[3:-3].strip()
            parsed = json.loads(raw_text) if raw_text else {}
            bulletin_text = str(parsed.get('bulletin_text', '')).strip()
            if bulletin_text:
                return bulletin_text
        except Exception:
            pass

        return (
            f'{district_name} shows {risk_level} health pressure led by {", ".join(top_conditions)}. '
            f'Forecast: {forecast_summary}. Weather: {weather_summary}. Social signals: {social_summary}.'
        )

    async def generate_vaidya_suggestion(self, symptoms: list[str], dosha: str, history: list[dict], language: str = 'en') -> dict[str, Any]:
        language_map = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi', 'te': 'Telugu', 'ja': 'Japanese'}
        language_name = language_map.get((language or 'en').lower(), 'English')
        if not self.gemini_api_key:
            return self._default_vaidya_suggestion(dosha)

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                'Return ONLY valid JSON object with keys formulations (array), rationale (string), cautions (array). '
                f'Respond strictly in {language_name}. Do not translate JSON keys. '
                f'Dosha={dosha}, symptoms={symptoms}, history={history[:3]}.'
            )
            response = model.generate_content(
                prompt,
                generation_config={'temperature': 0.25, 'response_mime_type': 'application/json'},
            )
            raw_text = (getattr(response, 'text', '') or '').strip()
            if raw_text.startswith('```json'):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith('```'):
                raw_text = raw_text[3:-3].strip()
            parsed = json.loads(raw_text) if raw_text else {}
            if isinstance(parsed, dict) and parsed.get('formulations'):
                return {
                    'formulations': [str(item) for item in parsed.get('formulations', [])],
                    'rationale': str(parsed.get('rationale', '')), 
                    'cautions': [str(item) for item in parsed.get('cautions', [])],
                }
        except Exception:
            pass

        return self._default_vaidya_suggestion(dosha)

    def _default_vaidya_suggestion(self, dosha: str) -> dict[str, Any]:
        lowered = dosha.lower().strip()
        if lowered == 'pitta':
            return {
                'formulations': ['Guduchi Satva', 'Amalaki Rasayana'],
                'rationale': 'Cooling formulations to pacify pitta and reduce inflammatory tendency.',
                'cautions': ['Use supervised mineral preparations only with licensed practitioner'],
            }
        if lowered == 'kapha':
            return {
                'formulations': ['Trikatu Churna', 'Kanchanar Guggulu'],
                'rationale': 'Supports kapha reduction and metabolic activation.',
                'cautions': ['Use caution in active gastritis'],
            }
        return {
            'formulations': ['Ashwagandha Churna', 'Triphala'],
            'rationale': 'Supports vata balance, stress adaptation, and bowel regularity.',
            'cautions': ['Adjust dose for pregnancy and chronic disease'],
        }

    def _rule_based_fallback(self, dosha: str, season: str, symptoms: list[str], history: list[dict]) -> dict[str, Any]:
        dosha_key = dosha.lower()
        symptoms_l = [s.lower().strip() for s in symptoms]

        rules = {
            'vata': {
                'match': ['anxiety', 'dryness', 'constipation'],
                'herbs': [
                    {'name': 'ashwagandha', 'dosage': '500 mg', 'timing': 'night'},
                ],
                'diet_eat': ['warm foods'],
                'diet_avoid': ['cold raw foods', 'irregular meals'],
                'yoga': ['slow yoga'],
            },
            'pitta': {
                'match': ['acidity', 'anger', 'heat'],
                'herbs': [
                    {'name': 'amla', 'dosage': '1 tsp powder', 'timing': 'morning'},
                ],
                'diet_eat': ['cooling foods'],
                'diet_avoid': ['spicy fried foods', 'excess caffeine'],
                'yoga': ['cool breathing'],
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
            'prevention_plan': f'Follow a {dosha} balancing routine in {season}, monitor symptoms: {", ".join(symptoms[:4])}. {recurrence_note}',
        }

    def _merge_recommendations(self, base: dict[str, Any], enhanced: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(enhanced, dict):
            return base

        merged = dict(base)
        for key in ['herbs', 'diet', 'yoga', 'dinacharya', 'prevention_plan', 'prevention_30day']:
            if key in enhanced and enhanced[key]:
                merged[key] = enhanced[key]
        return merged

    def _normalize_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        safe = payload if isinstance(payload, dict) else {}

        herbs = safe.get('herbs', [])
        if not isinstance(herbs, list):
            herbs = []
        normalized_herbs: list[dict[str, str]] = []
        for item in herbs[:8]:
            if isinstance(item, dict):
                normalized_herbs.append(
                    {
                        'name': str(item.get('name', '')).strip(),
                        'dosage': str(item.get('dosage', '')).strip(),
                        'timing': str(item.get('timing', '')).strip(),
                    }
                )
            else:
                normalized_herbs.append({'name': str(item), 'dosage': '', 'timing': ''})

        diet = safe.get('diet', {})
        if not isinstance(diet, dict):
            diet = {}
        eat = diet.get('eat', [])
        avoid = diet.get('avoid', [])
        if not isinstance(eat, list):
            eat = [str(eat)]
        if not isinstance(avoid, list):
            avoid = [str(avoid)]

        yoga = safe.get('yoga', [])
        if not isinstance(yoga, list):
            yoga = [str(yoga)]

        dinacharya = safe.get('dinacharya', [])
        if not isinstance(dinacharya, list):
            dinacharya = []

        prevention = str(safe.get('prevention_plan', '') or safe.get('prevention_30day', '')).strip()
        if not prevention:
            prevention = 'Follow dosha-balanced routine, regular sleep, hydration, and symptom monitoring for 30 days.'

        return {
            'herbs': normalized_herbs,
            'diet': {'eat': [str(x) for x in eat], 'avoid': [str(x) for x in avoid]},
            'yoga': [str(x) for x in yoga],
            'dinacharya': dinacharya,
            'prevention_plan': prevention,
            'prevention_30day': prevention,
        }

    async def generate_prevention_plan(self, location: str, risk_score: int, dosha: str, season: str, language: str = 'en') -> str:
        fallback = (
            f'30-day plan for {location}: keep a {dosha}-balancing routine in {season}, '
            f'monitor weekly risk score ({risk_score}/100), maintain early sleep, daily pranayama, '
            'and fresh seasonal AYUSH diet.'
        )

        language_map = {'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi', 'te': 'Telugu', 'ja': 'Japanese'}
        language_name = language_map.get((language or 'en').lower(), 'English')

        if self.claude.is_configured():
            try:
                claude_json = await self.claude.generate_recommendation_json(
                    dosha=str(dosha).lower(),
                    vata=33,
                    pitta=33,
                    kapha=34,
                    season=season,
                    symptoms=[f'location:{location}', f'risk_score:{risk_score}'],
                    history=[],
                    free_text=(
                        f'Generate a strict 30-day prevention plan for {location} '
                        f'with risk score {risk_score} and dosha {dosha}. '
                        f'Return actionable weekly structure in {language_name}.'
                    ),
                    language_name=language_name,
                    fallback_json={
                        'herbs': [],
                        'diet': {'eat': [], 'avoid': []},
                        'yoga': [],
                        'dinacharya': [],
                        'prevention_plan': fallback,
                    },
                )
                normalized = self._normalize_output(claude_json)
                prevention = str(normalized.get('prevention_plan', '')).strip()
                if prevention:
                    return prevention
            except Exception:
                pass

        return fallback
