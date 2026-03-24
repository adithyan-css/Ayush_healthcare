import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:printing/printing.dart';
import '../../services/api_service.dart';
import '../../services/hive_service.dart';

abstract class ForecastState {}

class ForecastInitial extends ForecastState {}

class ForecastLoading extends ForecastState {}

class ForecastLoaded extends ForecastState {
	final Map<String, dynamic> data;
	ForecastLoaded(this.data);
}

class ForecastError extends ForecastState {
	final String msg;
	ForecastError(this.msg);
}

class ForecastCubit extends Cubit<ForecastState> {
	ForecastCubit() : super(ForecastInitial());

	final ApiService _api = ApiService.instance;

	dynamic _extractData(dynamic response) {
		if (response is Map<String, dynamic>) {
			return response['data'] ?? response;
		}
		return response;
	}

	Future<void> loadForecast() async {
		emit(ForecastLoading());
		try {
			final results = await Future.wait([
				_api.get('/forecast/national'),
				_api.get('/forecast/regions'),
				_api.get('/forecast/population'),
				_api.get('/forecast/seasonal'),
			]);

			final dynamic national = _extractData(results[0]);
			final dynamic regions = _extractData(results[1]);
			final dynamic population = _extractData(results[2]);
			final dynamic seasonal = _extractData(results[3]);

			final merged = {
				'conditions': (national as Map)['conditions'],
				'region_cards': regions,
				'population_risks': population,
				'seasonal': seasonal,
			};
			await HiveService.saveForecast(Map<String, dynamic>.from(merged));
			emit(ForecastLoaded(Map<String, dynamic>.from(merged)));
		} catch (e) {
			final cached = HiveService.getForecast();
			if (cached != null) {
				emit(ForecastLoaded(cached));
			} else {
				emit(ForecastError('Failed to load forecast: $e'));
			}
		}
	}

	Future<void> generateBulletin(String districtId) async {
		try {
			final response = await _api.post('/forecast/bulletin', {'district_id': districtId});
			final dynamic data = _extractData(response);
			final b64 = ((data is Map ? data['pdf_base64'] : null) ?? '').toString();
			if (b64.isEmpty) throw Exception('Empty PDF');
			final bytes = base64Decode(b64);
			await Printing.sharePdf(bytes: Uint8List.fromList(bytes), filename: 'prakriti_bulletin_$districtId.pdf');
		} catch (e) {
			emit(ForecastError('Failed to generate bulletin: $e'));
		}
	}
}
