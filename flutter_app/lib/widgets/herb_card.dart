import 'package:flutter/material.dart';

class HerbCard extends StatelessWidget {
	final String name;
	final String benefit;
	final String dosage;
	final String timing;

	const HerbCard({
		super.key,
		required this.name,
		required this.benefit,
		required this.dosage,
		required this.timing,
	});

	@override
	Widget build(BuildContext context) {
		return Card(
			child: Padding(
				padding: const EdgeInsets.all(12),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
						const SizedBox(height: 6),
						Text(benefit),
						const SizedBox(height: 10),
						Row(
							children: [
								Chip(label: Text(dosage)),
								const SizedBox(width: 8),
								Chip(label: Text(timing)),
							],
						),
					],
				),
			),
		);
	}
}
