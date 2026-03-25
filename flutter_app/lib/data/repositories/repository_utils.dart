import 'package:dio/dio.dart';

Future<T> runWithRetry<T>(Future<T> Function() action, {int retries = 1}) async {
  int attempt = 0;
  while (true) {
    try {
      return await action();
    } on DioException {
      if (attempt >= retries) {
        rethrow;
      }
      attempt += 1;
      await Future<void>.delayed(const Duration(milliseconds: 350));
    }
  }
}

Map<String, dynamic> extractDataMap(dynamic response) {
  if (response is Map<String, dynamic>) {
    final dynamic data = response['data'];
    if (data is Map<String, dynamic>) {
      return data;
    }
    return response;
  }
  return <String, dynamic>{};
}

List<Map<String, dynamic>> extractDataList(dynamic response) {
  if (response is Map<String, dynamic>) {
    final dynamic data = response['data'];
    if (data is List) {
      return data
          .whereType<Map>()
          .map((Map item) => Map<String, dynamic>.from(item))
          .toList(growable: false);
    }
  }
  if (response is List) {
    return response
        .whereType<Map>()
        .map((Map item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
  }
  return <Map<String, dynamic>>[];
}
