import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
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
		return Scaffold(
			body: BlocListener<AuthCubit, AuthState>(
				listener: (context, state) {
					if (state is AuthAuthenticated || state is AuthUnauthenticated) {
						_authResolved = true;
						_lastState = state;
						_handleNavigation();
					}
				},
				child: Center(
					child: Column(
						mainAxisSize: MainAxisSize.min,
						children: [
							Icon(Icons.spa, size: 64, color: Theme.of(context).colorScheme.primary),
							const SizedBox(height: 12),
							Text(
								'PrakritiOS',
								style: TextStyle(
									fontSize: 36,
									fontWeight: FontWeight.bold,
									color: Theme.of(context).colorScheme.primary,
								),
							),
						],
					),
				),
			),
		);
	}
}
