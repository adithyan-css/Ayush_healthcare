import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/i18n/language_map.dart';
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
  String _todayTip = 'Daily AYUSH guidance is being prepared for you.';

  @override
  void initState() {
    super.initState();
    context.read<HeatmapCubit>().loadHeatmapData();
    _loadDoshaTip();
  }

  Future<void> _loadDoshaTip() async {
    try {
      final String raw = await rootBundle.loadString('assets/data/dosha_tips.json');
      final Map<String, dynamic> tipMap = Map<String, dynamic>.from(jsonDecode(raw) as Map);

      final Map<String, dynamic> profile = HiveService.getPrakritiProfile() ?? <String, dynamic>{};
      final String dosha = (profile['dominant_dosha'] ?? 'vata').toString().toLowerCase();
      final List<dynamic> source = (tipMap[dosha] as List<dynamic>? ?? <dynamic>[]);

      if (source.isEmpty) {
        return;
      }

      final int index = DateTime.now().day % 10;
      final String tip = source[index % source.length].toString();
      if (!mounted) {
        return;
      }
      setState(() {
        _todayTip = tip;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _todayTip = 'Stay hydrated, eat warm fresh food, and follow your routine.';
      });
    }
  }

  List<Map<String, String>> _ritucharyaTips() {
    return List<Map<String, String>>.generate(7, (int i) {
      final DateTime day = DateTime.now().add(Duration(days: i));
      return <String, String>{
        'day': DateFormat('EEE').format(day),
        'tip': _todayTip,
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    final Map<String, dynamic> profile = HiveService.getPrakritiProfile() ?? <String, dynamic>{};
    final List<Map<String, dynamic>> sessions = HiveService.getSessions().take(3).toList();
    final List<Map<String, String>> ritucharya = _ritucharyaTips();

    return Scaffold(
      appBar: AppBar(
        title: Text(context.t('app_name')),
        actions: <Widget>[
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
          children: <Widget>[
            const DataBannerWidget(),
            const SizedBox(height: 12),
            DoshaGaugeWidget(
              vata: (profile['vata_percent'] ?? 0).toDouble(),
              pitta: (profile['pitta_percent'] ?? 0).toDouble(),
              kapha: (profile['kapha_percent'] ?? 0).toDouble(),
            ),
            const SizedBox(height: 12),
            BlocBuilder<HeatmapCubit, HeatmapState>(
              builder: (BuildContext context, HeatmapState state) {
                if (state is HeatmapLoaded && state.districts.isNotEmpty) {
                  final List<Map<String, dynamic>> sorted = List<Map<String, dynamic>>.from(state.districts);
                  sorted.sort((Map<String, dynamic> a, Map<String, dynamic> b) {
                    final num scoreA = (a['risk_score'] ?? 0) as num;
                    final num scoreB = (b['risk_score'] ?? 0) as num;
                    return scoreB.compareTo(scoreA);
                  });
                  final Map<String, dynamic> top = sorted.first;
                  return AlertBannerWidget(
                    riskLevel: (top['risk_level'] ?? 'medium').toString(),
                    condition: (top['top_condition'] ?? 'Monitoring').toString(),
                    stateName: (top['state_name'] ?? 'India').toString(),
                    onTap: () => context.go('/heatmap'),
                  );
                }

                return AlertBannerWidget(
                  riskLevel: 'low',
                  condition: 'Monitoring 10 states across India',
                  stateName: 'India',
                  onTap: () => context.go('/heatmap'),
                );
              },
            ),
            const SizedBox(height: 16),
            Text(context.t('ritucharya_7_days'), style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            SizedBox(
              height: 88,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: ritucharya.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (BuildContext context, int index) {
                  final Map<String, String> item = ritucharya[index];
                  return Container(
                    width: 180,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      color: Colors.white,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(item['day'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        Text(
                          item['tip'] ?? '',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            Text(context.t('recent_sessions'), style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ...sessions.map((Map<String, dynamic> session) {
              final dynamic rawSymptoms = session['symptoms'];
              final List<dynamic> source = rawSymptoms is List
                  ? rawSymptoms
                  : List<dynamic>.from((rawSymptoms is Map ? (rawSymptoms['items'] ?? <dynamic>[]) : <dynamic>[]));
              final List<String> symptoms = source.map((dynamic e) => e.toString()).toList();

              return Card(
                child: ListTile(
                  title: Text(session['created_at']?.toString().split('T').first ?? context.t('recent')),
                  subtitle: Wrap(
                    spacing: 6,
                    children: symptoms
                        .take(4)
                        .map((String s) => Chip(label: Text(s), visualDensity: VisualDensity.compact))
                        .toList(),
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
              children: <Widget>[
                _ActionTile(title: context.t('get_recommendations'), icon: Icons.medical_services, onTap: () => context.go('/symptoms')),
                _ActionTile(title: context.t('disease_heatmap'), icon: Icons.map, onTap: () => context.go('/heatmap')),
                _ActionTile(title: context.t('forecast'), icon: Icons.query_stats, onTap: () => context.go('/forecast')),
                _ActionTile(title: context.t('nadi_monitor'), icon: Icons.favorite, onTap: () => context.go('/nadi')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  const _ActionTile({required this.title, required this.icon, required this.onTap});

  final String title;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Card(
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
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
