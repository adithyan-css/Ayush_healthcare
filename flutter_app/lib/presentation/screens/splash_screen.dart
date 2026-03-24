import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../core/i18n/language_map.dart';
import '../../services/hive_service.dart';
import '../cubits/auth_cubit.dart';

class SplashScreen extends StatefulWidget {
	const SplashScreen({super.key});

	@override
	State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
	final Completer<void> _delayCompleter = Completer<void>();
	bool _authResolved = false;
	AuthState? _lastState;

	@override
	void initState() {
		super.initState();
		Future.delayed(const Duration(seconds: 2), () {
			if (!_delayCompleter.isCompleted) _delayCompleter.complete();
			_handleNavigation();
		});
		context.read<AuthCubit>().checkAuthStatus();
	}

	Future<void> _handleNavigation() async {
		if (!_authResolved || _lastState == null) return;
		await _delayCompleter.future;
		if (!mounted) return;

		if (_lastState is AuthAuthenticated) {
			if (HiveService.hasPrakritiProfile()) {
				context.go('/home');
			} else {
				context.go('/quiz');
			}
		} else if (_lastState is AuthUnauthenticated) {
			context.go('/login');
		}
	}

	@override
	Widget build(BuildContext context) {
		final colorScheme = Theme.of(context).colorScheme;
		final textTheme = Theme.of(context).textTheme;
		return Scaffold(
			body: BlocListener<AuthCubit, AuthState>(
				listener: (context, state) {
					if (state is AuthAuthenticated || state is AuthUnauthenticated) {
						_authResolved = true;
						_lastState = state;
						_handleNavigation();
					}
				},
				child: Container(
					decoration: BoxDecoration(
						gradient: LinearGradient(
							begin: Alignment.topLeft,
							end: Alignment.bottomRight,
							colors: [colorScheme.primaryContainer, colorScheme.surface],
						),
					),
					child: Stack(
						children: [
							Center(
								child: Container(
									width: 260,
									height: 260,
									decoration: BoxDecoration(
										shape: BoxShape.circle,
										color: colorScheme.primary.withValues(alpha: 0.08),
									),
								),
							),
							Center(
								child: Column(
									mainAxisSize: MainAxisSize.min,
									children: [
										CircleAvatar(
											radius: 38,
											backgroundColor: colorScheme.primary.withValues(alpha: 0.12),
											child: Icon(Icons.spa, size: 42, color: colorScheme.primary),
										),
										const SizedBox(height: 14),
										Text(context.t('app_name'), style: textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w700)),
									],
								),
							),
						],
					),
				),
			),
		);
	}
}
