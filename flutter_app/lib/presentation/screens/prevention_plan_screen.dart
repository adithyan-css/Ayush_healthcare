import 'package:flutter/material.dart';

import '../../core/i18n/language_map.dart';

class PreventionPlanScreen extends StatelessWidget {
  const PreventionPlanScreen({super.key, required this.plan});

  final String plan;

  List<String> _parseSteps(String text) {
    final List<String> lines = text
        .split(RegExp(r'\r?\n'))
        .map((String e) => e.trim())
        .where((String e) => e.isNotEmpty)
        .toList(growable: false);

    if (lines.isNotEmpty) {
      return lines;
    }

    return text
        .split(RegExp(r'(?<=[.!?])\s+'))
        .map((String e) => e.trim())
        .where((String e) => e.isNotEmpty)
        .toList(growable: false);
  }

  @override
  Widget build(BuildContext context) {
    final List<String> steps = _parseSteps(plan);
    return Scaffold(
      appBar: AppBar(title: Text(context.t('prevention_30_day_plan'))),
      body: ListView.separated(
        padding: const EdgeInsets.all(14),
        itemCount: steps.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (BuildContext context, int index) {
          final String step = steps[index];
          return Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                CircleAvatar(
                  radius: 14,
                  child: Text('${index + 1}', style: const TextStyle(fontSize: 12)),
                ),
                const SizedBox(width: 10),
                Expanded(child: Text(step)),
              ],
            ),
          );
        },
      ),
    );
  }
}
