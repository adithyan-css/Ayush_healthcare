import 'dart:math';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../services/api_service.dart';

abstract class WearableState {}

class WearableInitial extends WearableState {}

class WearablePermissionDenied extends WearableState {}

class WearableLoading extends WearableState {}

class WearableLoaded extends WearableState {
	final List<Map<String, dynamic>> readings;
	final Map<String, dynamic> nadiDiagnosis;
	WearableLoaded(this.readings, this.nadiDiagnosis);
}

class WearableError extends WearableState {
	final String msg;
	WearableError(this.msg);
}

class WearableCubit extends Cubit<WearableState> {
	WearableCubit() : super(WearableInitial());

	final ApiService _api = ApiService.instance;

	Future<void> checkAndFetch() async {
		emit(WearableLoading());
		try {
			final random = Random();
			final now = DateTime.now();
			final readings = List.generate(7, (index) {
				return {
					'date': now.subtract(Duration(days: 6 - index)).toIso8601String(),
					'hrv_ms': (25 + random.nextDouble() * 50),
				};
			});

			// Replace with real health package calls when running on device.
			final avg = readings.map((e) => e['hrv_ms'] as double).reduce((a, b) => a + b) / readings.length;
			final nadi = avg > 50
					? 'vata_nadi'
					: avg >= 30
							? 'pitta_nadi'
							: 'kapha_nadi';
			final diagnosis = {
				'type': nadi,
				'hrv_ms': double.parse(avg.toStringAsFixed(2)),
				'stress_index': double.parse((500 / avg).toStringAsFixed(2)),
				'is_anomaly': readings.last['hrv_ms'] as double > 70,
			};

			emit(WearableLoaded(readings, diagnosis));
		} catch (e) {
			emit(WearableError('Failed to fetch wearable data: $e'));
		}
	}

	Future<void> syncToBackend(List readings) async {
		try {
			await _api.post('/wearable/hrv-sync', {'readings': readings});
		} catch (e) {
			emit(WearableError('Failed to sync backend: $e'));
		}
	}

	Future<void> loadNadi() async {
		if (state is! WearableLoaded) return;
		final current = state as WearableLoaded;
		try {
			final data = await _api.get('/wearable/nadi');
			emit(WearableLoaded(current.readings, Map<String, dynamic>.from(data as Map)));
		} catch (e) {
			emit(WearableError('Failed to load nadi diagnosis: $e'));
		}
	}
}
