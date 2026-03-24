import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class TrendChart extends StatelessWidget {
	final List<double> data;
	final String title;

	const TrendChart({super.key, required this.data, required this.title});

	@override
	Widget build(BuildContext context) {
		return Card(
			child: Padding(
				padding: const EdgeInsets.all(12),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Text(title, style: Theme.of(context).textTheme.titleMedium),
						const SizedBox(height: 10),
						SizedBox(
							height: 180,
							child: LineChart(
								LineChartData(
									borderData: FlBorderData(show: false),
									gridData: const FlGridData(show: true),
									lineBarsData: [
										LineChartBarData(
											spots: List.generate(data.length, (i) => FlSpot(i.toDouble(), data[i])),
											isCurved: true,
											color: Theme.of(context).colorScheme.primary,
											barWidth: 3,
										),
									],
								),
							),
						),
					],
				),
			),
		);
	}
}
