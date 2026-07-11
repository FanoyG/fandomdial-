"""
Run with: python -m app_test.test_voice_trigger
Statistical check — with randomness, we can't expect an exact 20%,
but over enough trials it should land close.
"""
from app.services.voice_trigger import VoiceTriggerDecider

print("================ VOICE TRIGGER PROBABILITY TEST ================")

trigger = VoiceTriggerDecider(probability=0.2)

trials = 2000
auto_play_count = sum(1 for _ in range(trials) if trigger.should_auto_play())
actual_rate = auto_play_count / trials

print(f"Trials: {trials}")
print(f"Auto-play triggered: {auto_play_count} times")
print(f"Actual rate: {actual_rate:.3f} (Expected: ~0.200, tolerance ±0.03)")

if abs(actual_rate - 0.2) <= 0.03:
    print("\n -> SUCCESS: Probability behaves correctly within tolerance.")
else:
    print("\n -> FAILURE: Rate is off — check the implementation.")

# Edge case checks
print("\n-- Edge case checks --")
try:
    VoiceTriggerDecider(probability=1.5)
    print("FAILURE: should have rejected probability > 1")
except ValueError:
    print("PASS: correctly rejected probability > 1")

try:
    VoiceTriggerDecider(probability=-0.1)
    print("FAILURE: should have rejected negative probability")
except ValueError:
    print("PASS: correctly rejected negative probability")

zero_trigger = VoiceTriggerDecider(probability=0.0)
never_true = any(zero_trigger.should_auto_play() for _ in range(500))
print("PASS: probability=0.0 never triggers" if not never_true else "FAILURE: 0.0 triggered")

always_trigger = VoiceTriggerDecider(probability=1.0)
always_true = all(always_trigger.should_auto_play() for _ in range(500))
print("PASS: probability=1.0 always triggers" if always_true else "FAILURE: 1.0 didn't always trigger")

print("=========================================================================")