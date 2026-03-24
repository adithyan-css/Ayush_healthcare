import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../services/api_service.dart';
import '../../services/hive_service.dart';

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

  final ApiService _api = ApiService.instance;

  List<Map<String, dynamic>> _lastLoaded = <Map<String, dynamic>>[];

  Future<void> loadHeatmapData() async {
    emit(HeatmapLoading());
    try {
      final dynamic response = await _api.get('/heatmap/districts');
      final List<Map<String, dynamic>> districts = _toDistrictList(response);
      if (districts.isNotEmpty) {
        await HiveService.saveDistrictRisks(districts);
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
      final List<Map<String, dynamic>>? cached = HiveService.getDistrictRisks();
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
      List<Map<String, dynamic>> source = _lastLoaded;
      if (source.isEmpty) {
        final List<Map<String, dynamic>>? cached = HiveService.getDistrictRisks();
        source = cached ?? <Map<String, dynamic>>[];
      }
      if (source.isEmpty) {
        await loadHeatmapData();
        if (state is HeatmapLoaded) {
          source = List<Map<String, dynamic>>.from((state as HeatmapLoaded).districts);
        }
      }

      final String c = condition.toLowerCase();
      final String s = season.toLowerCase();

      final List<Map<String, dynamic>> filtered = source.where((Map<String, dynamic> district) {
        final String topCondition = (district['top_condition'] ?? '').toString().toLowerCase();
        final Map<String, dynamic> seasons = (district['seasons_map'] is Map)
            ? Map<String, dynamic>.from(district['seasons_map'] as Map)
            : <String, dynamic>{};
        final bool conditionOk = c == 'all' || topCondition == c;
        final bool seasonOk = s == 'all' || seasons.containsKey(s);
        return conditionOk && seasonOk;
      }).toList(growable: false);

      emit(HeatmapLoaded(filtered));
    } catch (e) {
      emit(HeatmapError('Failed to apply filter: $e'));
    }
  }

  Future<void> selectState(String stateId) async {
    emit(HeatmapLoading());
    try {
      final dynamic response = await _api.get('/heatmap/state/$stateId');
      final Map<String, dynamic> detail = response is Map<String, dynamic>
          ? Map<String, dynamic>.from((response['data'] ?? response) as Map)
          : <String, dynamic>{};
      emit(StateSelected(detail));
    } catch (e) {
      emit(HeatmapError('Failed to load state details: $e'));
    }
  }

  List<Map<String, dynamic>> _toDistrictList(dynamic response) {
    if (response is Map<String, dynamic>) {
      final dynamic data = response['data'];
      if (data is List) {
        return data
            .map((dynamic item) => Map<String, dynamic>.from(item as Map))
            .toList(growable: false);
      }
    }
    if (response is List) {
      return response
          .map((dynamic item) => Map<String, dynamic>.from(item as Map))
          .toList(growable: false);
    }
    return <Map<String, dynamic>>[];
  }
}
