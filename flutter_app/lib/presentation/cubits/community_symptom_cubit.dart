import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/community_repository.dart';

abstract class CommunitySymptomState {}

class CommunitySymptomInitial extends CommunitySymptomState {}

class CommunitySymptomLoading extends CommunitySymptomState {}

class CommunitySymptomLoaded extends CommunitySymptomState {
	CommunitySymptomLoaded({
		required this.items,
		required this.hotspots,
		required this.alerts,
	});

	final List<Map<String, dynamic>> items;
	final List<Map<String, dynamic>> hotspots;
	final List<Map<String, dynamic>> alerts;
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

	final CommunityRepository _repo = CommunityRepository();

	Future<void> loadCommunity() async {
		emit(CommunitySymptomLoading());
		try {
			final List<Map<String, dynamic>> items = await _repo.community();
			final List<Map<String, dynamic>> hotspots = await _repo.hotspots();
			final List<Map<String, dynamic>> alerts = await _repo.alerts();
			emit(
				CommunitySymptomLoaded(
					items: items,
					hotspots: hotspots,
					alerts: alerts,
				),
			);
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
			await _repo.reportSymptoms(symptoms: symptoms, latitude: latitude, longitude: longitude);
			emit(CommunitySymptomSuccess('Community symptom report submitted'));
		} catch (e) {
			emit(CommunitySymptomError('Unable to submit symptom report: $e'));
		}
	}
}
