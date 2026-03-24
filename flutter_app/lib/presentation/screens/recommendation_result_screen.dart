import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:shimmer/shimmer.dart';

import '../cubits/recommendation_cubit.dart';

class RecommendationResultScreen extends StatefulWidget {
  const RecommendationResultScreen({super.key});

  @override
  State<RecommendationResultScreen> createState() => _RecommendationResultScreenState();
}

class _RecommendationResultScreenState extends State<RecommendationResultScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabController;

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

  void _downloadReport() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Arogya Report feature coming soon')),
    );
  }

  Color _timeColor(String time) {
    final String t = time.toLowerCase();
    if (t.contains('am') || t.contains('morning')) {
      return Colors.amber;
    }
    if (t.contains('afternoon') || t.contains('noon') || t.contains('pm') && t.startsWith('12')) {
      return Colors.blue;
    }
    if (t.contains('evening')) {
      return Colors.purple;
    }
    if (t.contains('night')) {
      return Colors.grey;
    }
    return Colors.grey;
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<RecommendationCubit, RecommendationState>(
      builder: (BuildContext context, RecommendationState state) {
        if (state is RecommendationInitial) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (mounted) {
              context.go('/symptoms');
            }
          });
          return const Scaffold(body: SizedBox.shrink());
        }

        if (state is RecommendationLoading) {
          return Scaffold(
            appBar: AppBar(title: const Text('Recommendations')),
            body: _ShimmerLoadingView(),
          );
        }

        if (state is RecommendationError) {
          return Scaffold(
            appBar: AppBar(title: const Text('Recommendations')),
            body: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  Text(state.msg, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => context.read<RecommendationCubit>().regenerate(),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          );
        }

        if (state is! RecommendationLoaded) {
          return const Scaffold(body: SizedBox.shrink());
        }

        final Map<String, dynamic> payload = state.data;
        final Map<String, dynamic> response = Map<String, dynamic>.from(payload['response_json'] as Map? ?? <String, dynamic>{});

        final List<Map<String, dynamic>> herbs = ((response['herbs'] as List<dynamic>? ?? <dynamic>[]))
            .map((dynamic item) => Map<String, dynamic>.from(item as Map))
            .toList();

        final Map<String, dynamic> diet = Map<String, dynamic>.from(response['diet'] as Map? ?? <String, dynamic>{});
        final List<dynamic> eatList = (diet['eat'] as List<dynamic>? ?? <dynamic>[]);
        final List<dynamic> avoidList = (diet['avoid'] as List<dynamic>? ?? <dynamic>[]);

        final List<Map<String, dynamic>> yoga = ((response['yoga'] as List<dynamic>? ?? <dynamic>[]))
            .map((dynamic item) => Map<String, dynamic>.from(item as Map))
            .toList();

        final List<Map<String, dynamic>> dinacharya = ((response['dinacharya'] as List<dynamic>? ?? <dynamic>[]))
            .map((dynamic item) => Map<String, dynamic>.from(item as Map))
            .toList();

        final String prevention =
            payload['prevention_30day']?.toString() ?? response['prevention_30day']?.toString() ?? 'No prevention plan available.';

        return Scaffold(
          appBar: AppBar(
            title: const Text('Recommendations'),
            actions: <Widget>[
              IconButton(
                onPressed: () => context.read<RecommendationCubit>().regenerate(),
                icon: const Icon(Icons.refresh),
              ),
            ],
            bottom: TabBar(
              controller: _tabController,
              tabs: const <Tab>[
                Tab(text: 'HERBS'),
                Tab(text: 'DIET'),
                Tab(text: 'YOGA'),
                Tab(text: 'DINACHARYA'),
              ],
            ),
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: _downloadReport,
            child: const Icon(Icons.download),
          ),
          body: Column(
            children: <Widget>[
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: <Widget>[
                    ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: herbs.length,
                      itemBuilder: (BuildContext context, int index) {
                        final Map<String, dynamic> herb = herbs[index];
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  herb['name']?.toString() ?? 'Herb',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                                const SizedBox(height: 6),
                                Text(herb['benefit']?.toString() ?? ''),
                                const SizedBox(height: 8),
                                Wrap(
                                  spacing: 8,
                                  children: <Widget>[
                                    Chip(label: Text(herb['dosage']?.toString() ?? 'Dosage N/A')),
                                    Chip(label: Text(herb['timing']?.toString() ?? 'Timing N/A')),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: <Widget>[
                          Expanded(
                            child: Card(
                              color: Colors.green.shade50,
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: <Widget>[
                                    const Text('Eat', style: TextStyle(fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 10),
                                    ...eatList.map((dynamic item) {
                                      final String text = item is Map
                                          ? '${item['food'] ?? ''}${item['reason'] != null ? ' - ${item['reason']}' : ''}'
                                          : item.toString();
                                      return Padding(
                                        padding: const EdgeInsets.only(bottom: 8),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: <Widget>[
                                            const Icon(Icons.check_circle, color: Colors.green, size: 18),
                                            const SizedBox(width: 6),
                                            Expanded(child: Text(text)),
                                          ],
                                        ),
                                      );
                                    }),
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
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: <Widget>[
                                    const Text('Avoid', style: TextStyle(fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 10),
                                    ...avoidList.map((dynamic item) {
                                      final String text = item is Map
                                          ? '${item['food'] ?? ''}${item['reason'] != null ? ' - ${item['reason']}' : ''}'
                                          : item.toString();
                                      return Padding(
                                        padding: const EdgeInsets.only(bottom: 8),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: <Widget>[
                                            const Icon(Icons.cancel, color: Colors.red, size: 18),
                                            const SizedBox(width: 6),
                                            Expanded(child: Text(text)),
                                          ],
                                        ),
                                      );
                                    }),
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
                          .map((Map<String, dynamic> y) => Card(
                                child: ListTile(
                                  title: Text(y['name']?.toString() ?? 'Yoga Practice'),
                                  subtitle: Text(y['benefit']?.toString() ?? ''),
                                  trailing: Chip(label: Text(y['duration']?.toString() ?? '10 min')),
                                ),
                              ))
                          .toList(),
                    ),
                    ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: dinacharya.length,
                      itemBuilder: (BuildContext context, int index) {
                        final Map<String, dynamic> entry = dinacharya[index];
                        final String time = entry['time']?.toString() ?? '--:--';
                        final Color color = _timeColor(time);
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                SizedBox(
                                  width: 90,
                                  child: Text(
                                    time,
                                    style: TextStyle(fontWeight: FontWeight.bold, color: color),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(entry['activity']?.toString() ?? ''),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
                child: ExpansionTile(
                  tilePadding: const EdgeInsets.symmetric(horizontal: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  backgroundColor: Colors.blue.shade50,
                  collapsedBackgroundColor: Colors.blue.shade50,
                  title: const Text('30-Day Prevention Plan', style: TextStyle(fontWeight: FontWeight.bold)),
                  children: <Widget>[
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(prevention),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ShimmerLoadingView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey.shade300,
      highlightColor: Colors.grey.shade100,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: 4,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => Container(
          height: 110,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
