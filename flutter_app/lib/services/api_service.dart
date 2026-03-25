import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'hive_service.dart';

class ApiService {
  static const String _compileTimeApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  ApiService._internal() {
    final String? savedBaseUrl = HiveService.getSetting('api_base_url') as String?;
    _dio.options.baseUrl = (savedBaseUrl != null && savedBaseUrl.trim().isNotEmpty)
        ? savedBaseUrl.trim()
        : _compileTimeApiBaseUrl;

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _secureStorage.read(key: 'jwt') ?? HiveService.getJwt();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          options.headers['X-Language'] = HiveService.getLanguageCode();
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            await _secureStorage.delete(key: 'jwt');
          }
          handler.next(error);
        },
      ),
    );
  }

  static final ApiService instance = ApiService._internal();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: _compileTimeApiBaseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
      sendTimeout: const Duration(seconds: 20),
      headers: {'Content-Type': 'application/json'},
    ),
  );

  Future<void> updateBaseUrl(String baseUrl) async {
    final String normalized = baseUrl.trim();
    if (normalized.isEmpty) {
      return;
    }
    _dio.options.baseUrl = normalized;
    await HiveService.saveSettings('api_base_url', normalized);
  }

  Future<void> saveJwt(String token) async {
    await _secureStorage.write(key: 'jwt', value: token);
  }

  Future<void> clearJwt() async {
    await _secureStorage.delete(key: 'jwt');
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? queryParams}) async {
    final response = await _dio.get(path, queryParameters: queryParams);
    return response.data;
  }

  Future<dynamic> post(String path, dynamic data) async {
    final response = await _dio.post(path, data: data);
    return response.data;
  }

  Future<dynamic> put(String path, dynamic data) async {
    final response = await _dio.put(path, data: data);
    return response.data;
  }

  Future<dynamic> delete(String path) async {
    final response = await _dio.delete(path);
    return response.data;
  }
}
