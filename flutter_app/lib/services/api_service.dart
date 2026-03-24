import 'package:dio/dio.dart';
class ApiService {
  final Dio dio = Dio(BaseOptions(baseUrl: "http://localhost:8000/"));
  Future<Response> get(String path) => dio.get(path);
  Future<Response> post(String path, dynamic data) => dio.post(path, data: data);
}\n