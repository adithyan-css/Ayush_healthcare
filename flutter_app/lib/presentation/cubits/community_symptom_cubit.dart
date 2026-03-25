import 'package:flutter_bloc/flutter_bloc.dart';

import '../../services/api_service.dart';

abstract class CommunitySymptomState {}

class CommunitySymptomInitial extends CommunitySymptomState {}

class CommunitySymptomLoading extends CommunitySymptomState {}

class CommunitySymptomLoaded extends CommunitySymptomState {
	CommunitySymptomLoaded(this.items);

	final List<Map<String, dynamic>> items;
}

class CommunitySymptomSuccess extends CommunitySymptomState {
	CommunitySymptomSuccess(this.message);

	final String message;
}

class CommunitySymptomError extends CommunitySymptomState {
	CommunitySymptomError(this.message);

	final String message;
}

class CommunitySymptomCubit extends Cubit<CommunitySymptomState> {
	CommunitySymptomCubit() : super(CommunitySymptomInitial());

	final ApiService _api = ApiService.instance;

	List<Map<String, dynamic>> _extractList(dynamic response) {
		if (response is Map<String, dynamic>) {
			final dynamic data = response['data'];
			if (data is List) {
				return data
					.whereType<Map>()
					.map((Map item) => Map<String, dynamic>.from(item))
					.toList(growable: false);
			}
		}
		return <Map<String, dynamic>>[];
	}

	Future<void> loadCommunity() async {
		emit(CommunitySymptomLoading());
		try {
			final dynamic response = await _api.get('/symptoms/community');
			emit(CommunitySymptomLoaded(_extractList(response)));
		} catch (e) {
			emit(CommunitySymptomError('Unable to load community symptoms: $e'));
		}
	}

	Future<void> reportSymptoms(List<String> symptoms, {double? latitude, double? longitude}) async {
		if (symptoms.isEmpty) {
			emit(CommunitySymptomError('Select at least one symptom'));
			return;
		}
		emit(CommunitySymptomLoading());
		try {
			await _api.post('/symptoms/report', {
				'symptoms': symptoms,
				'latitude': latitude,
				'longitude': longitude,
			});
			emit(CommunitySymptomSuccess('Community symptom report submitted'));
		} catch (e) {
			emit(CommunitySymptomError('Unable to submit symptom report: $e'));
		}
	}
}
