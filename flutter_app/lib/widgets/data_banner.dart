import 'package:flutter/material.dart';

class DataBannerWidget extends StatelessWidget {
	const DataBannerWidget({super.key});

	Widget _chip(String label, int value) {
		return Expanded(
			child: TweenAnimationBuilder<double>(
				tween: Tween(begin: 0, end: value.toDouble()),
				duration: const Duration(milliseconds: 1200),
				builder: (context, v, _) {
					return Column(
						children: [
							Text(v.toInt().toString(), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
							const SizedBox(height: 2),
							Text(label, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 12)),
						],
					);
				},
			),
		);
	}

	@override
	Widget build(BuildContext context) {
		return Container(
			padding: const EdgeInsets.all(14),
			decoration: BoxDecoration(
				color: Colors.green,
				borderRadius: BorderRadius.circular(12),
			),
			child: Row(
				children: [
					_chip('Records Analysed', 12400),
					_chip('States Monitored', 28),
					_chip('Conditions Tracked', 5),
				],
			),
		);
	}
}
