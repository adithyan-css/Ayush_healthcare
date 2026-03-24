import random


class SocialSignalSummary:
    def __init__(self, state_code, total, top, summary):
        self.state_code = state_code
        self.total_signals = total
        self.top_symptoms = top
        self.summary = summary


class NLPService:
    def get_signal_summary(self, state_code: str) -> SocialSignalSummary:
        total = random.randint(20, 200)
        symptoms = ['fever', 'cough', 'fatigue', 'body ache']
        random.shuffle(symptoms)
        top = symptoms[:3]
        summary = f'{total} health signals detected, top: {top[0]}'
        return SocialSignalSummary(state_code, total, top, summary)
import random

class SocialSignalSummary:
    def __init__(self, state_code, total, top, summary):
        self.state_code = state_code
        self.total_signals = total
        self.top_symptoms = top
        self.summary = summary

class NLPService:
    def get_signal_summary(self, state_code: str):
        # Replace with real Twitter/X API v2 call using TWITTER_BEARER_TOKEN when available
        total = random.randint(20, 200)
        symptoms = ["fever", "cough", "fatigue", "body ache"]
        random.shuffle(symptoms)
        top = symptoms[:3]
        summary = f"{total} health signals detected, top: {top[0]}"
        return SocialSignalSummary(state_code, total, top, summary)
