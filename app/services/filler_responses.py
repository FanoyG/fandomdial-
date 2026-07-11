def get_filler(character_id: str) -> str:
    """
    Returns immediate local fallback text assets to mitigate cloud pipeline demand spikes.
    """
    fillers = {
        "gullu": "Nahi, theek hai. Thoda ruko... ek minute me baat karte hain.",
        "sohail": "Arre yaar, hold karo thoda! Itna fast message bhejoge toh browser hang ho jayega.",
        "zaid": "Arre chill karo bhai! Jugaad system over-heat ho raha hai, do second me reply deta hu."
    }
    return fillers.get(character_id, "Switchboard processing line busy. Hold for connection...")
