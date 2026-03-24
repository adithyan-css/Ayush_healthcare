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

	Map<String, dynamic> _extractDataMap(dynamic response) {
		if (response is Map<String, dynamic>) {
			final dynamic data = response['data'];
			if (data is Map<String, dynamic>) {
				return data;
			}
			return response;
		}
		return <String, dynamic>{};
	}

	List<dynamic> _extractDataList(dynamic response) {
		if (response is Map<String, dynamic>) {
			final dynamic data = response['data'];
			if (data is List) {
				return data;
			}
		}
		if (response is List) {
			return response;
		}
		return <dynamic>[];
	}

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
			final dynamic response = await _api.post('/recommendations/generate', {
				'symptoms': selectedSymptoms,
				'free_text': freeText,
			});
			final mapped = _extractDataMap(response);
			await HiveService.saveSession(mapped);
			await HiveService.clearOldSessions();
			emit(RecommendationLoaded(mapped));
		} catch (e) {
			emit(RecommendationError('Failed to generate recommendation: $e'));
		}
	}

	Future<List<dynamic>> loadHistory() async {
		try {
			final dynamic history = await _api.get('/recommendations/history');
			return _extractDataList(history);
		} catch (_) {
			return HiveService.getSessions();
		}
	}

	Future<void> regenerate() async {
		await generateRecommendation(null);
	}
}
