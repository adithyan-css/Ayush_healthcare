import 'package:flutter/material.dart';

class DoshaGaugeWidget extends StatelessWidget {
	final double vata;
	final double pitta;
	final double kapha;

	const DoshaGaugeWidget({
		super.key,
		required this.vata,
		required this.pitta,
		required this.kapha,
	});

	Widget _row(String label, double value, Color color) {
		return Padding(
			padding: const EdgeInsets.only(bottom: 10),
			child: Row(
				children: [
					SizedBox(width: 56, child: Text(label)),
					Expanded(
						child: LinearProgressIndicator(
							value: (value / 100).clamp(0.0, 1.0),
							minHeight: 8,
							color: color,
							  backgroundColor: color.withOpacity(0.2),
						),
					),
					const SizedBox(width: 8),
					SizedBox(width: 44, child: Text('${value.toStringAsFixed(1)}%')),
				],
			),
		);
	}

	@override
	Widget build(BuildContext context) {
		if (vata == 0 && pitta == 0 && kapha == 0) {
			return Card(
				child: Padding(
					padding: const EdgeInsets.all(14),
					child: Column(
						crossAxisAlignment: CrossAxisAlignment.start,
						children: [
							const Text('No Prakriti profile yet'),
							const SizedBox(height: 8),
							ElevatedButton(onPressed: null, child: const Text('Complete Quiz to unlock gauge')),
						],
					),
				),
			);
		}

		return Card(
			child: Padding(
				padding: const EdgeInsets.all(14),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Text('Dosha Balance', style: Theme.of(context).textTheme.titleMedium),
						const SizedBox(height: 10),
						_row('Vata', vata, Colors.green),
						_row('Pitta', pitta, Colors.orange),
						_row('Kapha', kapha, Colors.blue),
					],
				),
			),
		);
	}
}
