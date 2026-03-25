import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import 'repository_utils.dart';

class PrakritiRepository {
  PrakritiRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<void> saveProfile(Map<String, dynamic> payload) async {
    await runWithRetry<dynamic>(() => _api.post('/prakriti/profile', payload));
    await HiveService.savePrakritiProfile(payload);
  }

  Future<Map<String, dynamic>> loadProfile() async {
    final Map<String, dynamic>? local = HiveService.getPrakritiProfile();
    if (local != null && local.isNotEmpty) {
      return local;
    }
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/prakriti/profile'));
    final Map<String, dynamic> data = extractDataMap(response);
    await HiveService.savePrakritiProfile(data);
    return data;
  }

  Future<List<String>> tips(String dosha) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.get('/prakriti/tips', queryParams: <String, dynamic>{'dosha': dosha}),
    );
    final Map<String, dynamic> data = extractDataMap(response);
    return (data['tips'] as List<dynamic>? ?? <dynamic>[]).map((dynamic item) => item.toString()).toList(growable: false);
  }
}
