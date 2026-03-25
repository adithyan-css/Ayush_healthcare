import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:dio/dio.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';

abstract class AuthState {}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
	final Map<String, dynamic> user;
	AuthAuthenticated(this.user);
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
	final String message;
	AuthError(this.message);
}

class AuthCubit extends Cubit<AuthState> {
	AuthCubit() : super(AuthInitial());

	final ApiService _api = ApiService.instance;

	Map<String, dynamic> _extractData(dynamic response) {
		if (response is Map<String, dynamic>) {
			final dynamic data = response['data'];
			if (data is Map<String, dynamic>) {
				return data;
			}
			return response;
		}
		return <String, dynamic>{};
	}

	Future<void> _saveAuthSession(Map<String, dynamic> tokenData) async {
		final String token = (tokenData['access_token'] ?? '').toString();
		if (token.isEmpty) {
			throw Exception('Missing access token');
		}
		await HiveService.saveJwt(token);
		await _api.saveJwt(token);

		final dynamic meResponse = await _api.get('/auth/me');
		final Map<String, dynamic> meData = _extractData(meResponse);
		await HiveService.saveSettings('user_data', meData);
		emit(AuthAuthenticated(meData));
	}

	Future<void> checkAuthStatus() async {
		final jwt = HiveService.getJwt();
		if (jwt != null && jwt.isNotEmpty) {
			await _api.saveJwt(jwt);
			try {
				final dynamic response = await _api.get('/auth/me');
				final Map<String, dynamic> user = _extractData(response);
				await HiveService.saveSettings('user_data', user);
				emit(AuthAuthenticated(user));
			} catch (_) {
				await HiveService.clearJwt();
				await _api.clearJwt();
				emit(AuthUnauthenticated());
			}
		} else {
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signInWithEmail(String email, String password) async {
		emit(AuthLoading());
		try {
			final dynamic response = await _api.post('/auth/login', {
				'email': email,
				'password': password,
			});
			await _saveAuthSession(_extractData(response));
		} on DioException catch (e) {
			if (e.type == DioExceptionType.connectionTimeout ||
				e.type == DioExceptionType.receiveTimeout ||
				e.type == DioExceptionType.sendTimeout ||
				e.type == DioExceptionType.connectionError) {
				emit(AuthError('Email sign-in failed: Cannot reach server. Start backend and verify API URL.'));
			} else {
				emit(AuthError('Email sign-in failed: ${e.message ?? e.toString()}'));
			}
			emit(AuthUnauthenticated());
		} catch (e) {
			emit(AuthError('Email sign-in failed: $e'));
			emit(AuthUnauthenticated());
		}
	}

	Future<void> registerWithEmail(String name, String email, String password) async {
		emit(AuthLoading());
		try {
			final String language = HiveService.getLanguageCode();
			final dynamic response = await _api.post('/auth/register', {
				'email': email,
				'password': password,
				'display_name': name,
				'language': language,
			});
			await _saveAuthSession(_extractData(response));
		} on DioException catch (e) {
			if (e.type == DioExceptionType.connectionTimeout ||
				e.type == DioExceptionType.receiveTimeout ||
				e.type == DioExceptionType.sendTimeout ||
				e.type == DioExceptionType.connectionError) {
				emit(AuthError('Registration failed: Cannot reach server. Start backend and verify API URL.'));
			} else {
				emit(AuthError('Registration failed: ${e.message ?? e.toString()}'));
			}
			emit(AuthUnauthenticated());
		} catch (e) {
			emit(AuthError('Registration failed: $e'));
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signOut() async {
		await HiveService.clearJwt();
		await _api.clearJwt();
		await Hive.box('prakriti').clear();
		emit(AuthUnauthenticated());
	}
}
