import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../core/i18n/language_map.dart';
import '../cubits/auth_cubit.dart';

class RegisterScreen extends StatefulWidget {
	const RegisterScreen({super.key});

	@override
	State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
	final _formKey = GlobalKey<FormState>();
	final _nameController = TextEditingController();
	final _emailController = TextEditingController();
	final _passwordController = TextEditingController();

	@override
	void dispose() {
		_nameController.dispose();
		_emailController.dispose();
		_passwordController.dispose();
		super.dispose();
	}

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(title: Text(context.t('register'))),
			body: BlocListener<AuthCubit, AuthState>(
				listener: (context, state) {
					if (state is AuthAuthenticated) {
						context.go('/quiz');
					}
					if (state is AuthError) {
						ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
					}
				},
				child: Padding(
					padding: const EdgeInsets.all(20),
					child: Form(
						key: _formKey,
						child: Column(
							children: [
								TextFormField(
									controller: _nameController,
									decoration: InputDecoration(labelText: context.t('name')),
									validator: (v) => (v == null || v.trim().isEmpty) ? context.t('name_required') : null,
								),
								const SizedBox(height: 12),
								TextFormField(
									controller: _emailController,
									decoration: InputDecoration(labelText: context.t('email')),
									validator: (v) => (v == null || !v.contains('@')) ? context.t('valid_email_required') : null,
								),
								const SizedBox(height: 12),
								TextFormField(
									controller: _passwordController,
									decoration: InputDecoration(labelText: context.t('password')),
									obscureText: true,
									validator: (v) => (v == null || v.length < 6) ? context.t('minimum_6_chars') : null,
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
										child: Text(context.t('create_account')),
									),
								),
								TextButton(onPressed: () => context.go('/login'), child: Text(context.t('already_have_account'))),
							],
						),
					),
				),
			),
		);
	}
}
