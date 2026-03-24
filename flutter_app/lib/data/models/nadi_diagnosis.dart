class NadiDiagnosis {
	final String dominantNadi;
	final double hrv7DayAvg;
	final bool anomalyDetected;
	final List<String> recommendations;

	NadiDiagnosis({
		required this.dominantNadi,
		required this.hrv7DayAvg,
		required this.anomalyDetected,
		required this.recommendations,
	});

	factory NadiDiagnosis.fromJson(Map<String, dynamic> json) {
		return NadiDiagnosis(
			dominantNadi: json['dominant_nadi']?.toString() ?? json['type']?.toString() ?? 'Unknown',
			hrv7DayAvg: (json['hrv_7day_avg'] ?? json['hrv_ms'] ?? 0).toDouble(),
			anomalyDetected: json['anomaly_detected'] == true || json['is_anomaly'] == true,
			recommendations: (json['recommendations'] as List<dynamic>? ??
							['Maintain regular sleep', 'Practice alternate nostril breathing', 'Avoid heavy dinner'])
					.map((e) => e.toString())
					.toList(),
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'dominant_nadi': dominantNadi,
			'hrv_7day_avg': hrv7DayAvg,
			'anomaly_detected': anomalyDetected,
			'recommendations': recommendations,
		};
	}
}
