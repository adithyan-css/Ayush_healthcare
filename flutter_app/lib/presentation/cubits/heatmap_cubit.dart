import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../data/repositories/heatmap_repository.dart';

abstract class HeatmapState {}

class HeatmapInitial extends HeatmapState {}

class HeatmapLoading extends HeatmapState {}

class HeatmapLoaded extends HeatmapState {
  HeatmapLoaded(this.districts);

  final List<Map<String, dynamic>> districts;
}

class StateSelected extends HeatmapState {
  StateSelected(this.detail);

  final Map<String, dynamic> detail;
}

class HeatmapError extends HeatmapState {
  HeatmapError(this.msg);

  final String msg;
}

class HeatmapCubit extends Cubit<HeatmapState> {
  HeatmapCubit() : super(HeatmapInitial());

  final HeatmapRepository _repo = HeatmapRepository();

  List<Map<String, dynamic>> _lastLoaded = <Map<String, dynamic>>[];

  Future<void> loadHeatmapData() async {
    emit(HeatmapLoading());
    try {
      final List<Map<String, dynamic>> districts = await _repo.districts();
      if (districts.isNotEmpty) {
        _lastLoaded = districts;
        emit(HeatmapLoaded(districts));
        return;
      }
      throw Exception('Empty API payload');
    } on DioException {
      await _loadFallbackHierarchy();
    } catch (_) {
      await _loadFallbackHierarchy();
    }
  }

  Future<void> _loadFallbackHierarchy() async {
    try {
      final List<Map<String, dynamic>>? cached = _repo.cachedDistricts();
      if (cached != null && cached.isNotEmpty) {
        _lastLoaded = List<Map<String, dynamic>>.from(cached);
        emit(HeatmapLoaded(_lastLoaded));
        return;
      }
      await loadFromAssets();
    } catch (_) {
      await loadFromAssets();
    }
  }

  Future<void> loadFromAssets() async {
    try {
      final String raw = await rootBundle.loadString('assets/data/district_risk.json');
      final List<dynamic> decoded = jsonDecode(raw) as List<dynamic>;
      final List<Map<String, dynamic>> districts = decoded
          .map((dynamic item) => Map<String, dynamic>.from(item as Map))
          .toList(growable: false);
      _lastLoaded = districts;
      emit(HeatmapLoaded(districts));
    } catch (e) {
      emit(HeatmapError('Failed to load heatmap data: $e'));
    }
  }

  Future<void> applyFilter(String condition, String season) async {
    try {
      final List<Map<String, dynamic>> filtered = await _repo.districts(condition: condition, season: season);
      _lastLoaded = filtered;
      emit(HeatmapLoaded(filtered));
    } catch (e) {
      emit(HeatmapError('Failed to apply filter: $e'));
    }
  }

  Future<void> selectState(String stateId) async {
    emit(HeatmapLoading());
    try {
      final Map<String, dynamic> detail = await _repo.stateDetail(stateId);
      emit(StateSelected(detail));
    } catch (e) {
      emit(HeatmapError('Failed to load state details: $e'));
    }
  }
}
