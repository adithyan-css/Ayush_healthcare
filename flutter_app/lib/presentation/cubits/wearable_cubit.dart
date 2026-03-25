import 'dart:math';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/repositories/wearable_repository.dart';

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

	final WearableRepository _repo = WearableRepository();

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

			try {
				await _repo.syncReadings(readings.cast<Map<String, dynamic>>());
				final Map<String, dynamic> backendDiagnosis = await _repo.nadi();
				await _repo.trend(days: 30);
				await _repo.anomalies();
				emit(WearableLoaded(readings, backendDiagnosis.isNotEmpty ? backendDiagnosis : diagnosis));
				return;
			} catch (_) {}

			emit(WearableLoaded(readings, diagnosis));
		} catch (e) {
			emit(WearableError('Failed to fetch wearable data: $e'));
		}
	}

	Future<void> syncToBackend(List readings) async {
		try {
			await _repo.syncReadings(readings.cast<Map<String, dynamic>>());
		} catch (e) {
			emit(WearableError('Failed to sync backend: $e'));
		}
	}

	Future<void> loadNadi() async {
		if (state is! WearableLoaded) return;
		final current = state as WearableLoaded;
		try {
			final Map<String, dynamic> data = await _repo.nadi();
			emit(WearableLoaded(current.readings, data));
		} catch (e) {
			emit(WearableError('Failed to load nadi diagnosis: $e'));
		}
	}
}
