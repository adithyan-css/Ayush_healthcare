import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
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
		return Scaffold(
			appBar: AppBar(title: const Text('Prakriti Quiz')),
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
									padding: const EdgeInsets.all(16),
									child: LinearProgressIndicator(value: progress),
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
												child: Column(
													crossAxisAlignment: CrossAxisAlignment.start,
													children: [
														Text('Q${index + 1}', style: Theme.of(context).textTheme.titleLarge),
														const SizedBox(height: 8),
														Text(q['question'].toString(), style: Theme.of(context).textTheme.headlineSmall),
														const SizedBox(height: 20),
														...options.map((opt) {
															final dosha = opt['dosha'].toString();
															final selected = _selectedByQuestion[index] == dosha;
															return GestureDetector(
																onTap: () {
																	setState(() {
																		_selectedByQuestion[index] = dosha;
																	});
																},
																child: Card(
																	color: selected ? Theme.of(context).colorScheme.primaryContainer : null,
																	child: Padding(
																		padding: const EdgeInsets.all(14),
																		child: Row(
																			children: [
																				Expanded(child: Text(opt['text'].toString())),
																				if (selected) const Icon(Icons.check_circle),
																			],
																		),
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
																child: Text(index == state.questions.length - 1 ? 'See Results' : 'Next'),
															),
														),
													],
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
