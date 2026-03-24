import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/i18n/language_map.dart';
import '../cubits/wearable_cubit.dart';

class NadiMonitorScreen extends StatefulWidget {
	const NadiMonitorScreen({super.key});

	@override
	State<NadiMonitorScreen> createState() => _NadiMonitorScreenState();
}

class _NadiMonitorScreenState extends State<NadiMonitorScreen> {
	@override
	void initState() {
		super.initState();
		context.read<WearableCubit>().checkAndFetch();
	}

	@override
	Widget build(BuildContext context) {
		final ColorScheme colorScheme = Theme.of(context).colorScheme;
		return Scaffold(
			appBar: AppBar(title: Text(context.t('nadi_monitor'))),
			body: BlocBuilder<WearableCubit, WearableState>(
				builder: (context, state) {
					if (state is WearableInitial || state is WearableLoading) {
						return const Center(
							child: Column(
								mainAxisSize: MainAxisSize.min,
								children: [
									CircularProgressIndicator(),
									SizedBox(height: 10),
									Text('Syncing HRV data...'),
								],
							),
						);
					}
					if (state is WearableError) return Center(child: Text(state.msg));
					if (state is! WearableLoaded) return const SizedBox.shrink();

					final readings = state.readings;
					final diagnosis = state.nadiDiagnosis;
					final avg = (diagnosis['hrv_ms'] ?? 0).toDouble();
					final anomaly = diagnosis['is_anomaly'] == true;

					final vataIntensity = (avg / 75).clamp(0.0, 1.0).toDouble();
					final pittaIntensity = (avg / 60).clamp(0.0, 1.0).toDouble();
					final kaphaIntensity = (avg / 45).clamp(0.0, 1.0).toDouble();

					return SingleChildScrollView(
						padding: const EdgeInsets.all(12),
						child: Column(
							crossAxisAlignment: CrossAxisAlignment.start,
							children: [
								Container(
									width: double.infinity,
									padding: const EdgeInsets.all(14),
									decoration: BoxDecoration(
										borderRadius: BorderRadius.circular(14),
										gradient: LinearGradient(
											begin: Alignment.topLeft,
											end: Alignment.bottomRight,
											colors: <Color>[colorScheme.secondaryContainer, colorScheme.surface],
										),
									),
									child: Row(
										children: [
											Icon(Icons.monitor_heart, color: colorScheme.secondary),
											const SizedBox(width: 8),
											Expanded(child: Text('${context.t('dominant_nadi')}: ${(diagnosis['type'] ?? 'Unknown').toString()}')),
										],
									),
								),
								const SizedBox(height: 12),
								SizedBox(
									height: 220,
									child: RadarChart(
										RadarChartData(
											radarBorderData: const BorderSide(color: Colors.transparent),
											titleTextStyle: const TextStyle(fontSize: 12),
											getTitle: (index, _) {
												const labels = ['Vata', 'Pitta', 'Kapha'];
												return RadarChartTitle(text: labels[index]);
											},
											tickCount: 5,
											dataSets: [
												RadarDataSet(
														  fillColor: Colors.green.withValues(alpha: 0.25),
													borderColor: Colors.green,
													entryRadius: 2,
													dataEntries: [
														RadarEntry(value: vataIntensity),
														RadarEntry(value: pittaIntensity),
														RadarEntry(value: kaphaIntensity),
													],
												),
											],
										),
									),
								),
								const SizedBox(height: 12),
								SizedBox(
									height: 220,
									child: LineChart(
										LineChartData(
											lineBarsData: [
												LineChartBarData(
													spots: List.generate(readings.length, (i) => FlSpot(i.toDouble(), (readings[i]['hrv_ms'] as num).toDouble())),
													color: Theme.of(context).colorScheme.primary,
													isCurved: true,
													barWidth: 3,
												),
											],
										),
									),
								),
								const SizedBox(height: 12),
								Card(
									child: ListTile(
										title: Text('${context.t('dominant_nadi')}: ${(diagnosis['type'] ?? 'Unknown').toString()}'),
										subtitle: Text('${context.t('avg_7_day_hrv')}: ${avg.toStringAsFixed(2)} ms'),
										trailing: anomaly
												? Text(context.t('anomaly'), style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold))
												: Text(context.t('stable')),
									),
								),
								const SizedBox(height: 12),
								SizedBox(
									width: double.infinity,
									child: ElevatedButton.icon(
										onPressed: () => context.read<WearableCubit>().syncToBackend(readings),
										icon: const Icon(Icons.sync),
										label: Text(context.t('sync')),
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
