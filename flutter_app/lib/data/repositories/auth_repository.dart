import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import 'repository_utils.dart';

class AuthRepository {
  AuthRepository({ApiService? apiService}) : _api = apiService ?? ApiService.instance;

  final ApiService _api;

  Future<Map<String, dynamic>> login(String email, String password) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post('/auth/login', <String, dynamic>{'email': email, 'password': password}),
    );
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> register(String name, String email, String password, String language) async {
    final dynamic response = await runWithRetry<dynamic>(
      () => _api.post(
        '/auth/register',
        <String, dynamic>{
          'email': email,
          'password': password,
          'display_name': name,
          'language': language,
        },
      ),
    );
    return extractDataMap(response);
  }

  Future<Map<String, dynamic>> me() async {
    final dynamic response = await runWithRetry<dynamic>(() => _api.get('/auth/me'));
    return extractDataMap(response);
  }

  Future<void> updateMe({String? displayName, String? language}) async {
    final Map<String, dynamic> payload = <String, dynamic>{};
    if (displayName != null) {
      payload['display_name'] = displayName;
    }
    if (language != null) {
      payload['language'] = language;
    }
    if (payload.isEmpty) {
      return;
    }
    await runWithRetry<dynamic>(() => _api.put('/auth/me', payload));
  }

  Future<void> saveSession(Map<String, dynamic> tokenData) async {
    final String access = (tokenData['access_token'] ?? '').toString();
    final String refresh = (tokenData['refresh_token'] ?? '').toString();
    if (access.isNotEmpty) {
      await HiveService.saveJwt(access);
    }
    if (refresh.isNotEmpty) {
      await HiveService.saveRefreshToken(refresh);
    }
    await _api.saveAuthTokens(accessToken: access, refreshToken: refresh);
  }

  Future<void> logout() async {
    try {
      await _api.post('/auth/logout', <String, dynamic>{});
    } catch (_) {}
    await HiveService.clearJwt();
    await HiveService.clearRefreshToken();
    await _api.clearAuthTokens();
  }
}
