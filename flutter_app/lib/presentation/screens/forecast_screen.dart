import 'dart:convert';
import 'dart:typed_data';

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:printing/printing.dart';

import '../../core/i18n/language_map.dart';
import '../../services/api_service.dart';
import '../cubits/forecast_cubit.dart';

class ForecastScreen extends StatefulWidget {
  const ForecastScreen({super.key});

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  static const Map<String, Color> _lineColors = <String, Color>{
    'Respiratory': Colors.blue,
    'Digestive': Colors.orange,
    'Fever/Viral': Colors.red,
    'Skin': Colors.green,
    'Joint': Colors.purple,
  };

  @override
  void initState() {
    super.initState();
    context.read<ForecastCubit>().loadForecast();
  }

  Future<void> _generateBulletin() async {
    try {
      final dynamic response = await ApiService.instance.post('/forecast/bulletin', <String, dynamic>{'district_id': 'MH'});
      final String b64 = (response['pdf_base64'] ?? '').toString();
      if (b64.isEmpty) {
        if (!mounted) {
          return;
        }
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Bulletin generated successfully')));
        return;
      }

      final Uint8List bytes = Uint8List.fromList(base64Decode(b64));
      await Printing.sharePdf(bytes: bytes, filename: 'prakriti_bulletin_MH.pdf');
    } catch (_) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Unable to generate bulletin right now')));
    }
  }

  Color _severityColor(String severity) {
    switch (severity.toLowerCase()) {
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

  Color _barColor(num value) {
    if (value > 70) {
      return Colors.red;
    }
    if (value >= 50) {
      return Colors.orange;
    }
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
			appBar: AppBar(title: Text(context.t('forecast'))),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _generateBulletin,
        icon: const Icon(Icons.picture_as_pdf),
        label: Text(context.t('bulletin')),
      ),
      body: BlocBuilder<ForecastCubit, ForecastState>(
        builder: (BuildContext context, ForecastState state) {
          if (state is ForecastInitial || state is ForecastLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is ForecastError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  Text(state.msg, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => context.read<ForecastCubit>().loadForecast(),
                    child: Text(context.t('retry')),
                  ),
                ],
              ),
            );
          }

          if (state is! ForecastLoaded) {
            return const SizedBox.shrink();
          }

          final Map<String, dynamic> forecast = state.data;
          final Map<String, dynamic> conditions = Map<String, dynamic>.from(forecast['conditions'] as Map? ?? <String, dynamic>{});
          final List<Map<String, dynamic>> regionCards = ((forecast['region_cards'] as List<dynamic>? ?? <dynamic>[]))
              .map((dynamic item) => Map<String, dynamic>.from(item as Map))
              .toList();
          final Map<String, dynamic> populationRisks =
              Map<String, dynamic>.from(forecast['population_risks'] as Map? ?? <String, dynamic>{});
          final Map<String, dynamic> seasonal = Map<String, dynamic>.from(forecast['seasonal'] as Map? ?? <String, dynamic>{});

          final List<MapEntry<String, dynamic>> orderedLines = <MapEntry<String, dynamic>>[
            MapEntry<String, dynamic>('Respiratory', conditions['Respiratory'] ?? <dynamic>[]),
            MapEntry<String, dynamic>('Digestive', conditions['Digestive'] ?? <dynamic>[]),
            MapEntry<String, dynamic>('Fever/Viral', conditions['Fever/Viral'] ?? <dynamic>[]),
            MapEntry<String, dynamic>('Skin', conditions['Skin'] ?? <dynamic>[]),
            MapEntry<String, dynamic>('Joint', conditions['Joint'] ?? <dynamic>[]),
          ];

          final Map<String, num> orderedPopulation = <String, num>{
            'Children': (populationRisks['Children'] as num?) ?? 0,
            'Adults': (populationRisks['Adults'] as num?) ?? 0,
            'Elderly': (populationRisks['Elderly'] as num?) ?? 0,
            'Urban': (populationRisks['Urban'] as num?) ?? 0,
            'Rural': (populationRisks['Rural'] as num?) ?? 0,
          };

          return SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(14),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: <Color>[colorScheme.primaryContainer, colorScheme.surface],
                    ),
                  ),
                  child: Row(
                    children: <Widget>[
                      Icon(Icons.query_stats, color: colorScheme.primary),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          seasonal['advisory']?.toString() ?? 'Stay aligned with seasonal AYUSH lifestyle guidance.',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: orderedLines.map((MapEntry<String, dynamic> entry) {
                    final Color c = _lineColors[entry.key] ?? Colors.teal;
                    return Row(
                      mainAxisSize: MainAxisSize.min,
                      children: <Widget>[
                        Container(
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(color: c, shape: BoxShape.circle),
                        ),
                        const SizedBox(width: 5),
                        Text(entry.key),
                      ],
                    );
                  }).toList(),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  height: 220,
                  child: LineChart(
                    LineChartData(
                      minX: 1,
                      maxX: 30,
                      minY: 0,
                      lineBarsData: orderedLines.map((MapEntry<String, dynamic> entry) {
                        final List<double> values = (entry.value as List<dynamic>).map((dynamic v) => (v as num).toDouble()).toList();
                        return LineChartBarData(
                          spots: List<FlSpot>.generate(
                            values.length,
                            (int idx) => FlSpot((idx + 1).toDouble(), values[idx]),
                          ),
                          color: _lineColors[entry.key],
                          barWidth: 2.5,
                          isCurved: true,
                          dotData: const FlDotData(show: false),
                        );
                      }).toList(),
                      gridData: const FlGridData(show: true),
                      borderData: FlBorderData(show: false),
                      titlesData: FlTitlesData(
                        rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            interval: 5,
                            getTitlesWidget: (double value, TitleMeta meta) => Text(value.toInt().toString()),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: regionCards.length >= 4 ? 4 : regionCards.length,
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 1.25,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                  ),
                  itemBuilder: (BuildContext context, int index) {
                    final Map<String, dynamic> card = regionCards[index];
                    final String severity = (card['severity'] ?? 'low').toString();
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(10),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Text(
                              card['region']?.toString() ?? 'Region',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 4),
                            Text(card['condition']?.toString() ?? ''),
                            const Spacer(),
                            Text('Peaks in ${card['peak_in_days'] ?? '--'} days'),
                            const SizedBox(height: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: _severityColor(severity).withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                severity.toUpperCase(),
                                style: TextStyle(color: _severityColor(severity), fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16),
                SizedBox(
                  height: 160,
                  child: BarChart(
                    BarChartData(
                      gridData: const FlGridData(show: true),
                      borderData: FlBorderData(show: false),
                      barGroups: orderedPopulation.entries.toList().asMap().entries.map((MapEntry<int, MapEntry<String, num>> e) {
                        return BarChartGroupData(
                          x: e.key,
                          barRods: <BarChartRodData>[
                            BarChartRodData(
                              toY: e.value.value.toDouble(),
                              width: 18,
                              color: _barColor(e.value.value),
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ],
                        );
                      }).toList(),
                      titlesData: FlTitlesData(
                        rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            getTitlesWidget: (double value, TitleMeta meta) {
                              final int index = value.toInt();
                              final List<String> labels = orderedPopulation.keys.toList();
                              if (index < 0 || index >= labels.length) {
                                return const SizedBox.shrink();
                              }
                              return Text(labels[index], style: const TextStyle(fontSize: 10));
                            },
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.wb_sunny),
                    title: Text(context.t('seasonal_advisory')),
                    subtitle: Text(seasonal['advisory']?.toString() ?? 'Stay aligned with seasonal AYUSH lifestyle guidance.'),
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
