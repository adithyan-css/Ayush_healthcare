import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../core/i18n/language_map.dart';
import '../../data/repositories/forecast_repository.dart';
import '../cubits/heatmap_cubit.dart';

class StateDetailScreen extends StatefulWidget {
  const StateDetailScreen({super.key, required this.stateId});

  final String stateId;

  @override
  State<StateDetailScreen> createState() => _StateDetailScreenState();
}

class _StateDetailScreenState extends State<StateDetailScreen> {
  bool _xaiLoading = true;
  List<String> _xaiReasons = <String>[];
  final ForecastRepository _forecastRepository = ForecastRepository();

  @override
  void initState() {
    super.initState();
    _loadStateAndExplain();
  }

  Future<void> _loadStateAndExplain() async {
    await context.read<HeatmapCubit>().selectState(widget.stateId);
    await _loadXaiReasons();
  }

  Future<void> _loadXaiReasons() async {
    try {
      final List<String> reasons = await _forecastRepository.explain(widget.stateId);
      if (!mounted) {
        return;
      }
      setState(() {
        _xaiReasons = reasons;
        _xaiLoading = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _xaiReasons = <String>[];
        _xaiLoading = false;
      });
    }
  }

  Color _riskColor(String level) {
    switch (level.toLowerCase()) {
      case 'critical':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'medium':
        return Colors.amber;
      default:
        return Colors.green;
    }
  }

  IconData _trendIcon(String trend) {
    switch (trend.toLowerCase()) {
      case 'rising':
        return Icons.trending_up;
      case 'falling':
        return Icons.trending_down;
      default:
        return Icons.trending_flat;
    }
  }

  List<String> _fallbackTips(String condition) {
    final String c = condition.toLowerCase();
    if (c.contains('respiratory')) {
      return <String>[
        'Steam inhalation with tulsi or ajwain once daily',
        'Practice Anulom Vilom for 10 minutes each morning',
        'Avoid exposure to dust and sudden cold air',
      ];
    }
    if (c.contains('digestive')) {
      return <String>[
        'Use warm cumin-fennel water after meals',
        'Eat freshly cooked light meals and avoid stale food',
        'Maintain regular meal timings to support Agni',
      ];
    }
    if (c.contains('joint')) {
      return <String>[
        'Do gentle abhyanga with warm sesame oil',
        'Include dry ginger in diet in moderation',
        'Practice low-impact mobility stretches daily',
      ];
    }
    return <String>[
      'Keep hydration and sleep routine consistent',
      'Use seasonal AYUSH herbs under guidance',
      'Practice pranayama daily for resilience',
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('${context.t('state_detail')} - ${widget.stateId}')),
      body: BlocBuilder<HeatmapCubit, HeatmapState>(
        builder: (BuildContext context, HeatmapState state) {
          if (state is HeatmapError) {
            return Center(child: Text(state.msg));
          }

          if (state is! StateSelected || _xaiLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final Map<String, dynamic> detail = state.detail;
          final String stateName = (detail['state_name'] ?? widget.stateId).toString();
          final String riskLevel = (detail['risk_level'] ?? 'low').toString();
          final String trend = (detail['trend'] ?? 'stable').toString();
          final String topCondition = (detail['top_condition'] ?? 'General').toString();

          final List<dynamic> monthlyRaw = detail['monthly_cases'] is List
              ? List<dynamic>.from(detail['monthly_cases'] as List)
              : <dynamic>[];
          final List<double> monthlyValues = monthlyRaw.map((dynamic e) => (e as num).toDouble()).toList();

          final Map<String, dynamic> seasonsMap = detail['seasons_map'] is Map
              ? Map<String, dynamic>.from(detail['seasons_map'] as Map)
              : <String, dynamic>{};

          final List<String> ayushTips = (detail['ayush_tips'] is List)
              ? List<dynamic>.from(detail['ayush_tips'] as List).map((dynamic e) => e.toString()).toList()
              : _fallbackTips(topCondition);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        stateName,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                    ),
                    Chip(
                      label: Text(riskLevel.toUpperCase()),
                      backgroundColor: _riskColor(riskLevel).withValues(alpha: 0.16),
                      side: BorderSide(color: _riskColor(riskLevel)),
                    ),
                    const SizedBox(width: 8),
                    Icon(_trendIcon(trend), color: _riskColor(riskLevel)),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: <Widget>[
                    Chip(label: Text(topCondition)),
                    ...seasonsMap.values.map((dynamic e) => Chip(label: Text(e.toString()))),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  height: 180,
                  child: LineChart(
                    LineChartData(
                      lineBarsData: <LineChartBarData>[
                        LineChartBarData(
                          spots: List<FlSpot>.generate(
                            monthlyValues.length,
                            (int index) => FlSpot((index + 1).toDouble(), monthlyValues[index]),
                          ),
                          isCurved: true,
                          barWidth: 3,
                          color: _riskColor(riskLevel),
                          dotData: const FlDotData(show: true),
                        ),
                      ],
                      minX: 1,
                      maxX: 6,
                      gridData: const FlGridData(show: true),
                      borderData: FlBorderData(show: false),
                      titlesData: FlTitlesData(
                        rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            getTitlesWidget: (double value, TitleMeta meta) => Text('M${value.toInt()}'),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text('AYUSH Tips', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                ...ayushTips.take(3).map(
                      (String tip) => Card(
                        child: ListTile(
                          leading: const Icon(Icons.eco),
                          title: Text(tip),
                        ),
                      ),
                    ),
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(context.t('xai_reasoning_steps'), style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        if (_xaiReasons.isEmpty)
                          Text(context.t('no_explanation_available'))
                        else
                          ..._xaiReasons.asMap().entries.map(
                                (MapEntry<int, String> entry) => Padding(
                                  padding: const EdgeInsets.only(bottom: 8),
                                  child: Container(
                                    width: double.infinity,
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: Colors.blueGrey.withValues(alpha: 0.08),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: <Widget>[
                                        CircleAvatar(
                                          radius: 12,
                                          child: Text('${entry.key + 1}', style: const TextStyle(fontSize: 12)),
                                        ),
                                        const SizedBox(width: 8),
                                        Expanded(child: Text(entry.value)),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
