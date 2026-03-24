import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import '../cubits/auth_cubit.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final List<String> _languages = <String>['English', 'Tamil', 'Hindi', 'Telugu'];
  final Map<String, String> _languageCodeMap = <String, String>{
    'English': 'en',
    'Tamil': 'ta',
    'Hindi': 'hi',
    'Telugu': 'te',
  };

  late String _selectedLanguage;
  late bool _notifications;

  @override
  void initState() {
    super.initState();
    _selectedLanguage = (HiveService.getSetting('language')?.toString() ?? 'English');
    _notifications = (HiveService.getSetting('notifications') as bool?) ?? true;
  }

  Future<void> _saveLanguage(String language) async {
    final String code = _languageCodeMap[language] ?? 'en';
    await HiveService.saveSettings('language', language);
    await HiveService.saveSettings('language_code', code);
    try {
      await ApiService.instance.put('/auth/me', <String, dynamic>{'language': code});
    } catch (_) {
      // Silent fail: local preference should still persist.
    }
  }

  Future<void> _retakeQuiz() async {
    try {
      await Hive.box('prakriti').clear();
      if (!mounted) {
        return;
      }
      context.go('/quiz');
    } catch (_) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Unable to reset quiz right now')));
    }
  }

  Future<void> _clearCache() async {
    try {
      await Hive.box('sessions').clear();
      await HiveService.saveSettings('districtRiskUpdatedAt', null);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cache cleared')));
    } catch (_) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to clear cache')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            const Text('Language'),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              value: _selectedLanguage,
              items: _languages.map((String l) => DropdownMenuItem<String>(value: l, child: Text(l))).toList(),
              onChanged: (String? value) async {
                if (value == null) {
                  return;
                }
                setState(() {
                  _selectedLanguage = value;
                });
                await _saveLanguage(value);
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Notifications'),
              value: _notifications,
              onChanged: (bool value) async {
                setState(() {
                  _notifications = value;
                });
                await HiveService.saveSettings('notifications', value);
              },
            ),
            const Divider(height: 28),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.replay_circle_filled_outlined),
              title: const Text('Retake Prakriti Quiz'),
              onTap: _retakeQuiz,
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.cleaning_services_outlined),
              title: const Text('Clear Cache'),
              onTap: _clearCache,
            ),
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
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade600,
                  foregroundColor: Colors.white,
                ),
                onPressed: () async {
                  await context.read<AuthCubit>().signOut();
                  if (!mounted) {
                    return;
                  }
                  context.go('/login');
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
