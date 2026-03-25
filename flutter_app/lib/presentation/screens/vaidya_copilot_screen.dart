import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/i18n/language_map.dart';
import '../../data/repositories/vaidya_repository.dart';
import '../../services/hive_service.dart';

class VaidyaCopilotScreen extends StatefulWidget {
	const VaidyaCopilotScreen({super.key});

	@override
	State<VaidyaCopilotScreen> createState() => _VaidyaCopilotScreenState();
}

class _VaidyaCopilotScreenState extends State<VaidyaCopilotScreen> {
	final _searchController = TextEditingController();
	final _symptomsController = TextEditingController();
	final _repo = VaidyaRepository();

	List<Map<String, dynamic>> _patients = <Map<String, dynamic>>[];
	List<Map<String, dynamic>> _evidence = <Map<String, dynamic>>[];
	List<Map<String, dynamic>> _reports = <Map<String, dynamic>>[];

	Map<String, dynamic>? _selected;
	Map<String, dynamic>? _suggestion;
	bool _loading = false;
	bool _loadingPatients = false;
	bool _loadingReports = false;

	@override
	void initState() {
		super.initState();
		_loadPatients();
		_loadEvidence();
		_loadReports();
	}

	@override
	void dispose() {
		_searchController.dispose();
		_symptomsController.dispose();
		super.dispose();
	}

	Future<void> _loadPatients() async {
		setState(() => _loadingPatients = true);
		try {
			final List<Map<String, dynamic>> fetched = await _repo.patients(search: _searchController.text.trim());
			setState(() {
				_patients = fetched;
				if (_patients.isNotEmpty) {
					_selected = _patients.firstWhere(
						(Map<String, dynamic> p) => p['id'] == _selected?['id'],
						orElse: () => _patients.first,
					);
				}
			});
		} catch (e) {
			if (!mounted) {
				return;
			}
			ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to load patients: $e')));
		} finally {
			if (mounted) {
				setState(() => _loadingPatients = false);
			}
		}
	}

	Future<void> _loadEvidence() async {
		try {
			setState(() => _evidence = <Map<String, dynamic>>[]);
			final List<Map<String, dynamic>> evidence = await _repo.evidence();
			setState(() => _evidence = evidence);
		} catch (_) {}
	}

	Future<void> _loadReports() async {
		setState(() => _loadingReports = true);
		try {
			final List<Map<String, dynamic>> reports = await _repo.reports(limit: 10);
			setState(() => _reports = reports);
		} catch (_) {
			setState(() => _reports = <Map<String, dynamic>>[]);
		} finally {
			if (mounted) {
				setState(() => _loadingReports = false);
			}
		}
	}

	Future<void> _fetchSuggestion() async {
		setState(() => _loading = true);
		try {
			final List<String> symptoms = _symptomsController.text
					.split(',')
					.map((e) => e.trim())
					.where((e) => e.isNotEmpty)
					.toList();
			final String patientUid = (_selected?['id'] ?? '').toString();
			final Map<String, dynamic> suggestion = await _repo.suggest(
				symptoms: symptoms,
				dosha: (_selected?['prakriti_type'] ?? _selected?['prakriti'] ?? 'Vata').toString(),
				patientUid: patientUid,
			);
			setState(() => _suggestion = suggestion);

			if (patientUid.isNotEmpty) {
				await _repo.consult(patientUid: patientUid, symptoms: symptoms, suggestion: suggestion);
				await _loadReports();
			}
		} catch (e) {
			if (!mounted) return;
			ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to get suggestion: $e')));
		} finally {
			if (mounted) setState(() => _loading = false);
		}
	}

