import asyncio
import json
import re
from typing import Any

import httpx

from app.config import settings


class ClaudeService:
	def __init__(self):
		self.api_key = settings.CLAUDE_API_KEY
		self.model = settings.CLAUDE_MODEL or 'claude-3-5-sonnet-latest'
		self.url = 'https://api.anthropic.com/v1/messages'

	def is_configured(self) -> bool:
		return bool(self.api_key)

	async def generate_recommendation_json(
		self,
		*,
		dosha: str,
		vata: float,
		pitta: float,
		kapha: float,
		season: str,
		symptoms: list[str],
		history: list[dict[str, Any]],
		free_text: str | None,
		language_name: str,
		fallback_json: dict[str, Any],
	) -> dict[str, Any]:
		if not self.is_configured():
			return fallback_json

		history_lines: list[str] = []
		for item in history[:3]:
			h_date = str(item.get('date', 'NA'))
			h_symptoms = item.get('symptoms', [])
			history_lines.append(f'- {h_date}: {h_symptoms}')
		history_text = '\n'.join(history_lines) if history_lines else 'None'

		prompt = (
			'You are an Ayurvedic preventive care clinical copilot for an Indian national-scale health app.\n'
			'Return ONLY valid JSON, no markdown, no explanation outside JSON.\n\n'
			'Required output schema:\n'
			'{\n'
			'  "herbs": [{"name":"","dosage":"","timing":""}],\n'
			'  "diet": {"eat": [""], "avoid": [""]},\n'
			'  "yoga": [""],\n'
			'  "dinacharya": [{"time":"","activity":""}],\n'
			'  "prevention_plan": ""\n'
			'}\n\n'
			'Rules:\n'
			'1) Use practical AYUSH recommendations.\n'
			'2) Be history-aware and avoid repeating same plan if prior sessions overlap.\n'
			'3) Keep JSON keys exactly as required.\n'
			f'4) Respond in {language_name}, while keeping JSON keys in English.\n\n'
			f'Input context:\n'
			f'- Dosha: {dosha}\n'
			f'- Vata: {vata}\n'
			f'- Pitta: {pitta}\n'
			f'- Kapha: {kapha}\n'
			f'- Season: {season}\n'
			f'- Symptoms: {symptoms}\n'
			f'- Notes: {free_text or "None"}\n'
			f'- Last sessions:\n{history_text}\n\n'
			f'Fallback baseline JSON:\n{json.dumps(fallback_json, ensure_ascii=False)}'
		)

		payload = {
			'model': self.model,
			'max_tokens': 1200,
			'temperature': 0.2,
			'messages': [{'role': 'user', 'content': prompt}],
		}

		headers = {
			'x-api-key': self.api_key,
			'anthropic-version': '2023-06-01',
			'content-type': 'application/json',
		}

		for attempt in range(3):
			try:
				timeout = httpx.Timeout(18.0, connect=8.0)
				async with httpx.AsyncClient(timeout=timeout) as client:
					response = await client.post(self.url, headers=headers, json=payload)
					response.raise_for_status()
					body = response.json()
					content = body.get('content', [])
					text_parts = [str(item.get('text', '')) for item in content if isinstance(item, dict)]
					raw_text = '\n'.join(text_parts).strip()
					parsed = self._parse_json_payload(raw_text)
					if isinstance(parsed, dict) and parsed:
						return parsed
			except Exception:
				if attempt < 2:
					await asyncio.sleep(0.6 * (attempt + 1))
					continue

		return fallback_json

	def _parse_json_payload(self, text: str) -> dict[str, Any]:
		raw = text.strip()
		if not raw:
			return {}

		if raw.startswith('```json'):
			raw = raw[7:]
		if raw.startswith('```'):
			raw = raw[3:]
		if raw.endswith('```'):
			raw = raw[:-3]
		raw = raw.strip()

		try:
			parsed = json.loads(raw)
			return parsed if isinstance(parsed, dict) else {}
		except Exception:
			match = re.search(r'\{[\s\S]*\}', raw)
			if not match:
				return {}
			try:
				parsed = json.loads(match.group(0))
				return parsed if isinstance(parsed, dict) else {}
			except Exception:
				return {}
