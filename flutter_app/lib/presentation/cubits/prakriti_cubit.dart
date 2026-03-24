import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';

abstract class PrakritiState {}

class PrakritiInitial extends PrakritiState {}

class PrakritiLoading extends PrakritiState {}

class PrakritiQuestionsLoaded extends PrakritiState {
	final List<dynamic> questions;
	final int currentIndex;
	final Map<String, int> answers;
	final bool complete;

	PrakritiQuestionsLoaded(this.questions, this.currentIndex, this.answers, {this.complete = false});
}

class PrakritiCompleted extends PrakritiState {
	final Map<String, dynamic> profile;
	PrakritiCompleted(this.profile);
}

class PrakritiError extends PrakritiState {
	final String msg;
	PrakritiError(this.msg);
}

class PrakritiCubit extends Cubit<PrakritiState> {
	PrakritiCubit() : super(PrakritiInitial());

	final ApiService _api = ApiService.instance;
	List<dynamic> _questions = [];
	final Map<String, int> _answers = {'vata': 0, 'pitta': 0, 'kapha': 0};
	int _answeredCount = 0;
	int _currentIndex = 0;

	Future<void> loadQuestions() async {
		emit(PrakritiLoading());
		try {
			final jsonStr = await rootBundle.loadString('assets/data/prakriti_questions.json');
			_questions = jsonDecode(jsonStr) as List<dynamic>;
			_currentIndex = 0;
			_answeredCount = 0;
			_answers['vata'] = 0;
			_answers['pitta'] = 0;
			_answers['kapha'] = 0;
			emit(PrakritiQuestionsLoaded(_questions, _currentIndex, Map<String, int>.from(_answers)));
		} catch (e) {
			emit(PrakritiError('Failed to load questions: $e'));
		}
	}

	void answerQuestion(int index, String doshaKey) {
		if (index != _currentIndex) return;
		_answers[doshaKey] = (_answers[doshaKey] ?? 0) + 1;
		_answeredCount += 1;
		if (_answeredCount >= 10) {
			calculateResult();
			return;
		}
		_currentIndex = (_currentIndex + 1).clamp(0, _questions.length - 1);
		emit(PrakritiQuestionsLoaded(_questions, _currentIndex, Map<String, int>.from(_answers)));
	}

	void calculateResult() {
		final vata = _answers['vata'] ?? 0;
		final pitta = _answers['pitta'] ?? 0;
		final kapha = _answers['kapha'] ?? 0;
		final total = (vata + pitta + kapha).toDouble();
		final vPercent = total == 0 ? 33.3 : (vata / total) * 100;
		final pPercent = total == 0 ? 33.3 : (pitta / total) * 100;
		final kPercent = total == 0 ? 33.4 : (kapha / total) * 100;
		final scores = {'vata': vPercent, 'pitta': pPercent, 'kapha': kPercent};
		final dominant = scores.entries.reduce((a, b) => a.value > b.value ? a : b).key;

		final profile = {
			'vata_score': vata.toDouble(),
			'pitta_score': pitta.toDouble(),
			'kapha_score': kapha.toDouble(),
			'vata_percent': double.parse(vPercent.toStringAsFixed(1)),
			'pitta_percent': double.parse(pPercent.toStringAsFixed(1)),
			'kapha_percent': double.parse(kPercent.toStringAsFixed(1)),
			'dominant_dosha': dominant,
			'risk_score': double.parse((100 - scores[dominant]!).toStringAsFixed(1)),
			'constitutional_risk_score': double.parse((100 - scores[dominant]!).toStringAsFixed(1)),
			'completed_at': DateTime.now().toIso8601String(),
		};

		emit(PrakritiQuestionsLoaded(_questions, _currentIndex, Map<String, int>.from(_answers), complete: true));
		emit(PrakritiCompleted(profile));
	}

	Future<void> saveProfile(Map profile) async {
		emit(PrakritiLoading());
		try {
			final payload = {
				'vata_score': (profile['vata_score'] ?? 0).toDouble(),
				'pitta_score': (profile['pitta_score'] ?? 0).toDouble(),
				'kapha_score': (profile['kapha_score'] ?? 0).toDouble(),
				'dominant_dosha': profile['dominant_dosha'],
				'risk_score': (profile['risk_score'] ?? 0).toDouble(),
			};
			await _api.post('/prakriti/profile', payload);
			await HiveService.savePrakritiProfile(Map<String, dynamic>.from(profile));
			emit(PrakritiCompleted(Map<String, dynamic>.from(profile)));
		} catch (e) {
			emit(PrakritiError('Failed to save profile: $e'));
		}
	}

	Future<void> loadProfile() async {
		emit(PrakritiLoading());
		try {
			final local = HiveService.getPrakritiProfile();
			if (local != null) {
				emit(PrakritiCompleted(local));
				return;
			}
			final remote = await _api.get('/prakriti/profile');
			await HiveService.savePrakritiProfile(Map<String, dynamic>.from(remote as Map));
			emit(PrakritiCompleted(Map<String, dynamic>.from(remote)));
		} catch (e) {
			emit(PrakritiError('Failed to load profile: $e'));
		}
	}
}
