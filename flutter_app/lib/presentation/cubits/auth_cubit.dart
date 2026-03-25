import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:dio/dio.dart';
import '../../data/repositories/auth_repository.dart';
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

	final AuthRepository _repo = AuthRepository();

	Future<void> _saveAuthSession(Map<String, dynamic> tokenData) async {
		final String token = (tokenData['access_token'] ?? '').toString();
		if (token.isEmpty) {
			throw Exception('Missing access token');
		}
		await _repo.saveSession(tokenData);

		final Map<String, dynamic> meData = await _repo.me();
		await HiveService.saveSettings('user_data', meData);
		emit(AuthAuthenticated(meData));
	}

	Future<void> checkAuthStatus() async {
		final jwt = HiveService.getJwt();
		if (jwt != null && jwt.isNotEmpty) {
			await _repo.saveSession(<String, dynamic>{'access_token': jwt, 'refresh_token': HiveService.getRefreshToken()});
			try {
				final Map<String, dynamic> user = await _repo.me();
				await HiveService.saveSettings('user_data', user);
				emit(AuthAuthenticated(user));
			} catch (_) {
				await HiveService.clearJwt();
				await HiveService.clearRefreshToken();
				emit(AuthUnauthenticated());
			}
		} else {
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signInWithEmail(String email, String password) async {
		emit(AuthLoading());
		try {
			final Map<String, dynamic> response = await _repo.login(email, password);
			await _saveAuthSession(response);
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
			final Map<String, dynamic> response = await _repo.register(name, email, password, language);
			await _saveAuthSession(response);
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
		await _repo.logout();
		await Hive.box('prakriti').clear();
		emit(AuthUnauthenticated());
	}
}
