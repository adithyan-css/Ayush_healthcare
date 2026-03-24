class ForecastModel {
	final Map<String, List<double>> conditions;
	final List<Map<String, dynamic>> regionCards;
	final Map<String, int> populationRisks;

	ForecastModel({
		required this.conditions,
		required this.regionCards,
		required this.populationRisks,
	});

	factory ForecastModel.fromJson(Map<String, dynamic> json) {
		final rawConditions = Map<String, dynamic>.from(json['conditions'] ?? {});
		final convertedConditions = <String, List<double>>{};
		for (final entry in rawConditions.entries) {
			convertedConditions[entry.key] = (entry.value as List<dynamic>).map((e) => (e as num).toDouble()).toList();
		}

		final rawPopulation = Map<String, dynamic>.from(json['population_risks'] ?? json['populationRisks'] ?? {});
		final convertedPopulation = <String, int>{};
		for (final entry in rawPopulation.entries) {
			convertedPopulation[entry.key] = (entry.value as num).toInt();
		}

		return ForecastModel(
			conditions: convertedConditions,
			regionCards: List<Map<String, dynamic>>.from((json['region_cards'] ?? json['regionCards'] ?? []).map((e) => Map<String, dynamic>.from(e as Map))),
			populationRisks: convertedPopulation,
		);
	}

	Map<String, dynamic> toJson() {
		return {
			'conditions': conditions,
			'region_cards': regionCards,
			'population_risks': populationRisks,
		};
	}
}
