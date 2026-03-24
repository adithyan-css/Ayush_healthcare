import 'package:flutter_bloc/flutter_bloc.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';

abstract class RecommendationState {}

class RecommendationInitial extends RecommendationState {}

class RecommendationLoading extends RecommendationState {}

class RecommendationLoaded extends RecommendationState {
	final Map<String, dynamic> data;
	RecommendationLoaded(this.data);
}

class RecommendationError extends RecommendationState {
	final String msg;
	RecommendationError(this.msg);
}

class RecommendationCubit extends Cubit<RecommendationState> {
	RecommendationCubit() : super(RecommendationInitial());

	final ApiService _api = ApiService.instance;
	List<String> selectedSymptoms = [];

	void toggleSymptom(String symptom) {
		if (selectedSymptoms.contains(symptom)) {
			selectedSymptoms.remove(symptom);
		} else {
			selectedSymptoms.add(symptom);
		}

		if (state is RecommendationLoaded) {
			final current = Map<String, dynamic>.from((state as RecommendationLoaded).data);
			current['selectedSymptoms'] = List<String>.from(selectedSymptoms);
			emit(RecommendationLoaded(current));
		} else {
			emit(RecommendationLoaded({'selectedSymptoms': List<String>.from(selectedSymptoms)}));
		}
	}

	Future<void> generateRecommendation(String? freeText) async {
		emit(RecommendationLoading());
		try {
			final data = await _api.post('/recommendations/generate', {
				'symptoms': selectedSymptoms,
				'free_text': freeText,
			});
			final mapped = Map<String, dynamic>.from(data as Map);
			await HiveService.saveSession(mapped);
			await HiveService.clearOldSessions();
			emit(RecommendationLoaded(mapped));
		} catch (e) {
			emit(RecommendationError('Failed to generate recommendation: $e'));
		}
	}

	Future<List<dynamic>> loadHistory() async {
		try {
			final history = await _api.get('/recommendations/history');
			return history as List<dynamic>;
		} catch (_) {
			return HiveService.getSessions();
		}
	}

	Future<void> regenerate() async {
		await generateRecommendation(null);
	}
}
