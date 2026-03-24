class PrakritiService:
	def calculate_dominant_dosha(self, vata: int, pitta: int, kapha: int):
		total = max(1, vata + pitta + kapha)
		vata_percent = round((vata / total) * 100, 1)
		pitta_percent = round((pitta / total) * 100, 1)
		kapha_percent = round((kapha / total) * 100, 1)
		scores = {'vata': vata_percent, 'pitta': pitta_percent, 'kapha': kapha_percent}
		dominant_dosha = max(scores, key=scores.get)
		constitutional_risk_score = round(100 - scores[dominant_dosha], 1)
		return {
			'dominant_dosha': dominant_dosha,
			'vata_percent': vata_percent,
			'pitta_percent': pitta_percent,
			'kapha_percent': kapha_percent,
			'constitutional_risk_score': constitutional_risk_score,
		}

	def get_dosha_tips(self, dosha: str, count: int = 3):
		tips = {
			'vata': [
				'Eat warm freshly cooked meals at regular times.',
				'Use sesame oil self-massage before bath.',
				'Sleep by 10 PM to calm nervous system.',
				'Practice Anulom Vilom for 10 minutes daily.',
				'Limit cold raw foods in the evening.',
				'Hydrate with warm water and herbal teas.',
				'Avoid over-scheduling and late-night work.',
				'Use grounding yoga postures daily.',
				'Include ghee in moderation for lubrication.',
				'Maintain consistent wake-up and meal routine.',
			],
			'pitta': [
				'Favor cooling foods like cucumber and bottle gourd.',
				'Avoid very spicy, sour, and fried food.',
				'Practice Sheetali breathing in evening.',
				'Stay hydrated throughout hot hours.',
				'Reduce excess caffeine and alcohol.',
				'Take short cooling walks at sunset.',
				'Use coriander and fennel in meals.',
				'Pause for stress regulation during work.',
				'Prefer early dinner and good sleep hygiene.',
				'Use coconut water in hot season if suitable.',
			],
			'kapha': [
				'Start day with brisk walk or light jog.',
				'Eat light warm meals with digestive spices.',
				'Avoid daytime sleeping.',
				'Reduce heavy dairy and sugary foods.',
				'Practice Surya Namaskar daily.',
				'Use ginger-tulsi tea for lightness.',
				'Choose millet and legumes over refined carbs.',
				'Keep dinner early and minimal.',
				'Maintain active routines and avoid sedentary stretches.',
				'Use steam inhalation during congestion season.',
			],
		}
		return tips.get(dosha.lower(), tips['vata'])[: max(1, count)]

	def get_seasonal_recommendation(self, dosha: str, season: str):
		dosha_key = dosha.lower()
		season_key = season.lower()
		matrix = {
			('vata', 'winter'): 'Use warm oil massage and nourishing soups to prevent dryness and stiffness.',
			('vata', 'summer'): 'Hydrate regularly and avoid fasting for long hours in hot weather.',
			('vata', 'monsoon'): 'Keep digestion strong with warm spices and avoid raw food.',
			('vata', 'autumn'): 'Follow a stable routine with grounding meals and calming pranayama.',
			('pitta', 'winter'): 'Use moderate spices and avoid overeating fried foods.',
			('pitta', 'summer'): 'Prefer cooling meals and avoid direct midday sun exposure.',
			('pitta', 'monsoon'): 'Use light, freshly cooked food and maintain gut hygiene.',
			('pitta', 'autumn'): 'Balance residual heat with bitter greens and stress management.',
			('kapha', 'winter'): 'Increase movement and use warming herbs to reduce congestion.',
			('kapha', 'summer'): 'Keep meals light and stay physically active despite heat.',
			('kapha', 'monsoon'): 'Avoid heavy oily food and include dry ginger in diet.',
			('kapha', 'autumn'): 'Use seasonal vegetables and maintain daily cardio routine.',
		}
		return matrix.get((dosha_key, season_key), 'Follow seasonal fresh diet, regular sleep, and daily movement.')
