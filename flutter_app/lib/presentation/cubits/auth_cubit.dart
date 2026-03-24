import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
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

	Future<void> checkAuthStatus() async {
		final jwt = HiveService.getJwt();
		if (jwt != null && jwt.isNotEmpty) {
			final storedUser = HiveService.getSetting('user_data');
			final user = storedUser is Map
					? Map<String, dynamic>.from(storedUser)
					: {
							'email': 'user@gmail.com',
							'display_name': 'Test User',
							'role': 'patient',
						};
			emit(AuthAuthenticated(user));
		} else {
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signInWithGoogle() async {
		emit(AuthLoading());
		try {
			final response = await _api.post('/auth/firebase-verify', {
				'firebase_uid': 'google_mock',
				'email': 'user@gmail.com',
				'display_name': 'Test User',
			});
			final token = (response['access_token'] ?? '').toString();
			await HiveService.saveJwt(token);
			await HiveService.saveSettings('user_data', {
				'email': 'user@gmail.com',
				'display_name': 'Test User',
				'role': 'patient',
			});
			emit(AuthAuthenticated({'email': 'user@gmail.com', 'display_name': 'Test User', 'role': 'patient'}));
		} catch (e) {
			emit(AuthError('Google sign-in failed: $e'));
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signInWithEmail(String email, String password) async {
		emit(AuthLoading());
		try {
			final response = await _api.post('/auth/firebase-verify', {
				'firebase_uid': 'email_${email.hashCode}',
				'email': email,
				'display_name': 'Test User',
			});
			final token = (response['access_token'] ?? '').toString();
			await HiveService.saveJwt(token);
			await HiveService.saveSettings('user_data', {
				'email': email,
				'display_name': 'Test User',
				'role': 'patient',
			});
			emit(AuthAuthenticated({'email': email, 'display_name': 'Test User', 'role': 'patient'}));
		} catch (e) {
			emit(AuthError('Email sign-in failed: $e'));
			emit(AuthUnauthenticated());
		}
	}

	Future<void> signOut() async {
		await HiveService.clearJwt();
		await Hive.box('prakriti').clear();
		emit(AuthUnauthenticated());
	}
}
