import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

import '../../services/hive_service.dart';

class LanguageState extends Equatable {
  const LanguageState(this.languageCode);

  final String languageCode;

  @override
  List<Object?> get props => <Object?>[languageCode];
}

class LanguageCubit extends Cubit<LanguageState> {
  LanguageCubit() : super(const LanguageState('en'));

  static const Set<String> supported = <String>{'en', 'ta', 'hi', 'ja'};

  Future<void> loadSavedLanguage() async {
    final String saved = HiveService.getLanguageCode();
    emit(LanguageState(_normalize(saved)));
  }

  Future<void> setLanguage(String languageCode) async {
    final String normalized = _normalize(languageCode);
    await HiveService.saveLanguageCode(normalized);
    emit(LanguageState(normalized));
  }

  String _normalize(String code) {
    final String lowered = code.toLowerCase().trim();
    return supported.contains(lowered) ? lowered : 'en';
  }
}
