import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../services/hive_service.dart';
import '../cubits/auth_cubit.dart';

class SettingsScreen extends StatefulWidget {
	const SettingsScreen({super.key});

	@override
	State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
	final List<String> _languages = ['English', 'Tamil', 'Hindi', 'Telugu'];
	late String _selectedLanguage;
	late bool _notifications;

	@override
	void initState() {
		super.initState();
		_selectedLanguage = (HiveService.getSetting('language')?.toString() ?? 'English');
		_notifications = (HiveService.getSetting('notifications') as bool?) ?? true;
	}

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(title: const Text('Settings')),
			body: Padding(
				padding: const EdgeInsets.all(16),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						const Text('Language'),
						const SizedBox(height: 6),
						DropdownButtonFormField<String>(
							value: _selectedLanguage,
							items: _languages.map((l) => DropdownMenuItem(value: l, child: Text(l))).toList(),
							onChanged: (value) async {
								if (value == null) return;
								setState(() => _selectedLanguage = value);
								await HiveService.saveSettings('language', value);
							},
						),
						const SizedBox(height: 16),
						SwitchListTile(
							contentPadding: EdgeInsets.zero,
							title: const Text('Notifications'),
							value: _notifications,
							onChanged: (value) async {
								setState(() => _notifications = value);
								await HiveService.saveSettings('notifications', value);
							},
						),
						const Divider(height: 28),
						const ListTile(
							contentPadding: EdgeInsets.zero,
							leading: Icon(Icons.info_outline),
							title: Text('About'),
							subtitle: Text('PrakritiOS v1.0.0'),
						),
						const Spacer(),
						SizedBox(
							width: double.infinity,
							child: ElevatedButton.icon(
								style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade600, foregroundColor: Colors.white),
								onPressed: () async {
									await context.read<AuthCubit>().signOut();
									if (context.mounted) context.go('/login');
								},
								icon: const Icon(Icons.logout),
								label: const Text('Sign Out'),
							),
						),
					],
				),
			),
		);
	}
}
