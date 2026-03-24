import 'package:flutter/material.dart';

class AlertBannerWidget extends StatelessWidget {
	final String riskLevel;
	final String condition;
	final String stateName;
	final VoidCallback? onTap;

	const AlertBannerWidget({
		super.key,
		required this.riskLevel,
		required this.condition,
		required this.stateName,
		this.onTap,
	});

	Color _color() {
		switch (riskLevel.toLowerCase()) {
			case 'critical':
				return Colors.red;
			case 'high':
				return Colors.orange;
			case 'medium':
				return Colors.yellow.shade700;
			default:
				return Colors.green;
		}
	}

	@override
	Widget build(BuildContext context) {
		return InkWell(
			onTap: onTap,
			borderRadius: BorderRadius.circular(12),
			child: Container(
				padding: const EdgeInsets.all(12),
				decoration: BoxDecoration(
					  color: _color().withOpacity(0.18),
					borderRadius: BorderRadius.circular(12),
					border: Border.all(color: _color()),
				),
				child: Row(
					children: [
						Icon(Icons.warning_amber_rounded, color: _color()),
						const SizedBox(width: 10),
						Expanded(child: Text('$stateName - $condition - ↑')),
					],
				),
			),
		);
	}
}
