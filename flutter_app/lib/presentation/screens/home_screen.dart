import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/hive_service.dart';
import '../../widgets/alert_banner.dart';
import '../../widgets/data_banner.dart';
import '../../widgets/dosha_gauge.dart';
import '../cubits/heatmap_cubit.dart';

class HomeScreen extends StatefulWidget {
	const HomeScreen({super.key});

	@override
	State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
	@override
	void initState() {
		super.initState();
		context.read<HeatmapCubit>().loadHeatmapData();
	}

	List<Map<String, String>> _ritucharyaTips() {
		final month = DateTime.now().month;
		final seasonTip = (month >= 6 && month <= 9)
				? 'Boiled water + digestive spices'
				: (month >= 3 && month <= 5)
						? 'Cooling foods + hydration'
						: (month == 12 || month <= 2)
								? 'Warm oil massage + soups'
								: 'Balanced grounding meals';

		return List.generate(7, (i) {
			final day = DateTime.now().add(Duration(days: i));
			return {'day': DateFormat('EEE').format(day), 'tip': seasonTip};
		});
	}

	@override
	Widget build(BuildContext context) {
		final profile = HiveService.getPrakritiProfile() ?? {};
		final sessions = HiveService.getSessions().take(3).toList();
		final ritucharya = _ritucharyaTips();

		return Scaffold(
			appBar: AppBar(
				title: const Text('PrakritiOS'),
				actions: [
					IconButton(
						onPressed: () => context.go('/settings'),
						icon: const Icon(Icons.settings),
					),
				],
			),
			body: SingleChildScrollView(
				padding: const EdgeInsets.all(16),
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						const DataBannerWidget(),
						const SizedBox(height: 12),
						DoshaGaugeWidget(
							vata: (profile['vata_percent'] ?? 0).toDouble(),
							pitta: (profile['pitta_percent'] ?? 0).toDouble(),
							kapha: (profile['kapha_percent'] ?? 0).toDouble(),
						),
						const SizedBox(height: 12),
						BlocBuilder<HeatmapCubit, HeatmapState>(
							builder: (context, state) {
								if (state is HeatmapLoaded && state.districts.isNotEmpty) {
									final sorted = List<Map<String, dynamic>>.from(state.districts.map((e) => Map<String, dynamic>.from(e as Map)));
									sorted.sort((a, b) => ((b['risk_score'] ?? 0) as num).compareTo((a['risk_score'] ?? 0) as num));
									final top = sorted.first;
									return AlertBannerWidget(
										riskLevel: top['risk_level']?.toString() ?? 'low',
										condition: top['top_condition']?.toString() ?? 'N/A',
										stateName: top['state_name']?.toString() ?? 'Unknown',
										onTap: () => context.go('/heatmap'),
									);
								}
								return AlertBannerWidget(
									riskLevel: 'medium',
									condition: 'Loading regional data',
									stateName: 'India',
									onTap: () => context.go('/heatmap'),
								);
							},
						),
						const SizedBox(height: 16),
						Text('Ritucharya (7 days)', style: Theme.of(context).textTheme.titleMedium),
						const SizedBox(height: 8),
						SizedBox(
							height: 88,
							child: ListView.separated(
								scrollDirection: Axis.horizontal,
								itemCount: ritucharya.length,
								separatorBuilder: (_, __) => const SizedBox(width: 8),
								itemBuilder: (context, index) {
									final item = ritucharya[index];
									return Container(
										width: 140,
										padding: const EdgeInsets.all(10),
										decoration: BoxDecoration(
											borderRadius: BorderRadius.circular(12),
											color: Colors.white,
										),
										child: Column(
											crossAxisAlignment: CrossAxisAlignment.start,
											children: [
												Text(item['day']!, style: const TextStyle(fontWeight: FontWeight.bold)),
												const SizedBox(height: 6),
												Text(item['tip']!, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
											],
										),
									);
								},
							),
						),
						const SizedBox(height: 16),
						Text('Recent Sessions', style: Theme.of(context).textTheme.titleMedium),
						const SizedBox(height: 8),
						...sessions.map((session) {
							final symptoms = ((session['symptoms'] is List)
											? List<dynamic>.from(session['symptoms'] as List)
											: List<dynamic>.from((session['symptoms']?['items'] ?? []) as List))
									.map((e) => e.toString())
									.toList();
							return Card(
								child: ListTile(
									title: Text(session['created_at']?.toString().split('T').first ?? 'Recent'),
									subtitle: Wrap(
										spacing: 6,
										children: symptoms.take(4).map((s) => Chip(label: Text(s), visualDensity: VisualDensity.compact)).toList(),
									),
								),
							);
						}),
						const SizedBox(height: 16),
						GridView.count(
							crossAxisCount: 2,
							shrinkWrap: true,
							physics: const NeverScrollableScrollPhysics(),
							crossAxisSpacing: 10,
							mainAxisSpacing: 10,
							children: [
								_ActionTile(title: 'Get Recommendations', icon: Icons.medical_services, onTap: () => context.go('/symptoms')),
								_ActionTile(title: 'Disease Heatmap', icon: Icons.map, onTap: () => context.go('/heatmap')),
								_ActionTile(title: 'Forecast', icon: Icons.query_stats, onTap: () => context.go('/forecast')),
								_ActionTile(title: 'Nadi Monitor', icon: Icons.favorite, onTap: () => context.go('/nadi')),
							],
						),
					],
				),
			),
		);
	}
}

class _ActionTile extends StatelessWidget {
	final String title;
	final IconData icon;
	final VoidCallback onTap;

	const _ActionTile({required this.title, required this.icon, required this.onTap});

	@override
	Widget build(BuildContext context) {
		return InkWell(
			onTap: onTap,
			child: Card(
				child: Center(
					child: Column(
						mainAxisSize: MainAxisSize.min,
						children: [
							Icon(icon, size: 28),
							const SizedBox(height: 8),
							Text(title, textAlign: TextAlign.center),
						],
					),
				),
			),
		);
	}
}
