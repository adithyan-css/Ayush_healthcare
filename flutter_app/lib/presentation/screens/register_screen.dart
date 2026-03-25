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
		final colorScheme = Theme.of(context).colorScheme;
		final textTheme = Theme.of(context).textTheme;
		return Scaffold(
			body: BlocListener<AuthCubit, AuthState>(
				listener: (context, state) {
					if (state is AuthAuthenticated) {
						context.go('/prakriti/quiz');
					}
					if (state is AuthError) {
						ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
					}
				},
				child: SafeArea(
					child: LayoutBuilder(
						builder: (context, constraints) {
							return Column(
								children: [
									Container(
										height: constraints.maxHeight * 0.3,
										width: double.infinity,
										padding: const EdgeInsets.symmetric(horizontal: 24),
										decoration: BoxDecoration(
											gradient: LinearGradient(
												begin: Alignment.topLeft,
												end: Alignment.bottomRight,
												colors: [colorScheme.secondaryContainer, colorScheme.surface],
											),
										),
										child: Column(
											mainAxisAlignment: MainAxisAlignment.center,
											children: [
												CircleAvatar(
													radius: 28,
													backgroundColor: colorScheme.secondary.withValues(alpha: 0.12),
													child: Icon(Icons.person_add_alt_1, color: colorScheme.secondary),
												),
												const SizedBox(height: 10),
												Text(context.t('register'), style: textTheme.headlineSmall),
											],
										),
									),
									Expanded(
										child: Container(
											width: double.infinity,
											padding: const EdgeInsets.fromLTRB(20, 24, 20, 20),
											decoration: BoxDecoration(
												color: colorScheme.surface,
												borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
											),
											child: Center(
												child: SingleChildScrollView(
													child: Form(
														key: _formKey,
														child: ConstrainedBox(
															constraints: const BoxConstraints(maxWidth: 420),
															child: Column(
																crossAxisAlignment: CrossAxisAlignment.stretch,
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
																	ElevatedButton(
																		onPressed: () {
																			if (_formKey.currentState?.validate() ?? false) {
																				context.read<AuthCubit>().registerWithEmail(
																					_nameController.text.trim(),
																					_emailController.text.trim(),
																					_passwordController.text.trim(),
																				);
																			}
																		},
																		child: Text(context.t('create_account')),
																	),
																	TextButton(onPressed: () => context.go('/login'), child: Text(context.t('already_have_account'))),
																],
															),
														),
													),
												),
											),
										),
									),
								],
							);
						},
					),
				),
			),
		);
	}
}
