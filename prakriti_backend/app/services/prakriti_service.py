class PrakritiService:
	def calculate_dominant(self, vata: float, pitta: float, kapha: float) -> str:
		scores = {'vata': vata, 'pitta': pitta, 'kapha': kapha}
		return max(scores, key=scores.get)

	def calculate_percentages(self, vata: float, pitta: float, kapha: float):
		total = vata + pitta + kapha
		if total == 0:
			return 33.3, 33.3, 33.3
		return round(vata / total * 100, 1), round(pitta / total * 100, 1), round(kapha / total * 100, 1)
