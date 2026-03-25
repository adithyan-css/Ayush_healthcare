import '../../services/api_service.dart';
import 'repository_utils.dart';

class CommunityRepository {
  CommunityRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<List<Map<String, dynamic>>> community({int days = 7}) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/symptoms/community', queryParams: <String, dynamic>{'days': days}));
    return extractDataList(response);
  }

  Future<List<Map<String, dynamic>>> hotspots({int days = 7}) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/symptoms/community/hotspots', queryParams: <String, dynamic>{'days': days}));
    final Map<String, dynamic> data = extractDataMap(response);
    return (data['hotspots'] as List<dynamic>? ?? <dynamic>[])
        .whereType<Map>()
        .map((Map item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
  }

  Future<List<Map<String, dynamic>>> alerts({int days = 7}) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/symptoms/community/alerts', queryParams: <String, dynamic>{'days': days}));
    final Map<String, dynamic> data = extractDataMap(response);
    return (data['alerts'] as List<dynamic>? ?? <dynamic>[])
        .whereType<Map>()
        .map((Map item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
  }

  Future<void> reportSymptoms({required List<String> symptoms, double? latitude, double? longitude}) async {
    await runWithRetry<dynamic>(() => _api.post('/symptoms/community/report', <String, dynamic>{
          'symptoms': symptoms,
          'latitude': latitude,
          'longitude': longitude,
        }));
  }
}
