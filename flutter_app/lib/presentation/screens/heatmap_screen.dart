import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../core/i18n/language_map.dart';
import '../cubits/heatmap_cubit.dart';

class HeatmapScreen extends StatefulWidget {
  const HeatmapScreen({super.key});

  @override
  State<HeatmapScreen> createState() => _HeatmapScreenState();
}

class _HeatmapScreenState extends State<HeatmapScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;

  String _selectedCondition = 'All';
  String _selectedSeason = 'All';
  List<Map<String, dynamic>> _allDistricts = <Map<String, dynamic>>[];

  static const List<String> _conditionOptions = <String>[
    'All',
    'Respiratory',
    'Digestive',
    'Fever-Viral',
    'Skin',
    'Joint',
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    context.read<HeatmapCubit>().loadHeatmapData();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Color _riskColor(String level) {
    switch (level.toLowerCase()) {
      case 'critical':
        return Colors.red.withValues(alpha: 0.7);
      case 'high':
        return Colors.orange.withValues(alpha: 0.6);
      case 'medium':
        return Colors.yellow.shade700.withValues(alpha: 0.5);
      default:
        return Colors.green.withValues(alpha: 0.4);
    }
  }

  String _normalizeCondition(String value) {
    if (value.toLowerCase() == 'fever-viral') {
      return 'fever/viral';
    }
    return value.toLowerCase();
  }

  List<Map<String, dynamic>> _filteredDistricts() {
    return _allDistricts.where((Map<String, dynamic> district) {
      final String topCondition = (district['top_condition'] ?? '').toString().toLowerCase();
      final Map<String, dynamic> seasons = district['seasons_map'] is Map
          ? Map<String, dynamic>.from(district['seasons_map'] as Map)
          : <String, dynamic>{};

      final bool conditionOk = _selectedCondition == 'All' || topCondition == _normalizeCondition(_selectedCondition);
      final bool seasonOk = _selectedSeason == 'All' || seasons.containsKey(_selectedSeason.toLowerCase());

      return conditionOk && seasonOk;
    }).toList(growable: false);
  }

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
			appBar: AppBar(title: Text(context.t('disease_heatmap'))),
      body: BlocBuilder<HeatmapCubit, HeatmapState>(
        builder: (BuildContext context, HeatmapState state) {
          if (state is HeatmapLoaded) {
            _allDistricts = List<Map<String, dynamic>>.from(state.districts);
          }

          final List<Map<String, dynamic>> districts = _filteredDistricts();

          return Stack(
            children: <Widget>[
              FlutterMap(
                options: const MapOptions(
                  initialCenter: LatLng(20.5937, 78.9629),
                  initialZoom: 5,
                ),
                children: <Widget>[
                  TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
                  AnimatedBuilder(
                    animation: _pulseController,
                    builder: (_, __) {
                      return CircleLayer(
                        circles: districts.map((Map<String, dynamic> district) {
                          final double lat = (district['latitude'] as num?)?.toDouble() ?? 20.5937;
                          final double lng = (district['longitude'] as num?)?.toDouble() ?? 78.9629;
                          final bool rising = (district['trend'] ?? '').toString().toLowerCase() == 'rising';
                          final double radius = rising ? (40 + (_pulseController.value * 15)) : 40;

                          return CircleMarker(
                            point: LatLng(lat, lng),
                            radius: radius,
                            color: _riskColor((district['risk_level'] ?? 'low').toString()),
                            borderStrokeWidth: 1.3,
                            borderColor: Colors.white70,
                          );
                        }).toList(growable: false),
                      );
                    },
                  ),
                  MarkerLayer(
                    markers: districts.map((Map<String, dynamic> district) {
                      final double lat = (district['latitude'] as num?)?.toDouble() ?? 20.5937;
                      final double lng = (district['longitude'] as num?)?.toDouble() ?? 78.9629;
                      final String stateCode = (district['state_code'] ?? '').toString();

                      return Marker(
                        point: LatLng(lat, lng),
                        width: 90,
                        height: 90,
                        child: GestureDetector(
                          onTap: () {
                            context.push('/state-detail', extra: stateCode);
                          },
                          child: const SizedBox.expand(),
                        ),
                      );
                    }).toList(growable: false),
                  ),
                ],
              ),
              if (state is HeatmapLoading)
                const Center(child: CircularProgressIndicator()),
              if (state is HeatmapError)
                Align(
                  alignment: Alignment.topCenter,
                  child: Container(
                    margin: const EdgeInsets.all(12),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.red.shade100,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(state.msg),
                  ),
                ),
              Align(
                alignment: Alignment.bottomCenter,
                child: Container(
                  height: 96,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: colorScheme.surface,
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                    boxShadow: <BoxShadow>[
                      BoxShadow(color: Colors.black.withValues(alpha: 0.12), blurRadius: 10),
                    ],
                  ),
                  child: Row(
                    children: <Widget>[
                      Expanded(
                        child: DropdownButtonFormField<String>(
							initialValue: _selectedCondition,
                          isDense: true,
                          decoration: InputDecoration(labelText: context.t('condition')),
                          items: _conditionOptions
                              .map((String option) => DropdownMenuItem<String>(value: option, child: Text(option)))
                              .toList(),
                          onChanged: (String? value) {
                            if (value == null) {
                              return;
                            }
                            setState(() {
                              _selectedCondition = value;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: SegmentedButton<String>(
                          segments: const <ButtonSegment<String>>[
                            ButtonSegment<String>(value: 'All', label: Text('All')),
                            ButtonSegment<String>(value: 'Winter', label: Text('Winter')),
                            ButtonSegment<String>(value: 'Summer', label: Text('Summer')),
                            ButtonSegment<String>(value: 'Monsoon', label: Text('Monsoon')),
                            ButtonSegment<String>(value: 'Autumn', label: Text('Autumn')),
                          ],
                          selected: <String>{_selectedSeason},
                          onSelectionChanged: (Set<String> value) {
                            setState(() {
                              _selectedSeason = value.first;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
