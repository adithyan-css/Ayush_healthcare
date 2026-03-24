import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../cubits/forecast_cubit.dart';

class ForecastScreen extends StatefulWidget {
	const ForecastScreen({super.key});

	@override
	State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
	@override
	void initState() {
		super.initState();
		context.read<ForecastCubit>().loadForecast();
	}

	Color _severityColor(String severity) {
		switch (severity) {
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

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(title: const Text('Forecast')),
			floatingActionButton: FloatingActionButton.extended(
				onPressed: () => context.read<ForecastCubit>().generateBulletin('MH'),
				icon: const Icon(Icons.picture_as_pdf),
				label: const Text('Generate Bulletin'),
			),
			body: BlocBuilder<ForecastCubit, ForecastState>(
				builder: (context, state) {
					if (state is ForecastLoading || state is ForecastInitial) return const Center(child: CircularProgressIndicator());
					if (state is ForecastError) return Center(child: Text(state.msg));
					if (state is! ForecastLoaded) return const SizedBox.shrink();

					final data = state.data;
					final conditions = Map<String, dynamic>.from(data['conditions'] ?? {});
					final regionCards = List<Map<String, dynamic>>.from((data['region_cards'] ?? []).map((e) => Map<String, dynamic>.from(e as Map)));
					final population = Map<String, dynamic>.from(data['population_risks'] ?? {});
					final seasonal = Map<String, dynamic>.from(data['seasonal'] ?? {});

					final colors = [Colors.green, Colors.orange, Colors.blue, Colors.purple, Colors.red];

					return SingleChildScrollView(
						padding: const EdgeInsets.all(12),
						child: Column(
							crossAxisAlignment: CrossAxisAlignment.start,
							children: [
								SizedBox(
									height: 260,
									child: LineChart(
										LineChartData(
											lineBarsData: conditions.entries.toList().asMap().entries.map((entry) {
												final i = entry.key;
												final values = (entry.value.value as List).map((e) => (e as num).toDouble()).toList();
												return LineChartBarData(
													spots: List.generate(values.length, (idx) => FlSpot(idx.toDouble(), values[idx])),
													color: colors[i % colors.length],
													isCurved: true,
													barWidth: 2,
												);
											}).toList(),
										),
									),
								),
								const SizedBox(height: 8),
								Wrap(
									spacing: 8,
									children: conditions.keys.toList().asMap().entries.map((entry) {
										return Row(
											mainAxisSize: MainAxisSize.min,
											children: [
												Container(width: 10, height: 10, decoration: BoxDecoration(color: colors[entry.key % colors.length], shape: BoxShape.circle)),
												const SizedBox(width: 4),
												Text(entry.value),
											],
										);
									}).toList(),
								),
								const SizedBox(height: 16),
								GridView.builder(
									shrinkWrap: true,
									physics: const NeverScrollableScrollPhysics(),
									itemCount: regionCards.length,
									gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 1.25, crossAxisSpacing: 8, mainAxisSpacing: 8),
									itemBuilder: (context, index) {
										final card = regionCards[index];
										final severity = card['severity']?.toString() ?? 'low';
										return Card(
											child: Padding(
												padding: const EdgeInsets.all(10),
												child: Column(
													crossAxisAlignment: CrossAxisAlignment.start,
													children: [
														Text(card['region']?.toString() ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
														Text(card['condition']?.toString() ?? ''),
														const Spacer(),
														Chip(label: Text('Peak ${card['peak_in_days']}d')),
														Text(severity.toUpperCase(), style: TextStyle(color: _severityColor(severity))),
													],
												),
											),
										);
									},
								),
								const SizedBox(height: 16),
								SizedBox(
									height: 220,
									child: BarChart(
										BarChartData(
											barGroups: population.entries.toList().asMap().entries.map((e) {
												return BarChartGroupData(
													x: e.key,
													barRods: [BarChartRodData(toY: (e.value.value as num).toDouble(), color: Colors.teal)],
												);
											}).toList(),
											titlesData: FlTitlesData(
												leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true)),
												rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
												topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
												bottomTitles: AxisTitles(
													sideTitles: SideTitles(
														showTitles: true,
														getTitlesWidget: (value, meta) {
															final keys = population.keys.toList();
															if (value.toInt() < 0 || value.toInt() >= keys.length) return const SizedBox.shrink();
															return Text(keys[value.toInt()], style: const TextStyle(fontSize: 10));
														},
													),
												),
											),
										),
									),
								),
								const SizedBox(height: 12),
								Card(
									child: ListTile(
										leading: const Icon(Icons.wb_sunny_outlined),
										title: Text('Season: ${seasonal['season'] ?? ''}'),
										subtitle: Text(seasonal['advisory']?.toString() ?? ''),
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
