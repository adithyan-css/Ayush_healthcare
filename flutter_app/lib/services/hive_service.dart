import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';

class HiveService {
	static Box<dynamic> get _prakritiBox => Hive.box('prakriti');
	static Box<dynamic> get _sessionsBox => Hive.box('sessions');
	static Box<dynamic> get _settingsBox => Hive.box('settings');
	static Box<dynamic> get _districtRiskBox => Hive.box('districtRisk');
	static Box<dynamic> get _forecastBox => Hive.box('forecast');

	static Future<void> savePrakritiProfile(Map data) async {
		await _prakritiBox.put('profile', jsonEncode(data));
	}

	static Map<String, dynamic>? getPrakritiProfile() {
		final raw = _prakritiBox.get('profile');
		if (raw == null) return null;
		return Map<String, dynamic>.from(jsonDecode(raw as String) as Map);
	}

	static bool hasPrakritiProfile() {
		return _prakritiBox.containsKey('profile');
	}

	static Future<void> saveSession(Map data) async {
		final key = DateTime.now().millisecondsSinceEpoch.toString();
		await _sessionsBox.put(key, jsonEncode(data));
	}

	static List<Map<String, dynamic>> getSessions() {
		return _sessionsBox.values
				.map((e) => Map<String, dynamic>.from(jsonDecode(e as String) as Map))
				.toList()
			..sort(
				(a, b) => DateTime.tryParse(b['created_at']?.toString() ?? '')
								?.compareTo(DateTime.tryParse(a['created_at']?.toString() ?? '') ?? DateTime(1970)) ??
						0,
			);
	}

	static Future<void> clearOldSessions({int keepLast = 50}) async {
		final keys = _sessionsBox.keys.map((e) => e.toString()).toList()..sort();
		if (keys.length <= keepLast) return;
		final remove = keys.take(keys.length - keepLast);
		for (final key in remove) {
			await _sessionsBox.delete(key);
		}
	}

	static Future<void> saveJwt(String token) async {
		await _settingsBox.put('jwt', token);
	}

	static String? getJwt() {
		return _settingsBox.get('jwt') as String?;
	}

	static Future<void> clearJwt() async {
		await _settingsBox.delete('jwt');
	}

	static Future<void> saveSettings(String key, dynamic value) async {
		if (value is Map || value is List) {
			await _settingsBox.put(key, jsonEncode(value));
			return;
		}
		await _settingsBox.put(key, value);
	}

	static String normalizeLanguageCode(dynamic value) {
		final String source = (value ?? '').toString().toLowerCase().trim();
		switch (source) {
			case 'en':
			case 'english':
				return 'en';
			case 'ta':
			case 'tamil':
				return 'ta';
			case 'hi':
			case 'hindi':
				return 'hi';
			case 'ja':
			case 'japanese':
				return 'ja';
			default:
				return 'en';
		}
	}

	static Future<void> saveLanguageCode(String code) async {
		final String normalized = normalizeLanguageCode(code);
		await _settingsBox.put('language_code', normalized);
	}

	static String getLanguageCode() {
		final dynamic direct = _settingsBox.get('language_code');
		if (direct != null) {
			return normalizeLanguageCode(direct);
		}
		final dynamic legacy = _settingsBox.get('language');
		return normalizeLanguageCode(legacy);
	}

	static dynamic getSetting(String key) {
		final value = _settingsBox.get(key);
		if (value is String && (value.startsWith('{') || value.startsWith('['))) {
			try {
				return jsonDecode(value);
			} catch (_) {
				return value;
			}
		}
		return value;
	}

	static Future<void> saveForecast(Map data) async {
		await _forecastBox.put('national', jsonEncode(data));
		await _forecastBox.put('updatedAt', DateTime.now().toIso8601String());
	}

	static Map<String, dynamic>? getForecast() {
		final raw = _forecastBox.get('national');
		if (raw == null) return null;
		return Map<String, dynamic>.from(jsonDecode(raw as String) as Map);
	}

	static Future<void> saveDistrictRisks(List<Map> data) async {
		await _districtRiskBox.put('list', jsonEncode(data));
		await _districtRiskBox.put('updatedAt', DateTime.now().toIso8601String());
	}

	static List<Map<String, dynamic>>? getDistrictRisks() {
		final raw = _districtRiskBox.get('list');
		if (raw == null) return null;
		return (jsonDecode(raw as String) as List)
				.map((e) => Map<String, dynamic>.from(e as Map))
				.toList();
	}
}