	@override
	Widget build(BuildContext context) {
		final dynamic rawUser = HiveService.getSetting('user_data');
		final Map<String, dynamic> user = rawUser is Map<String, dynamic> ? rawUser : <String, dynamic>{};
		final bool isDoctor = (user['role'] ?? '').toString().toLowerCase() == 'doctor';
		if (!isDoctor) {
			return Scaffold(
				appBar: AppBar(title: Text(context.t('vaidya_copilot'))),
				body: Center(
					child: Padding(
						padding: const EdgeInsets.all(20),
						child: Column(
							mainAxisSize: MainAxisSize.min,
							children: [
								const Icon(Icons.lock_outline, size: 44),
								const SizedBox(height: 12),
								Text(context.t('vaidya_copilot'), style: Theme.of(context).textTheme.titleLarge),
								const SizedBox(height: 8),
								const Text('Doctor access required for this module.'),
								const SizedBox(height: 12),
								ElevatedButton(
									onPressed: () => context.go('/home'),
									child: const Text('Back to Home'),
								),
							],
						),
					),
				),
			);
		}

		final ColorScheme colorScheme = Theme.of(context).colorScheme;
		final filtered = _patients
				.where((p) => (p['display_name'] ?? '').toString().toLowerCase().contains(_searchController.text.toLowerCase()))
				.toList();

		Widget leftPanel() {
			return Column(
				crossAxisAlignment: CrossAxisAlignment.start,
				children: [
					TextField(
						controller: _searchController,
						decoration: InputDecoration(labelText: context.t('search_patient'), prefixIcon: const Icon(Icons.search)),
						onChanged: (_) => _loadPatients(),
					),
					const SizedBox(height: 10),
					Expanded(
						child: _loadingPatients
								? const Center(child: CircularProgressIndicator())
								: ListView.builder(
										itemCount: filtered.length,
										itemBuilder: (context, index) {
											final patient = filtered[index];
											final bool selected = _selected?['id'] == patient['id'];
											return Card(
												color: selected ? colorScheme.primaryContainer.withValues(alpha: 0.35) : null,
												child: ListTile(
													selected: selected,
													title: Text((patient['display_name'] ?? context.t('unknown')).toString()),
													subtitle: Text((patient['prakriti_type'] ?? 'N/A').toString()),
													onTap: () => setState(() => _selected = patient),
												),
											);
										},
								),
					),
					if (_evidence.isNotEmpty) ...[
						const SizedBox(height: 8),
						Text(context.t('evidence_snapshot'), style: Theme.of(context).textTheme.titleSmall),
						const SizedBox(height: 6),
						SizedBox(
							height: 88,
							child: ListView.separated(
								scrollDirection: Axis.horizontal,
								itemCount: _evidence.length,
								separatorBuilder: (_, __) => const SizedBox(width: 8),
								itemBuilder: (context, idx) {
									final item = _evidence[idx];
									return Container(
										width: 180,
										padding: const EdgeInsets.all(10),
										decoration: BoxDecoration(
											borderRadius: BorderRadius.circular(12),
											color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
										),
										child: Column(
											crossAxisAlignment: CrossAxisAlignment.start,
											children: [
												Text((item['condition'] ?? '').toString(), style: Theme.of(context).textTheme.labelLarge),
												const SizedBox(height: 4),
												Text('${item['success_rate'] ?? '--'}% ${context.t('success')}'),
											],
										),
									);
								},
							),
						),
					],
				],
			);
		}

		Widget rightPanel() {
			final List<dynamic> rawFormulations = (_suggestion?['formulations'] as List<dynamic>? ?? <dynamic>[]);
			final List<String> formulations = rawFormulations.map((dynamic item) {
				if (item is Map) {
					return (item['name'] ?? item['formulation'] ?? item['herb'] ?? item.toString()).toString();
				}
				return item.toString();
			}).toList();
			return SingleChildScrollView(
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Card(
							child: ListTile(
								title: Text((_selected?['display_name'] ?? context.t('no_patient')).toString()),
								subtitle: Text('${context.t('prakriti')}: ${(_selected?['prakriti_type'] ?? 'N/A').toString()}'),
							),
						),
						const SizedBox(height: 10),
						TextField(
							controller: _symptomsController,
							maxLines: 3,
							decoration: InputDecoration(
								labelText: context.t('symptoms_comma'),
								hintText: context.t('symptoms_hint'),
							),
						),
						const SizedBox(height: 10),
						SizedBox(
							width: double.infinity,
							child: ElevatedButton(
								onPressed: _loading ? null : _fetchSuggestion,
								child: Text(_loading ? context.t('loading') : context.t('get_ai_suggestion')),
							),
						),
						if (_suggestion != null) ...[
							const SizedBox(height: 12),
							Container(
								width: double.infinity,
								padding: const EdgeInsets.all(12),
								decoration: BoxDecoration(
									borderRadius: BorderRadius.circular(12),
									color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.25),
								),
								child: Text((_suggestion?['rationale'] ?? '').toString()),
							),
						],
						const SizedBox(height: 12),
						...formulations.map(
							(f) => ExpansionTile(
								title: Text(f),
								children: [
									Padding(
										padding: const EdgeInsets.all(12),
										child: Text(_suggestion?['rationale']?.toString() ?? ''),
									),
								],
							),
						),
						const SizedBox(height: 12),
						Text('Recent Consult Reports', style: Theme.of(context).textTheme.titleSmall),
						const SizedBox(height: 6),
						if (_loadingReports)
							const Center(child: CircularProgressIndicator())
						else
							..._reports
								.take(5)
								.map(
									(Map<String, dynamic> report) => Card(
										child: ListTile(
											title: Text('Consult ${report['consult_id'] ?? ''}'),
											subtitle: Text((report['status'] ?? 'unknown').toString()),
										),
									),
								)
								.toList(),
					],
				),
			);
		}

		return Scaffold(
			appBar: AppBar(
				title: Text(context.t('vaidya_copilot')),
				actions: [
					IconButton(
						onPressed: () async {
							await _loadPatients();
							await _loadReports();
						},
						icon: const Icon(Icons.refresh),
					),
				],
			),
			body: LayoutBuilder(
				builder: (context, constraints) {
					if (constraints.maxWidth > 600) {
						return Padding(
							padding: const EdgeInsets.all(12),
							child: Row(
								children: [
									Expanded(child: leftPanel()),
									const SizedBox(width: 12),
									Expanded(child: rightPanel()),
								],
							),
						);
					}
					return Padding(
						padding: const EdgeInsets.all(12),
						child: Column(
							children: [
								Expanded(flex: 2, child: leftPanel()),
								const SizedBox(height: 8),
								Expanded(flex: 3, child: rightPanel()),
							],
						),
					);
				},
			),
		);
	}
}
