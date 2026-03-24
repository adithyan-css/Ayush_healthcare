import 'package:flutter_bloc/flutter_bloc.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';

abstract class HeatmapState {}

class HeatmapInitial extends HeatmapState {}

class HeatmapLoading extends HeatmapState {}

class HeatmapLoaded extends HeatmapState {
	final List<dynamic> districts;
	HeatmapLoaded(this.districts);
}

class StateSelected extends HeatmapState {
	final Map<String, dynamic> detail;
	final List<String> xaiReasons;
	StateSelected(this.detail, this.xaiReasons);
}

class HeatmapError extends HeatmapState {
	final String msg;
	HeatmapError(this.msg);
}

class HeatmapCubit extends Cubit<HeatmapState> {
	HeatmapCubit() : super(HeatmapInitial());

	final ApiService _api = ApiService.instance;

	Future<void> loadHeatmapData() async {
		emit(HeatmapLoading());
		try {
			final cached = HiveService.getDistrictRisks();
			final updatedAt = HiveService.getSetting('districtRiskUpdatedAt') as String?;
			final stale = updatedAt == null || DateTime.now().difference(DateTime.tryParse(updatedAt) ?? DateTime(1970)).inHours > 6;

			if (cached != null && cached.isNotEmpty && !stale) {
				emit(HeatmapLoaded(cached));
				return;
			}

			final data = await _api.get('/heatmap/districts') as List<dynamic>;
			await HiveService.saveDistrictRisks(data.map((e) => Map<String, dynamic>.from(e as Map)).toList());
			await HiveService.saveSettings('districtRiskUpdatedAt', DateTime.now().toIso8601String());
			emit(HeatmapLoaded(data));
		} catch (e) {
			emit(HeatmapError('Failed to load heatmap: $e'));
		}
	}

	Future<void> applyFilter(String condition, String season) async {
		emit(HeatmapLoading());
		try {
			final data = await _api.get('/heatmap/districts', queryParams: {'condition': condition, 'season': season}) as List<dynamic>;
			emit(HeatmapLoaded(data));
		} catch (e) {
			emit(HeatmapError('Failed to apply filter: $e'));
		}
	}

	Future<void> selectState(String stateId) async {
		emit(HeatmapLoading());
		try {
			final results = await Future.wait([
				_api.get('/heatmap/state/$stateId'),
				_api.get('/forecast/explain/$stateId'),
			]);
			final detail = Map<String, dynamic>.from(results[0] as Map);
			final explain = Map<String, dynamic>.from(results[1] as Map);
			final reasons = (explain['reasons'] as List<dynamic>? ?? []).map((e) => e.toString()).toList();
			emit(StateSelected(detail, reasons));
		} catch (e) {
			emit(HeatmapError('Failed to load state details: $e'));
		}
	}
}
