import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import 'repository_utils.dart';

class ForecastRepository {
  ForecastRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<Map<String, dynamic>> loadDashboard() async {
    final List<dynamic> results = await runWithRetry<List<dynamic>>(
      () => Future.wait<dynamic>(<Future<dynamic>>[
        _api.get('/forecast/national'),
        _api.get('/forecast/regions'),
        _api.get('/forecast/population'),
        _api.get('/forecast/seasonal'),
      ]),
    );

    final Map<String, dynamic> national = extractDataMap(results[0]);
    final List<Map<String, dynamic>> regions = extractDataList(results[1]);
    final Map<String, dynamic> population = extractDataMap(results[2]);
    final Map<String, dynamic> seasonal = extractDataMap(results[3]);

    final Map<String, dynamic> merged = <String, dynamic>{
      'conditions': Map<String, dynamic>.from(national['conditions'] as Map? ?? <String, dynamic>{}),
      'region_cards': regions,
      'population_risks': population,
      'seasonal': seasonal,
    };
    await HiveService.saveForecast(merged);
    return merged;
  }

  Map<String, dynamic>? getCachedDashboard() {
    return HiveService.getForecast();
  }

  Future<Map<String, dynamic>> bulletin(String districtId) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post('/forecast/bulletin', <String, dynamic>{'district_id': districtId}),
    );
    return extractDataMap(response);
  }

  Future<List<String>> explain(String stateId) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/forecast/explain/$stateId'));
    final Map<String, dynamic> data = extractDataMap(response);
    return (data['reasons'] as List<dynamic>? ?? <dynamic>[]).map((dynamic item) => item.toString()).toList(growable: false);
  }
}
