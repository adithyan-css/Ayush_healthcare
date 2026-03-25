import '../../services/api_service.dart';
import 'repository_utils.dart';

class VaidyaRepository {
  VaidyaRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<List<Map<String, dynamic>>> patients({String search = ''}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.get('/vaidya/patients', queryParams: <String, dynamic>{'search': search}),
    );
    return extractDataList(response);
  }

  Future<Map<String, dynamic>> suggest({required List<String> symptoms, required String dosha, required String patientUid}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post('/vaidya/suggest', <String, dynamic>{'symptoms': symptoms, 'dosha': dosha, 'patient_uid': patientUid}),
    );
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> consult({required String patientUid, required List<String> symptoms, required Map<String, dynamic> suggestion}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post('/vaidya/consult', <String, dynamic>{
            'patient_uid': patientUid,
            'symptoms': symptoms,
            'suggestion': suggestion,
          }),
    );
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> updateOutcome({required String consultId, required Map<String, dynamic> outcome}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.patch('/vaidya/outcome/$consultId', outcome),
    );
    return extractDataMap(response);
  }

  Future<List<Map<String, dynamic>>> reports({String? patientUid, int limit = 20}) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.get('/vaidya/reports', queryParams: <String, dynamic>{if (patientUid != null && patientUid.isNotEmpty) 'patient_uid': patientUid, 'limit': limit}),
    );
    return extractDataList(response);
  }

  Future<List<Map<String, dynamic>>> evidence() async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/vaidya/evidence'));
    return extractDataList(response);
  }
}
