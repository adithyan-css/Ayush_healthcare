import 'package:flutter/material.dart';

class AppTheme {
	static ThemeData get lightTheme {
		final colorScheme = ColorScheme.fromSeed(
			seedColor: const Color(0xFF2E7D32),
			brightness: Brightness.light,
		);

		return ThemeData(
			useMaterial3: true,
			colorScheme: colorScheme,
			scaffoldBackgroundColor: Colors.grey.shade50,
			textTheme: TextTheme(
				displayLarge: const TextStyle(fontSize: 34, fontWeight: FontWeight.w700),
				headlineMedium: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
				titleLarge: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
				bodyLarge: TextStyle(fontSize: 16, color: Colors.grey.shade800),
				bodyMedium: TextStyle(fontSize: 14, color: Colors.grey.shade700),
				labelLarge: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
			),
			cardTheme: CardThemeData(
				elevation: 2,
				shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
			),
			inputDecorationTheme: InputDecorationTheme(
				border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
				contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
			),
		);
	}
}
