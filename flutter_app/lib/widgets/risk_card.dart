import 'package:flutter/material.dart';

class RiskCard extends StatelessWidget {
	final String region;
	final String condition;
	final String severity;
	final int peakDays;

	const RiskCard({
		super.key,
		required this.region,
		required this.condition,
		required this.severity,
		required this.peakDays,
	});

	Color _severityColor() {
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

	@override
	Widget build(BuildContext context) {
		return Container(
			decoration: BoxDecoration(
				color: Colors.white,
				borderRadius: BorderRadius.circular(12),
				border: Border(left: BorderSide(color: _severityColor(), width: 5)),
			),
			child: Padding(
				padding: const EdgeInsets.all(12),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Text(region, style: const TextStyle(fontWeight: FontWeight.bold)),
						const SizedBox(height: 4),
						Text(condition),
						const Spacer(),
						Chip(label: Text('Peak in $peakDays days')),
					],
				),
			),
		);
	}
}
