from dataclasses import dataclass
import random

HEALTH_KEYWORDS = {
    'en': ['fever', 'cough', 'fatigue', 'body ache', 'throat pain', 'diarrhea', 'joint pain', 'allergy'],
    'ta': ['kaichchal', 'irumal', 'sorvu', 'udal vali', 'thondai vali', 'vayitru pokku', 'mootu vali', 'allergy'],
    'hi': ['bukhar', 'khansi', 'thakan', 'sharir dard', 'gale mein dard', 'dast', 'jodon ka dard', 'allergy'],
    'te': ['jvaram', 'daggu', 'alasata', 'deha noppi', 'gonthu noppi', 'dastulu', 'mokaala noppi', 'allergy'],
}


@dataclass
class SocialSignalSummary:
    state_code: str
    total_signals: int
    top_symptoms: list[str]
    summary: str


class NLPService:
    def get_signal_summary(self, state_code: str) -> SocialSignalSummary:
        random.seed(hash(state_code) % 1000)
        total = random.randint(20, 300)
        keywords = HEALTH_KEYWORDS['en'][:]
        random.shuffle(keywords)
        top = keywords[:3]
        summary = f'{total} social health signals observed in {state_code}; top symptoms: {top[0]}, {top[1]}, {top[2]}.'
        return SocialSignalSummary(state_code=state_code, total_signals=total, top_symptoms=top, summary=summary)

    def get_symptom_clusters(self, days: int = 7) -> list[dict]:
        random.seed(days * 17)
        base = [
            ('Mumbai', 'fever'),
            ('Delhi', 'cough'),
            ('Chennai', 'diarrhea'),
            ('Bengaluru', 'allergy'),
            ('Kolkata', 'fatigue'),
        ]
        clusters = []
        for district, symptom in base:
            count = random.randint(8, 42)
            if count >= 30:
                severity = 'high'
            elif count >= 18:
                severity = 'medium'
            else:
                severity = 'low'
            clusters.append({'district': district, 'symptom': symptom, 'count': count, 'severity': severity})
        return clusters
