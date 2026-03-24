class RecommendationModel {
	final String sessionId;
	final String userId;
	final List<String> symptoms;
	final String? freeText;
	final String season;
	final List<Map<String, dynamic>> herbs;
	final Map<String, dynamic> diet;
	final List<Map<String, dynamic>> yoga;
	final List<Map<String, dynamic>> dinacharya;
	final String prevention30;
	final DateTime createdAt;

	RecommendationModel({
		required this.sessionId,
		required this.userId,
		required this.symptoms,
		required this.freeText,
		required this.season,
		required this.herbs,
		required this.diet,
		required this.yoga,
		required this.dinacharya,
		required this.prevention30,
		required this.createdAt,
	});

	factory RecommendationModel.fromJson(Map<String, dynamic> json) {
		final response = Map<String, dynamic>.from(json['response_json'] ?? {});
		return RecommendationModel(
			sessionId: json['id']?.toString() ?? json['session_id']?.toString() ?? '',
			userId: json['user_id']?.toString() ?? '',
			symptoms: ((json['symptoms'] is List)
							? List<dynamic>.from(json['symptoms'])
							: List<dynamic>.from((json['symptoms']?['items'] ?? [])))
					.map((e) => e.toString())
					.toList(),
			freeText: json['free_text']?.toString(),
			season: json['season']?.toString() ?? '',
			herbs: List<Map<String, dynamic>>.from((response['herbs'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))),
			diet: Map<String, dynamic>.from(response['diet'] ?? {}),
			yoga: List<Map<String, dynamic>>.from((response['yoga'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))),
			dinacharya: List<Map<String, dynamic>>.from((response['dinacharya'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))),
			prevention30: (response['prevention_30day'] ?? json['prevention_plan'] ?? '').toString(),
			createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ?? DateTime.now(),
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'id': sessionId,
			'user_id': userId,
			'symptoms': symptoms,
			'free_text': freeText,
			'season': season,
			'response_json': {
				'herbs': herbs,
				'diet': diet,
				'yoga': yoga,
				'dinacharya': dinacharya,
				'prevention_30day': prevention30,
			},
			'created_at': createdAt.toIso8601String(),
		};
	}
}
