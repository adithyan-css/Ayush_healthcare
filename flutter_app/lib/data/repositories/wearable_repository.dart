import '../../services/api_service.dart';
import 'repository_utils.dart';

class WearableRepository {
  WearableRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<void> syncReadings(List<Map<String, dynamic>> readings) async {
    await runWithRetry<dynamic>(() => _api.post('/wearable/hrv-sync', <String, dynamic>{'readings': readings}));
  }

  Future<Map<String, dynamic>> nadi() async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/wearable/nadi'));
    return extractDataMap(response);
  }

  Future<List<Map<String, dynamic>>> trend({int days = 30}) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/wearable/trends', queryParams: <String, dynamic>{'days': days}));
    return extractDataList(response);
  }

  Future<List<Map<String, dynamic>>> anomalies() async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/wearable/anomalies'));
    return extractDataList(response);
  }
}
