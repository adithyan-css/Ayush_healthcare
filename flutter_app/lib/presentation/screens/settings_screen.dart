import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

import '../../core/i18n/language_map.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';
import '../cubits/auth_cubit.dart';
import '../cubits/language_cubit.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late bool _notifications;

  @override
  void initState() {
    super.initState();
    _notifications = (HiveService.getSetting('notifications') as bool?) ?? true;
  }

  Future<void> _saveLanguage(String code) async {
    await context.read<LanguageCubit>().setLanguage(code);
    try {
      await ApiService.instance.put('/auth/me', <String, dynamic>{'language': code});
    } catch (_) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(context.t('cache_clear_failed'))));
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
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(context.t('unable_reset_quiz'))));
    }
  }

  Future<void> _clearCache() async {
    try {
      await Hive.box('sessions').clear();
      await HiveService.saveSettings('districtRiskUpdatedAt', null);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(context.t('cache_cleared'))));
    } catch (_) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(context.t('cache_clear_failed'))));
    }
  }

  @override
  Widget build(BuildContext context) {
    final String selectedCode = context.select((LanguageCubit cubit) => cubit.state.languageCode);

    return Scaffold(
      appBar: AppBar(title: Text(context.t('settings'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(context.t('language')),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              value: selectedCode,
              items: AppText.supportedLanguages
                  .map((Map<String, String> language) => DropdownMenuItem<String>(
                        value: language['code'],
                        child: Text(language['name'] ?? ''),
                      ))
                  .toList(),
              onChanged: (String? code) async {
                if (code == null) {
                  return;
                }
                await _saveLanguage(code);
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(context.t('notifications')),
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
              title: Text(context.t('retake_quiz')),
              onTap: _retakeQuiz,
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.cleaning_services_outlined),
              title: Text(context.t('clear_cache')),
              onTap: _clearCache,
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.info_outline),
              title: Text(context.t('about')),
              subtitle: const Text('PrakritiOS v1.0.0'),
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
                label: Text(context.t('sign_out')),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
