import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import 'repository_utils.dart';

class RecommendationRepository {
  RecommendationRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<Map<String, dynamic>> generate({required List<String> symptoms, String? freeText, bool variation = false}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post(
        '/recommendations/generate',
        <String, dynamic>{
          'symptoms': symptoms,
          'free_text': freeText,
          'variation': variation,
        },
      ),
    );
    final Map<String, dynamic> data = extractDataMap(response);
    await HiveService.saveSession(data);
    await HiveService.clearOldSessions();
    return data;
  }

  Future<List<Map<String, dynamic>>> history({int page = 1, int limit = 10}) async {
    try {
      final dynamic response = await runWithRetry<dynamic>(
        () => _api.get('/recommendations/history', queryParams: <String, dynamic>{'page': page, 'limit': limit}),
      );
      return extractDataList(response);
    } catch (_) {
      return HiveService.getSessions();
    }
  }

  Future<Map<String, dynamic>> preventionPlan({required String location, required int riskScore, required String dosha}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post(
        '/recommendations/prevention-plan',
        <String, dynamic>{'location': location, 'risk_score': riskScore, 'dosha': dosha},
      ),
    );
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> arogyaReport() async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post('/recommendations/arogya-report', <String, dynamic>{}),
    );
    return extractDataMap(response);
  }
}
