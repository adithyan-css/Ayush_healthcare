class DistrictRiskModel {
	final String stateId;
	final String stateName;
	final double riskScore;
	final String riskLevel;
	final String topCondition;
	final String trend;
	final Map<String, dynamic> monthlyCases;
	final List<String> ayushTips;
	final double latitude;
	final double longitude;

	DistrictRiskModel({
		required this.stateId,
		required this.stateName,
		required this.riskScore,
		required this.riskLevel,
		required this.topCondition,
		required this.trend,
		required this.monthlyCases,
		required this.ayushTips,
		required this.latitude,
		required this.longitude,
	});

	factory DistrictRiskModel.fromJson(Map<String, dynamic> json) {
		return DistrictRiskModel(
			stateId: json['state_code']?.toString() ?? json['stateId']?.toString() ?? '',
			stateName: json['state_name']?.toString() ?? json['stateName']?.toString() ?? '',
			riskScore: (json['risk_score'] ?? json['riskScore'] ?? 0).toDouble(),
			riskLevel: json['risk_level']?.toString() ?? json['riskLevel']?.toString() ?? 'low',
			topCondition: json['top_condition']?.toString() ?? json['topCondition']?.toString() ?? '',
			trend: json['trend']?.toString() ?? 'stable',
			monthlyCases: Map<String, dynamic>.from(json['monthly_cases'] ?? json['monthlyCases'] ?? {}),
			ayushTips: (json['ayush_tips'] as List<dynamic>? ??
							['Hydrate with warm water', 'Follow seasonal diet', 'Practice daily pranayama'])
					.map((e) => e.toString())
					.toList(),
			latitude: (json['latitude'] ?? 20.5937).toDouble(),
			longitude: (json['longitude'] ?? 78.9629).toDouble(),
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'state_code': stateId,
			'state_name': stateName,
			'risk_score': riskScore,
			'risk_level': riskLevel,
			'top_condition': topCondition,
			'trend': trend,
			'monthly_cases': monthlyCases,
			'ayush_tips': ayushTips,
			'latitude': latitude,
			'longitude': longitude,
		};
	}
}
