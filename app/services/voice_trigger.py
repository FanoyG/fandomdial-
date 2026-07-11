import random


class VoiceTriggerDecider:
    """
    SRP: this class's only job is deciding whether a given reply should
    auto-play as a voice note. Kept separate from ChatService so the
    probability/logic can be tuned or swapped without touching orchestration.

    Controlled randomness (not every reply) protects ElevenLabs' limited
    free-tier quota (~10 min/month) while still feeling alive and
    unpredictable to whoever is testing the app.
    """

    def __init__(self, probability: float = 0.2):
        if not 0 <= probability <= 1:
            raise ValueError("probability must be between 0 and 1")
        self.probability = probability

    def should_auto_play(self) -> bool:
        return random.random() < self.probability