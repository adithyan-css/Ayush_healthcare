import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import 'repository_utils.dart';

class HeatmapRepository {
  HeatmapRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<List<Map<String, dynamic>>> districts({String? condition, String? season}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.get(
        '/heatmap/districts',
        queryParams: <String, dynamic>{
          if (condition != null && condition.isNotEmpty && condition.toLowerCase() != 'all') 'condition': condition,
          if (season != null && season.isNotEmpty && season.toLowerCase() != 'all') 'season': season,
        },
      ),
    );
    final List<Map<String, dynamic>> rows = extractDataList(response);
    if (rows.isNotEmpty) {
      await HiveService.saveDistrictRisks(rows.cast<Map>());
    }
    return rows;
  }

  List<Map<String, dynamic>>? cachedDistricts() {
    return HiveService.getDistrictRisks();
  }

  Future<Map<String, dynamic>> stateDetail(String stateId) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/heatmap/state/$stateId'));
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> stateTrend(String stateId) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/heatmap/trends/$stateId'));
    return extractDataMap(response);
  }

  Future<List<Map<String, dynamic>>> rising({int limit = 5}) async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/heatmap/rising', queryParams: <String, dynamic>{'limit': limit}));
    return extractDataList(response);
  }
}
