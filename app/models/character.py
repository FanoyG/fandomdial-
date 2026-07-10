from dataclasses import dataclass


@dataclass
class Character:
    """
    Pure data holder for a character's identity and behavior config.
    No behavior here on purpose (SRP) — this class does not know
    how to generate replies or synthesize voice. That's AIProvider
    and VoiceProvider's job.
    """
    id: str
    name: str
    system_prompt: str
    voice_id: str | None
    comedic_mechanism: str  # "contrast" | "deflection" | "escalation" | "roast"

    def __post_init__(self):
        if not self.system_prompt or not self.system_prompt.strip():
            raise ValueError(f"Character '{self.id}' has an empty system_prompt.")
        if not self.id or not self.name:
            raise ValueError("Character must have both an id and a name.")

    @property
    def has_voice(self) -> bool:
        """Voice call feature should check this before offering the call button."""
        return bool(self.voice_id)
