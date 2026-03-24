import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../widgets/herb_card.dart';
import '../cubits/recommendation_cubit.dart';

class RecommendationResultScreen extends StatefulWidget {
	const RecommendationResultScreen({super.key});

	@override
	State<RecommendationResultScreen> createState() => _RecommendationResultScreenState();
}

class _RecommendationResultScreenState extends State<RecommendationResultScreen> with SingleTickerProviderStateMixin {
	late TabController _tabController;

	@override
	void initState() {
		super.initState();
		_tabController = TabController(length: 4, vsync: this);
	}

	@override
	void dispose() {
		_tabController.dispose();
		super.dispose();
	}

	@override
	Widget build(BuildContext context) {
		return Scaffold(
			appBar: AppBar(
				title: const Text('Recommendations'),
				actions: [
					IconButton(
						onPressed: () => context.read<RecommendationCubit>().regenerate(),
						icon: const Icon(Icons.refresh),
					),
				],
				bottom: TabBar(
					controller: _tabController,
					tabs: const [
						Tab(text: 'Herbs'),
						Tab(text: 'Diet'),
						Tab(text: 'Yoga'),
						Tab(text: 'Dinacharya'),
					],
				),
			),
			floatingActionButton: FloatingActionButton(
				onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Generating report...'))),
				child: const Icon(Icons.download),
			),
			body: BlocBuilder<RecommendationCubit, RecommendationState>(
				builder: (context, state) {
					if (state is RecommendationLoading) return const Center(child: CircularProgressIndicator());
					if (state is RecommendationError) return Center(child: Text(state.msg));
					if (state is! RecommendationLoaded) return const Center(child: Text('No recommendation generated yet.'));

					final data = state.data;
					final response = Map<String, dynamic>.from(data['response_json'] ?? {});
					final herbs = List<Map<String, dynamic>>.from((response['herbs'] ?? []).map((e) => Map<String, dynamic>.from(e as Map)));
					final diet = Map<String, dynamic>.from(response['diet'] ?? {});
					final yoga = List<Map<String, dynamic>>.from((response['yoga'] ?? []).map((e) => Map<String, dynamic>.from(e as Map)));
					final dinacharya = List<Map<String, dynamic>>.from((response['dinacharya'] ?? []).map((e) => Map<String, dynamic>.from(e as Map)));

					return TabBarView(
						controller: _tabController,
						children: [
							ListView.builder(
								padding: const EdgeInsets.all(12),
								itemCount: herbs.length,
								itemBuilder: (context, index) {
									final herb = herbs[index];
									return HerbCard(
										name: herb['name']?.toString() ?? 'Herb',
										benefit: herb['benefit']?.toString() ?? '',
										dosage: herb['dosage']?.toString() ?? '',
										timing: herb['timing']?.toString() ?? '',
									);
								},
							),
							Padding(
								padding: const EdgeInsets.all(12),
								child: Row(
									children: [
										Expanded(
											child: Card(
												color: Colors.green.shade50,
												child: Padding(
													padding: const EdgeInsets.all(10),
													child: Column(
														crossAxisAlignment: CrossAxisAlignment.start,
														children: [
															const Text('Eat', style: TextStyle(fontWeight: FontWeight.bold)),
															const SizedBox(height: 8),
															...List<Map<String, dynamic>>.from((diet['eat'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))).map(
																(item) => Padding(
																	padding: const EdgeInsets.only(bottom: 8),
																	child: Text('• ${item['food']}: ${item['reason']}'),
																),
															),
														],
													),
												),
											),
										),
										const SizedBox(width: 10),
										Expanded(
											child: Card(
												color: Colors.red.shade50,
												child: Padding(
													padding: const EdgeInsets.all(10),
													child: Column(
														crossAxisAlignment: CrossAxisAlignment.start,
														children: [
															const Text('Avoid', style: TextStyle(fontWeight: FontWeight.bold)),
															const SizedBox(height: 8),
															...List<Map<String, dynamic>>.from((diet['avoid'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))).map(
																(item) => Padding(
																	padding: const EdgeInsets.only(bottom: 8),
																	child: Text('• ${item['food']}: ${item['reason']}'),
																),
															),
														],
													),
												),
											),
										),
									],
								),
							),
							ListView(
								padding: const EdgeInsets.all(12),
								children: yoga
										.map(
											(y) => Card(
												child: ListTile(
													title: Text(y['name']?.toString() ?? 'Yoga Practice'),
													subtitle: Text(y['benefit']?.toString() ?? ''),
													trailing: Chip(label: Text(y['duration']?.toString() ?? '')),
												),
											),
										)
										.toList(),
							),
							ListView.builder(
								padding: const EdgeInsets.all(12),
								itemCount: dinacharya.length,
								itemBuilder: (context, index) {
									final d = dinacharya[index];
									return Row(
										crossAxisAlignment: CrossAxisAlignment.start,
										children: [
											SizedBox(width: 76, child: Text(d['time']?.toString() ?? '--:--', style: const TextStyle(fontWeight: FontWeight.bold))),
											Column(
												children: [
													Container(width: 8, height: 8, decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.green)),
													if (index < dinacharya.length - 1) Container(width: 2, height: 48, color: Colors.grey.shade300),
												],
											),
											const SizedBox(width: 10),
											Expanded(child: Padding(padding: const EdgeInsets.only(top: 0), child: Text(d['activity']?.toString() ?? ''))),
										],
									);
								},
							),
						],
					);
				},
			),
		);
	}
}
