import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/i18n/language_map.dart';
import '../../services/hive_service.dart';
import '../cubits/recommendation_cubit.dart';

class SymptomSelectionScreen extends StatefulWidget {
	const SymptomSelectionScreen({super.key});

	@override
	State<SymptomSelectionScreen> createState() => _SymptomSelectionScreenState();
}

class _SymptomSelectionScreenState extends State<SymptomSelectionScreen> {
	final _freeTextController = TextEditingController();

	final Map<String, List<String>> _categories = {
		'General': ['Fever', 'Fatigue', 'Weakness', 'Body Ache'],
		'Respiratory': ['Cough', 'Sore Throat', 'Runny Nose', 'Breathlessness'],
		'Digestive': ['Bloating', 'Acidity', 'Constipation', 'Loose Motions'],
		'Skin': ['Rash', 'Itching', 'Dry Skin', 'Acne'],
		'Mind/Stress': ['Anxiety', 'Irritability', 'Insomnia', 'Brain Fog'],
	};

	Color _doshaColor() {
		final profile = HiveService.getPrakritiProfile() ?? {};
		final dominant = (profile['dominant_dosha'] ?? 'vata').toString().toLowerCase();
		if (dominant == 'pitta') return Colors.orange;
		if (dominant == 'kapha') return Colors.blue;
		return Colors.green;
	}

	@override
	void dispose() {
		_freeTextController.dispose();
		super.dispose();
	}

	@override
	Widget build(BuildContext context) {
		final colorScheme = Theme.of(context).colorScheme;
		return Scaffold(
			appBar: AppBar(title: Text(context.t('select_symptoms'))),
			body: BlocListener<RecommendationCubit, RecommendationState>(
				listener: (context, state) {
					if (state is RecommendationLoaded) {
						context.go('/recommend/result');
					}
				},
				child: BlocBuilder<RecommendationCubit, RecommendationState>(
					builder: (context, state) {
						final cubit = context.read<RecommendationCubit>();
						final selected = cubit.selectedSymptoms;
						return Stack(
							children: [
								SingleChildScrollView(
									padding: const EdgeInsets.fromLTRB(16, 14, 16, 110),
									child: Column(
										crossAxisAlignment: CrossAxisAlignment.start,
										children: [
											Container(
												width: double.infinity,
												padding: const EdgeInsets.all(14),
												decoration: BoxDecoration(
													color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
													borderRadius: BorderRadius.circular(14),
												),
												child: Row(
													children: [
														Icon(Icons.fact_check_outlined, color: colorScheme.primary),
														const SizedBox(width: 8),
														Expanded(
															child: Text('${selected.length} ${context.t('selected')}', style: Theme.of(context).textTheme.titleSmall),
														),
													],
												),
											),
											const SizedBox(height: 14),
											..._categories.entries.map((entry) {
												return Column(
													crossAxisAlignment: CrossAxisAlignment.start,
													children: [
														Text(entry.key, style: Theme.of(context).textTheme.titleMedium),
														const SizedBox(height: 8),
														Wrap(
															spacing: 8,
															runSpacing: 8,
															children: entry.value.map((symptom) {
																final isSelected = selected.contains(symptom);
																return FilterChip(
																	label: Text(symptom),
																	selected: isSelected,
																	selectedColor: _doshaColor().withValues(alpha: 0.18),
																	checkmarkColor: _doshaColor(),
																	side: BorderSide(color: isSelected ? _doshaColor() : colorScheme.outlineVariant),
																	onSelected: (_) => cubit.toggleSymptom(symptom),
																);
															}).toList(),
														),
														const SizedBox(height: 16),
													],
												);
											}),
											TextField(
												controller: _freeTextController,
												minLines: 2,
												maxLines: 4,
												decoration: InputDecoration(
													labelText: context.t('optional_notes'),
													hintText: context.t('describe_symptoms'),
												),
											),
										],
									),
								),
								Align(
									alignment: Alignment.bottomCenter,
									child: SafeArea(
										minimum: const EdgeInsets.fromLTRB(16, 8, 16, 16),
										child: SizedBox(
											width: double.infinity,
											height: 52,
											child: ElevatedButton(
												onPressed: selected.isEmpty
														? null
														: () => context.read<RecommendationCubit>().generateRecommendation(_freeTextController.text.trim().isEmpty ? null : _freeTextController.text.trim()),
												child: Text(context.t('submit')),
											),
										),
									),
								),
								if (state is RecommendationLoading)
									Positioned.fill(
										child: Container(
											color: Colors.black.withValues(alpha: 0.25),
											child: Center(
												child: Shimmer.fromColors(
													baseColor: Colors.white,
													highlightColor: Colors.grey.shade100,
													child: Container(
														width: 220,
														height: 50,
														alignment: Alignment.center,
														decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
														child: Text(context.t('generating'), style: const TextStyle(fontWeight: FontWeight.bold)),
													),
												),
											),
										),
									),
							],
						);
					},
				),
			),
		);
	}
}
