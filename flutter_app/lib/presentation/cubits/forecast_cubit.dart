import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:printing/printing.dart';
import '../../data/repositories/forecast_repository.dart';

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

	final ForecastRepository _repo = ForecastRepository();

	Future<void> loadForecast() async {
		emit(ForecastLoading());
		try {
			final Map<String, dynamic> merged = await _repo.loadDashboard();
			emit(ForecastLoaded(merged));
		} catch (e) {
			final cached = _repo.getCachedDashboard();
			if (cached != null) {
				emit(ForecastLoaded(cached));
			} else {
				emit(ForecastError('Failed to load forecast: $e'));
			}
		}
	}

	Future<void> generateBulletin(String districtId) async {
		try {
			final Map<String, dynamic> data = await _repo.bulletin(districtId);
			final String b64 = (data['pdf_base64'] ?? '').toString();
			if (b64.isEmpty) throw Exception('Empty PDF');
			final bytes = base64Decode(b64);
			await Printing.sharePdf(bytes: Uint8List.fromList(bytes), filename: 'prakriti_bulletin_$districtId.pdf');
		} catch (e) {
			emit(ForecastError('Failed to generate bulletin: $e'));
		}
	}
}
