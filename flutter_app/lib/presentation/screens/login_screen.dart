import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../services/hive_service.dart';
import '../cubits/auth_cubit.dart';

class LoginScreen extends StatefulWidget {
	const LoginScreen({super.key});

	@override
	State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
	final _formKey = GlobalKey<FormState>();
	final _emailController = TextEditingController();
	final _passwordController = TextEditingController();

	@override
	void dispose() {
		_emailController.dispose();
		_passwordController.dispose();
		super.dispose();
	}

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			body: BlocListener<AuthCubit, AuthState>(
				listener: (context, state) {
					if (state is AuthAuthenticated) {
						if (HiveService.hasPrakritiProfile()) {
							context.go('/home');
						} else {
							context.go('/quiz');
						}
					}
					if (state is AuthError) {
						ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
					}
				},
				child: SafeArea(
					child: Center(
						child: SingleChildScrollView(
							padding: const EdgeInsets.all(20),
							child: Form(
								key: _formKey,
								child: ConstrainedBox(
									constraints: const BoxConstraints(maxWidth: 420),
									child: Column(
										children: [
											Icon(Icons.spa, size: 72, color: Theme.of(context).colorScheme.primary),
											const SizedBox(height: 8),
											Text('PrakritiOS', style: Theme.of(context).textTheme.headlineMedium),
											const SizedBox(height: 24),
											TextFormField(
												controller: _emailController,
												keyboardType: TextInputType.emailAddress,
												decoration: const InputDecoration(labelText: 'Email'),
												validator: (v) => (v == null || !v.contains('@')) ? 'Enter a valid email' : null,
											),
											const SizedBox(height: 12),
											TextFormField(
												controller: _passwordController,
												decoration: const InputDecoration(labelText: 'Password'),
												obscureText: true,
												validator: (v) => (v == null || v.length < 6) ? 'Minimum 6 characters' : null,
											),
											const SizedBox(height: 16),
											SizedBox(
												width: double.infinity,
												child: ElevatedButton(
													onPressed: () {
														if (_formKey.currentState?.validate() ?? false) {
															context.read<AuthCubit>().signInWithEmail(_emailController.text.trim(), _passwordController.text.trim());
														}
													},
													child: const Text('Sign In'),
												),
											),
											const SizedBox(height: 8),
											SizedBox(
												width: double.infinity,
												child: OutlinedButton.icon(
													onPressed: () {
														context.read<AuthCubit>().signInWithGoogle();
													},
													icon: const Icon(Icons.login),
													label: const Text('Google Sign In'),
												),
											),
											const SizedBox(height: 8),
											TextButton(
												onPressed: () => context.go('/register'),
												child: const Text('New user? Register'),
											),
										],
									),
								),
							),
						),
					),
				),
			),
		);
	}
}
