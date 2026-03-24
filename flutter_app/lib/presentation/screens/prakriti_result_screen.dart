import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../cubits/prakriti_cubit.dart';

class PrakritiResultScreen extends StatelessWidget {
	const PrakritiResultScreen({super.key});

	String _traits(String dosha) {
		switch (dosha.toLowerCase()) {
			case 'pitta':
				return 'Pitta traits: sharp digestion, focused mind, warm body nature. Balance with cooling foods and routines.';
			case 'kapha':
				return 'Kapha traits: stable energy, grounded temperament, strong endurance. Balance with movement and light meals.';
			default:
				return 'Vata traits: creative mind, light frame, variable energy. Balance with warm food and regular daily rhythm.';
		}
	}

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(title: const Text('Your Prakriti Result')),
			body: BlocBuilder<PrakritiCubit, PrakritiState>(
				builder: (context, state) {
					if (state is! PrakritiCompleted) {
						return const Center(child: Text('No result available'));
					}

					final p = state.profile;
					final v = (p['vata_percent'] ?? 0).toDouble();
					final pi = (p['pitta_percent'] ?? 0).toDouble();
					final k = (p['kapha_percent'] ?? 0).toDouble();
					final dominant = (p['dominant_dosha'] ?? 'vata').toString();
					final risk = ((p['constitutional_risk_score'] ?? 0).toDouble() / 100).clamp(0.0, 1.0);

					return SingleChildScrollView(
						padding: const EdgeInsets.all(16),
						child: Column(
							crossAxisAlignment: CrossAxisAlignment.start,
							children: [
								SizedBox(
									height: 220,
									child: PieChart(
										PieChartData(
											sectionsSpace: 2,
											sections: [
												PieChartSectionData(value: v, color: Colors.green, title: 'V ${v.toStringAsFixed(1)}%'),
												PieChartSectionData(value: pi, color: Colors.orange, title: 'P ${pi.toStringAsFixed(1)}%'),
												PieChartSectionData(value: k, color: Colors.blue, title: 'K ${k.toStringAsFixed(1)}%'),
											],
										),
									),
								),
								const SizedBox(height: 16),
								Row(
									children: [
										Icon(Icons.auto_awesome, color: Theme.of(context).colorScheme.primary, size: 32),
										const SizedBox(width: 8),
										Text('Dominant Dosha: ${dominant.toUpperCase()}', style: Theme.of(context).textTheme.titleLarge),
									],
								),
								const SizedBox(height: 12),
								ExpansionTile(
									title: const Text('Dosha Traits'),
									children: [
										Padding(
											padding: const EdgeInsets.all(12),
											child: Text(_traits(dominant)),
										),
									],
								),
								const SizedBox(height: 12),
								Text('Constitutional Risk Score', style: Theme.of(context).textTheme.titleMedium),
								const SizedBox(height: 8),
								LinearProgressIndicator(value: risk),
								const SizedBox(height: 20),
								SizedBox(
									width: double.infinity,
									child: ElevatedButton(
										onPressed: () async {
											await context.read<PrakritiCubit>().saveProfile(p);
											if (context.mounted) context.go('/home');
										},
										child: const Text('Save Profile'),
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
