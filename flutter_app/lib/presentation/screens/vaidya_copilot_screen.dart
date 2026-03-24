import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class VaidyaCopilotScreen extends StatefulWidget {
	const VaidyaCopilotScreen({super.key});

	@override
	State<VaidyaCopilotScreen> createState() => _VaidyaCopilotScreenState();
}

class _VaidyaCopilotScreenState extends State<VaidyaCopilotScreen> {
	final _searchController = TextEditingController();
	final _symptomsController = TextEditingController();
	final _api = ApiService.instance;

	final List<Map<String, String>> _patients = const [
		{'id': 'p1', 'name': 'Aarav Sharma', 'prakriti': 'Vata-Pitta'},
		{'id': 'p2', 'name': 'Meera Nair', 'prakriti': 'Pitta-Kapha'},
		{'id': 'p3', 'name': 'Rohan Iyer', 'prakriti': 'Kapha-Vata'},
	];

	Map<String, String>? _selected;
	Map<String, dynamic>? _suggestion;
	bool _loading = false;

	@override
	void initState() {
		super.initState();
		_selected = _patients.first;
	}

	@override
	void dispose() {
		_searchController.dispose();
		_symptomsController.dispose();
		super.dispose();
	}

	Future<void> _fetchSuggestion() async {
		setState(() => _loading = true);
		try {
			final symptoms = _symptomsController.text
					.split(',')
					.map((e) => e.trim())
					.where((e) => e.isNotEmpty)
					.toList();
			final response = await _api.post('/vaidya/suggest', {
				'symptoms': symptoms,
				'dosha': _selected?['prakriti'] ?? 'Vata',
			});
			setState(() => _suggestion = Map<String, dynamic>.from(response as Map));
		} catch (e) {
			if (!mounted) return;
			ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to get suggestion: $e')));
		} finally {
			if (mounted) setState(() => _loading = false);
		}
	}

	@override
	Widget build(BuildContext context) {
		final filtered = _patients
				.where((p) => p['name']!.toLowerCase().contains(_searchController.text.toLowerCase()))
				.toList();

		Widget leftPanel() {
			return Column(
				crossAxisAlignment: CrossAxisAlignment.start,
				children: [
					TextField(
						controller: _searchController,
						decoration: const InputDecoration(labelText: 'Search patient', prefixIcon: Icon(Icons.search)),
						onChanged: (_) => setState(() {}),
					),
					const SizedBox(height: 10),
					Expanded(
						child: ListView.builder(
							itemCount: filtered.length,
							itemBuilder: (context, index) {
								final patient = filtered[index];
								return Card(
									child: ListTile(
										selected: _selected?['id'] == patient['id'],
										title: Text(patient['name']!),
										subtitle: Text(patient['prakriti']!),
										onTap: () => setState(() => _selected = patient),
									),
								);
							},
						),
					),
				],
			);
		}

		Widget rightPanel() {
			final formulations = (_suggestion?['formulations'] as List<dynamic>? ?? []).map((e) => e.toString()).toList();
			return SingleChildScrollView(
				child: Column(
					crossAxisAlignment: CrossAxisAlignment.start,
					children: [
						Card(
							child: ListTile(
								title: Text(_selected?['name'] ?? 'No Patient'),
								subtitle: Text('Prakriti: ${_selected?['prakriti'] ?? 'N/A'}'),
							),
						),
						const SizedBox(height: 10),
						TextField(
							controller: _symptomsController,
							maxLines: 3,
							decoration: const InputDecoration(
								labelText: 'Symptoms (comma-separated)',
								hintText: 'fever, cough, acidity',
							),
						),
						const SizedBox(height: 10),
						SizedBox(
							width: double.infinity,
							child: ElevatedButton(
								onPressed: _loading ? null : _fetchSuggestion,
								child: Text(_loading ? 'Loading...' : 'Get AI Suggestion'),
							),
						),
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
					],
				),
			);
		}

		return Scaffold(
			appBar: AppBar(title: const Text('Vaidya Copilot — Doctor Dashboard')),
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
