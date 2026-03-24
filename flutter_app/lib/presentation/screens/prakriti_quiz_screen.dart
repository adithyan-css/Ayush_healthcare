import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../core/i18n/language_map.dart';
import '../cubits/prakriti_cubit.dart';

class PrakritiQuizScreen extends StatefulWidget {
	const PrakritiQuizScreen({super.key});

	@override
	State<PrakritiQuizScreen> createState() => _PrakritiQuizScreenState();
}

class _PrakritiQuizScreenState extends State<PrakritiQuizScreen> {
	final PageController _pageController = PageController();
	final Map<int, String> _selectedByQuestion = {};

	@override
	void initState() {
		super.initState();
		context.read<PrakritiCubit>().loadQuestions();
	}

	@override
	void dispose() {
		_pageController.dispose();
		super.dispose();
	}

	@override
	Widget build(BuildContext context) {
		final colorScheme = Theme.of(context).colorScheme;
		return Scaffold(
			appBar: AppBar(title: Text(context.t('prakriti_quiz'))),
			body: BlocConsumer<PrakritiCubit, PrakritiState>(
				listener: (context, state) {
					if (state is PrakritiCompleted) {
						context.go('/quiz-result');
					}
				},
				builder: (context, state) {
					if (state is PrakritiLoading || state is PrakritiInitial) {
						return const Center(child: CircularProgressIndicator());
					}
					if (state is PrakritiError) {
						return Center(child: Text(state.msg));
					}
					if (state is PrakritiQuestionsLoaded) {
						final progress = ((state.currentIndex + 1) / state.questions.length).clamp(0.0, 1.0);
						return Column(
							children: [
								Padding(
									padding: const EdgeInsets.fromLTRB(16, 16, 16, 10),
									child: Column(
										crossAxisAlignment: CrossAxisAlignment.start,
										children: [
											Text(
												'${context.t('question')} ${state.currentIndex + 1} ${context.t('of')} ${state.questions.length}',
												style: Theme.of(context).textTheme.labelMedium,
											),
											const SizedBox(height: 8),
											LinearProgressIndicator(value: progress),
										],
									),
								),
								Expanded(
									child: PageView.builder(
										controller: _pageController,
										physics: const NeverScrollableScrollPhysics(),
										itemCount: state.questions.length,
										itemBuilder: (context, index) {
											final q = state.questions[index] as Map<String, dynamic>;
											final options = (q['options'] as List).cast<Map<String, dynamic>>();
											return Padding(
												padding: const EdgeInsets.all(16),
												child: Container(
													decoration: BoxDecoration(
														color: colorScheme.surface,
														borderRadius: BorderRadius.circular(20),
													),
													padding: const EdgeInsets.all(16),
													child: Column(
														crossAxisAlignment: CrossAxisAlignment.start,
														children: [
															Text('Q${index + 1}', style: Theme.of(context).textTheme.titleLarge),
															const SizedBox(height: 8),
															Text(q['question'].toString(), style: Theme.of(context).textTheme.headlineSmall),
															const SizedBox(height: 16),
															...options.asMap().entries.map((entry) {
																final opt = entry.value;
																final dosha = opt['dosha'].toString();
																final selected = _selectedByQuestion[index] == dosha;
																final labels = <String>['A', 'B', 'C'];
																return GestureDetector(
																	onTap: () {
																		setState(() {
																			_selectedByQuestion[index] = dosha;
																		});
																	},
																	child: Container(
																		margin: const EdgeInsets.only(bottom: 10),
																		padding: const EdgeInsets.all(12),
																		decoration: BoxDecoration(
																			color: selected ? colorScheme.primaryContainer : colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
																			borderRadius: BorderRadius.circular(14),
																			border: Border.all(
																				color: selected ? colorScheme.primary : colorScheme.outlineVariant,
																			),
																		),
																		child: Row(
																			children: [
																				CircleAvatar(
																					radius: 12,
																					backgroundColor: selected ? colorScheme.primary : colorScheme.surfaceContainer,
																					child: Text(labels[entry.key], style: Theme.of(context).textTheme.labelSmall),
																				),
																				const SizedBox(width: 10),
																				Expanded(child: Text(opt['text'].toString())),
																				if (selected) Icon(Icons.check_circle, color: colorScheme.primary),
																			],
																		),
																	),
																);
															}),
															const Spacer(),
															SizedBox(
																width: double.infinity,
																child: ElevatedButton(
																	onPressed: _selectedByQuestion[index] == null
																		? null
																		: () {
																				context.read<PrakritiCubit>().answerQuestion(index, _selectedByQuestion[index]!);
																				if (index < state.questions.length - 1) {
																					_pageController.nextPage(duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
																				} else {
																					context.read<PrakritiCubit>().calculateResult();
																				}
																			},
																		child: Text(index == state.questions.length - 1 ? context.t('see_results') : context.t('next')),
																	),
															),
														],
													),
												),
											);
										},
									),
								),
							],
						);
					}
					return const SizedBox.shrink();
				},
			),
		);
	}
}
