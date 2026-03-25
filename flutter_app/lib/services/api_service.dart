import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:async';
import 'hive_service.dart';

class ApiService {
  static const String _defaultApiBaseUrl = 'http://10.0.2.2:8000/api/v1';
  static const String _compileTimeApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: _defaultApiBaseUrl,
  );

  ApiService._internal() {
    final String? savedBaseUrl = HiveService.getSetting('api_base_url') as String?;
    final bool hasExplicitCompileTimeBaseUrl = _compileTimeApiBaseUrl.trim() != _defaultApiBaseUrl;
    if (hasExplicitCompileTimeBaseUrl) {
      _dio.options.baseUrl = _compileTimeApiBaseUrl.trim();
    } else if (savedBaseUrl != null && savedBaseUrl.trim().isNotEmpty) {
      _dio.options.baseUrl = savedBaseUrl.trim();
    } else {
      _dio.options.baseUrl = _compileTimeApiBaseUrl;
    }

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
          final RequestOptions options = error.requestOptions;
          final bool isRefreshCall = options.path.contains('/auth/refresh');
          final bool alreadyRetried = options.extra['retried'] == true;
          if (error.response?.statusCode == 401 && !isRefreshCall && !alreadyRetried) {
            final String? freshToken = await _refreshAccessToken();
            if (freshToken != null && freshToken.isNotEmpty) {
              final RequestOptions retryOptions = options.copyWith(
                headers: <String, dynamic>{...options.headers, 'Authorization': 'Bearer $freshToken'},
                extra: <String, dynamic>{...options.extra, 'retried': true},
              );
              try {
                final Response<dynamic> retryResponse = await _dio.fetch<dynamic>(retryOptions);
                return handler.resolve(retryResponse);
              } catch (_) {}
            }

            await clearAuthTokens();
          }
          handler.next(error);
        },
      ),
    );
  }

  static final ApiService instance = ApiService._internal();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  Completer<String?>? _refreshCompleter;

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

  Future<void> saveAuthTokens({required String accessToken, String? refreshToken}) async {
    if (accessToken.isNotEmpty) {
      await _secureStorage.write(key: 'jwt', value: accessToken);
      await HiveService.saveJwt(accessToken);
    }
    final String? refresh = refreshToken?.trim();
    if (refresh != null && refresh.isNotEmpty) {
      await _secureStorage.write(key: 'refresh_token', value: refresh);
      await HiveService.saveRefreshToken(refresh);
    }
  }

  Future<void> clearJwt() async {
    await _secureStorage.delete(key: 'jwt');
  }

  Future<void> clearAuthTokens() async {
    await _secureStorage.delete(key: 'jwt');
    await _secureStorage.delete(key: 'refresh_token');
    await HiveService.clearJwt();
    await HiveService.clearRefreshToken();
  }

  Future<String?> _refreshAccessToken() async {
    if (_refreshCompleter != null) {
      return _refreshCompleter!.future;
    }

    _refreshCompleter = Completer<String?>();
    try {
      final String? refreshToken = await _secureStorage.read(key: 'refresh_token') ?? HiveService.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        _refreshCompleter!.complete(null);
        return _refreshCompleter!.future;
      }

      final Dio refreshDio = Dio(BaseOptions(baseUrl: _dio.options.baseUrl, headers: <String, dynamic>{'Content-Type': 'application/json'}));
      final Response<dynamic> response = await refreshDio.post('/auth/refresh', data: <String, dynamic>{'refresh_token': refreshToken});
      final dynamic payload = response.data;
      final String access = (payload is Map<String, dynamic> && payload['data'] is Map<String, dynamic>)
          ? (payload['data']['access_token'] ?? '').toString()
          : (payload is Map<String, dynamic> ? (payload['access_token'] ?? '').toString() : '');
      if (access.isEmpty) {
        _refreshCompleter!.complete(null);
        return _refreshCompleter!.future;
      }

      await saveAuthTokens(accessToken: access, refreshToken: refreshToken);
      _refreshCompleter!.complete(access);
      return _refreshCompleter!.future;
    } catch (_) {
      _refreshCompleter!.complete(null);
      return _refreshCompleter!.future;
    } finally {
      _refreshCompleter = null;
    }
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

  Future<dynamic> patch(String path, dynamic data) async {
    final response = await _dio.patch(path, data: data);
    return response.data;
  }

  Future<dynamic> delete(String path) async {
    final response = await _dio.delete(path);
    return response.data;
  }
}
