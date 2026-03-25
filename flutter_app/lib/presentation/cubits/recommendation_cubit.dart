import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/repositories/recommendation_repository.dart';

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

	final RecommendationRepository _repo = RecommendationRepository();
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
			final Map<String, dynamic> mapped = await _repo.generate(symptoms: selectedSymptoms, freeText: freeText);
			emit(RecommendationLoaded(mapped));
		} catch (e) {
			emit(RecommendationError('Failed to generate recommendation: $e'));
		}
	}

	Future<List<dynamic>> loadHistory() async {
		try {
			return await _repo.history();
		} catch (_) {
			return <dynamic>[];
		}
	}

	Future<void> regenerate() async {
		await generateRecommendation(null);
	}
}
