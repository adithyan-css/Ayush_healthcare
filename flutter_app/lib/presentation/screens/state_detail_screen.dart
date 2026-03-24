import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../cubits/heatmap_cubit.dart';

class StateDetailScreen extends StatelessWidget {
	final String stateId;
	const StateDetailScreen({super.key, required this.stateId});

	Color _severityColor(String level) {
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

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(title: Text('State Detail - $stateId')),
			body: BlocBuilder<HeatmapCubit, HeatmapState>(
				builder: (context, state) {
					if (state is HeatmapLoading || state is HeatmapInitial) {
						return const Center(child: CircularProgressIndicator());
					}
					if (state is! StateSelected) {
						return const Center(child: Text('No state selected'));
					}

					final d = state.detail;
					final level = d['risk_level']?.toString() ?? 'low';
					final monthly = Map<String, dynamic>.from(d['monthly_cases'] ?? {});
					final values = monthly.values.map((e) => (e as num).toDouble()).toList();
					final tips = [
						'Favor seasonal cooked foods.',
						'Hydrate with warm herbal water.',
						'Daily pranayama for respiratory resilience.',
					];

					return SingleChildScrollView(
						padding: const EdgeInsets.all(16),
						child: Column(
							crossAxisAlignment: CrossAxisAlignment.start,
							children: [
								Row(
									children: [
										Expanded(
											child: Text(d['state_name']?.toString() ?? 'Unknown', style: Theme.of(context).textTheme.headlineSmall),
										),
										Chip(
											label: Text(level.toUpperCase()),
											  backgroundColor: _severityColor(level).withOpacity(0.2),
											side: BorderSide(color: _severityColor(level)),
										),
									],
								),
								const SizedBox(height: 8),
								Wrap(
									spacing: 8,
									children: [
										Chip(label: Text(d['top_condition']?.toString() ?? 'Unknown Condition')),
									],
								),
								const SizedBox(height: 16),
								SizedBox(
									height: 220,
									child: LineChart(
										LineChartData(
											gridData: const FlGridData(show: true),
											borderData: FlBorderData(show: false),
											lineBarsData: [
												LineChartBarData(
													isCurved: true,
													color: Theme.of(context).colorScheme.primary,
													barWidth: 3,
													spots: List.generate(values.length, (i) => FlSpot(i.toDouble(), values[i])),
												),
											],
											titlesData: FlTitlesData(
												leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true)),
												rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
												topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
												bottomTitles: AxisTitles(
													sideTitles: SideTitles(
														showTitles: true,
														getTitlesWidget: (value, meta) {
															final keys = monthly.keys.toList();
															final idx = value.toInt();
															if (idx < 0 || idx >= keys.length) return const SizedBox.shrink();
															return Text(keys[idx]);
														},
													),
												),
											),
										),
									),
								),
								const SizedBox(height: 16),
								Text('AYUSH Tips', style: Theme.of(context).textTheme.titleMedium),
								const SizedBox(height: 8),
								...tips.map((t) => Card(child: ListTile(leading: const Icon(Icons.spa), title: Text(t)))),
								const SizedBox(height: 16),
								Text('XAI Panel', style: Theme.of(context).textTheme.titleMedium),
								const SizedBox(height: 8),
								...state.xaiReasons.asMap().entries.map(
											(e) => Card(
												child: ListTile(
													leading: CircleAvatar(radius: 12, child: Text('${e.key + 1}')),
													title: Text(e.value),
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
