class PrakritiModel {
	final String userId;
	final double vataScore;
	final double pittaScore;
	final double kaphaScore;
	final String dominantDosha;
	final double vataPercent;
	final double pittaPercent;
	final double kaphaPercent;
	final DateTime completedAt;
	final double constitutionalRiskScore;

	PrakritiModel({
		required this.userId,
		required this.vataScore,
		required this.pittaScore,
		required this.kaphaScore,
		required this.dominantDosha,
		required this.vataPercent,
		required this.pittaPercent,
		required this.kaphaPercent,
		required this.completedAt,
		required this.constitutionalRiskScore,
	});

	factory PrakritiModel.fromJson(Map<String, dynamic> json) {
		final vata = (json['vata_score'] ?? json['vataScore'] ?? 0).toDouble();
		final pitta = (json['pitta_score'] ?? json['pittaScore'] ?? 0).toDouble();
		final kapha = (json['kapha_score'] ?? json['kaphaScore'] ?? 0).toDouble();
		final total = vata + pitta + kapha;
		return PrakritiModel(
			userId: json['user_id']?.toString() ?? json['userId']?.toString() ?? '',
			vataScore: vata,
			pittaScore: pitta,
			kaphaScore: kapha,
			dominantDosha: json['dominant_dosha']?.toString() ?? json['dominantDosha']?.toString() ?? 'vata',
			vataPercent: (json['vata_percent'] ?? json['vataPercent'] ?? (total == 0 ? 33.3 : (vata / total) * 100)).toDouble(),
			pittaPercent: (json['pitta_percent'] ?? json['pittaPercent'] ?? (total == 0 ? 33.3 : (pitta / total) * 100)).toDouble(),
			kaphaPercent: (json['kapha_percent'] ?? json['kaphaPercent'] ?? (total == 0 ? 33.4 : (kapha / total) * 100)).toDouble(),
			completedAt: DateTime.tryParse(json['completed_at']?.toString() ?? json['completedAt']?.toString() ?? '') ?? DateTime.now(),
			constitutionalRiskScore: (json['constitutional_risk_score'] ?? json['constitutionalRiskScore'] ?? json['risk_score'] ?? 0).toDouble(),
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'user_id': userId,
			'vata_score': vataScore,
			'pitta_score': pittaScore,
			'kapha_score': kaphaScore,
			'dominant_dosha': dominantDosha,
			'vata_percent': vataPercent,
			'pitta_percent': pittaPercent,
			'kapha_percent': kaphaPercent,
			'completed_at': completedAt.toIso8601String(),
			'constitutional_risk_score': constitutionalRiskScore,
		};
	}
}
