class HealthService {
	Future<List<Map<String, dynamic>>> fetchMockReadings() async {
		return [
			{'hrv_ms': 42.0, 'timestamp': DateTime.now().toIso8601String()},
		];
	}
}
