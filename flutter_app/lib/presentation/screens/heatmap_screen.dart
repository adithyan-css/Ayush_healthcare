import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../cubits/heatmap_cubit.dart';

class HeatmapScreen extends StatefulWidget {
	const HeatmapScreen({super.key});

	@override
	State<HeatmapScreen> createState() => _HeatmapScreenState();
}

class _HeatmapScreenState extends State<HeatmapScreen> with SingleTickerProviderStateMixin {
	late final AnimationController _pulseController;
	String _condition = 'all';
	Set<String> _season = {'all'};

	@override
	void initState() {
		super.initState();
		_pulseController = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat(reverse: true);
		context.read<HeatmapCubit>().loadHeatmapData();
	}

	@override
	void dispose() {
		_pulseController.dispose();
		super.dispose();
	}

	Color _riskColor(String level) {
		switch (level.toLowerCase()) {
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
		return Scaffold(
			appBar: AppBar(title: const Text('Disease Heatmap')),
			body: BlocBuilder<HeatmapCubit, HeatmapState>(
				builder: (context, state) {
					final districts = state is HeatmapLoaded
							? state.districts
							: state is StateSelected
									? [state.detail]
									: <dynamic>[];

					return Stack(
						children: [
							FlutterMap(
								options: const MapOptions(
									initialCenter: LatLng(20.5937, 78.9629),
									initialZoom: 4.5,
								),
								children: [
									TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
									MarkerLayer(
										markers: districts.map((raw) {
											final d = Map<String, dynamic>.from(raw as Map);
											final risk = d['risk_level']?.toString() ?? 'low';
											final rising = (d['trend']?.toString() ?? '').toLowerCase() == 'rising';
											final lat = (d['latitude'] ?? 20.5937).toDouble();
											final lng = (d['longitude'] ?? 78.9629).toDouble();
											final color = _riskColor(risk);

											return Marker(
												point: LatLng(lat, lng),
												width: 36,
												height: 36,
												child: GestureDetector(
													onTap: () async {
														final id = d['state_code']?.toString() ?? 'MH';
														await context.read<HeatmapCubit>().selectState(id);
														if (context.mounted) context.go('/state-detail', extra: id);
													},
													child: AnimatedBuilder(
														animation: _pulseController,
														builder: (context, _) {
															final scale = rising ? (1 + (_pulseController.value * 0.4)) : 1.0;
															return Transform.scale(
																scale: scale,
																child: Container(
																	decoration: BoxDecoration(
																		shape: BoxShape.circle,
																		color: color.withOpacity(0.85),
																		border: Border.all(color: Colors.white, width: 2),
																	),
																),
															);
														},
													),
												),
											);
										}).toList(),
									),
								],
							),
							if (state is HeatmapLoading) const Center(child: CircularProgressIndicator()),
							Align(
								alignment: Alignment.bottomCenter,
								child: Container(
									decoration: BoxDecoration(
										color: Colors.white,
										borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
										boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10)],
									),
									padding: const EdgeInsets.all(12),
									child: Row(
										children: [
											Expanded(
												child: DropdownButtonFormField<String>(
													value: _condition,
													decoration: const InputDecoration(labelText: 'Condition'),
													items: const [
														DropdownMenuItem(value: 'all', child: Text('All')),
														DropdownMenuItem(value: 'Fever/Viral', child: Text('Fever/Viral')),
														DropdownMenuItem(value: 'Respiratory', child: Text('Respiratory')),
														DropdownMenuItem(value: 'Digestive', child: Text('Digestive')),
														DropdownMenuItem(value: 'Joint', child: Text('Joint')),
														DropdownMenuItem(value: 'Skin', child: Text('Skin')),
													],
													onChanged: (v) {
														setState(() => _condition = v ?? 'all');
														context.read<HeatmapCubit>().applyFilter(_condition, _season.first);
													},
												),
											),
											const SizedBox(width: 8),
											Expanded(
												child: SegmentedButton<String>(
													segments: const [
														ButtonSegment(value: 'all', label: Text('All')),
														ButtonSegment(value: 'summer', label: Text('Summer')),
														ButtonSegment(value: 'monsoon', label: Text('Monsoon')),
														ButtonSegment(value: 'winter', label: Text('Winter')),
													],
													selected: _season,
													onSelectionChanged: (v) {
														setState(() => _season = v);
														context.read<HeatmapCubit>().applyFilter(_condition, _season.first);
													},
												),
											),
										],
									),
								),
							),
						],
					);
				},
			),
		);
	}
}
